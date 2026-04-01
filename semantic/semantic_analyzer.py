from __future__ import annotations

from enum import Enum, auto

from lexer.token import TokenType
from parser.ast import (
    AssignExpression,
    BinaryExpression,
    BlockStatement,
    BooleanExpression,
    Expression,
    ExpressionStatement,
    IfStatement,
    NumberExpression,
    PrintStatement,
    Statement,
    StringExpression,
    UnaryExpression,
    VarStatement,
    VariableExpression,
    WhileStatement,
)


class DataType(Enum):
    UNKNOWN = auto()
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()

    def __str__(self) -> str:
        return self.name.lower()


class VariableInfo:
    def __init__(
        self,
        is_defined: bool = True,
        is_initialized: bool = False,
        is_used: bool = False,
        data_type: DataType = DataType.UNKNOWN,
    ):
        self.is_defined = is_defined
        self.is_initialized = is_initialized
        self.is_used = is_used
        self.data_type = data_type

    def clone(self) -> "VariableInfo":
        return VariableInfo(
            is_defined=self.is_defined,
            is_initialized=self.is_initialized,
            is_used=self.is_used,
            data_type=self.data_type,
        )

class SemanticAnalyzer:
    def __init__(self):
        self.scopes: list[dict[str, VariableInfo]] = []
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def analyze(self, statements: list[Statement]) -> tuple[list[str], list[str]]:
        self.scopes.clear()
        self.errors.clear()
        self.warnings.clear()
        self.begin_scope()
        for statement in statements:
            self.analyze_statement(statement)
        self.end_scope()
        return self.errors, self.warnings

    def analyze_statement(self, statement: Statement) -> None:
        if isinstance(statement, ExpressionStatement):
            self.analyze_expression(statement.expression)
            return

        if isinstance(statement, PrintStatement):
            self.analyze_expression(statement.expression)
            return

        if isinstance(statement, VarStatement):
            info = self.declare_variable(statement.name)
            if statement.initializer is not None:
                expression_type = self.analyze_expression(statement.initializer)
                if info is not None and expression_type != DataType.UNKNOWN:
                    info.data_type = expression_type
                    info.is_initialized = True
            return

        if isinstance(statement, BlockStatement):
            self.begin_scope()
            for nested_statement in statement.statements:
                self.analyze_statement(nested_statement)
            self.end_scope()
            return

        if isinstance(statement, IfStatement):
            condition_type = self.analyze_expression(statement.condition)
            self.require_boolean_condition("if", condition_type)
            self.analyze_isolated_statement(statement.then_branch)
            if statement.else_branch is not None:
                self.analyze_isolated_statement(statement.else_branch)
            return

        if isinstance(statement, WhileStatement):
            condition_type = self.analyze_expression(statement.condition)
            self.require_boolean_condition("while", condition_type)
            self.analyze_isolated_statement(statement.body)
            return

    def analyze_expression(self, expression: Expression | None) -> DataType:
        if expression is None:
            return DataType.UNKNOWN

        if isinstance(expression, NumberExpression):
            return DataType.NUMBER

        if isinstance(expression, StringExpression):
            return DataType.STRING

        if isinstance(expression, BooleanExpression):
            return DataType.BOOLEAN

        if isinstance(expression, VariableExpression):
            info = self.resolve_variable(expression.name)
            if info is None:
                self.errors.append(f"semantic error: {expression.name} is not declared")
                return DataType.UNKNOWN

            info.is_used = True
            if not info.is_initialized:
                self.errors.append(f"semantic error: {expression.name} is not initialized")
                return DataType.UNKNOWN

            return info.data_type

        if isinstance(expression, BinaryExpression):
            left_type = self.analyze_expression(expression.left)
            right_type = self.analyze_expression(expression.right)
            return self.get_binary_result_type(expression.operator, left_type, right_type)

        if isinstance(expression, UnaryExpression):
            right_type = self.analyze_expression(expression.right)
            return self.get_unary_result_type(expression.operator, right_type)

        if isinstance(expression, AssignExpression):
            value_type = self.analyze_expression(expression.value)
            info = self.resolve_variable(expression.name)

            if info is None:
                self.errors.append(f"semantic error: {expression.name} is not declared")
                return DataType.UNKNOWN

            if value_type == DataType.UNKNOWN:
                return info.data_type

            if info.data_type == DataType.UNKNOWN:
                info.data_type = value_type
                info.is_initialized = True
                return value_type

            if info.data_type != value_type:
                self.errors.append(
                    "semantic error: cannot assign "
                    f"{value_type} to {expression.name} of type {info.data_type}"
                )
                return info.data_type

            info.is_initialized = True
            return info.data_type

        self.errors.append(f"semantic error: unsupported expression {type(expression).__name__}")
        return DataType.UNKNOWN

    def begin_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        current_scope = self.scopes.pop()
        for name, info in current_scope.items():
            if not info.is_used:
                self.warnings.append(f"warning: {name} is declared but never used")

    def declare_variable(self, name: str) -> VariableInfo | None:
        current_scope = self.scopes[-1]
        if name in current_scope:
            self.errors.append(f"semantic error: {name} is already declared in this scope")
            return None
        current_scope[name] = VariableInfo(True, False, False)
        return current_scope[name]

    def resolve_variable(self, name: str) -> VariableInfo | None:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def require_boolean_condition(self, statement_name: str, condition_type: DataType) -> None:
        if condition_type == DataType.UNKNOWN:
            return
        if condition_type != DataType.BOOLEAN:
            self.errors.append(
                f"semantic error: {statement_name} condition must be boolean, got {condition_type}"
            )

    def analyze_isolated_statement(self, statement: Statement) -> None:
        original_scopes = self.scopes
        branch_scopes = self.clone_scopes(original_scopes)

        self.scopes = branch_scopes
        try:
            self.analyze_statement(statement)
        finally:
            analyzed_scopes = self.scopes
            self.scopes = original_scopes

        self.merge_used_flags(original_scopes, analyzed_scopes)

    def clone_scopes(self, scopes: list[dict[str, VariableInfo]]) -> list[dict[str, VariableInfo]]:
        return [
            {name: info.clone() for name, info in scope.items()}
            for scope in scopes
        ]

    def merge_used_flags(
        self,
        target_scopes: list[dict[str, VariableInfo]],
        source_scopes: list[dict[str, VariableInfo]],
    ) -> None:
        for index, source_scope in enumerate(source_scopes):
            if index >= len(target_scopes):
                break

            target_scope = target_scopes[index]
            for name, source_info in source_scope.items():
                if name in target_scope:
                    target_scope[name].is_used = (
                        target_scope[name].is_used or source_info.is_used
                    )

    def get_binary_result_type(
        self,
        operator: TokenType,
        left_type: DataType,
        right_type: DataType,
    ) -> DataType:
        if left_type == DataType.UNKNOWN or right_type == DataType.UNKNOWN:
            return DataType.UNKNOWN

        if operator in {TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH}:
            if operator == TokenType.PLUS and left_type == right_type == DataType.STRING:
                return DataType.STRING
            if left_type == right_type == DataType.NUMBER:
                return DataType.NUMBER
            return self.report_invalid_binary_operator(operator, left_type, right_type)

        if operator in {TokenType.LT, TokenType.LTEQ, TokenType.GT, TokenType.GTEQ}:
            if left_type == right_type == DataType.NUMBER:
                return DataType.BOOLEAN
            return self.report_invalid_binary_operator(operator, left_type, right_type)

        if operator in {TokenType.EQEQ, TokenType.NEQ}:
            if left_type == right_type and left_type != DataType.UNKNOWN:
                return DataType.BOOLEAN
            return self.report_invalid_binary_operator(operator, left_type, right_type)

        if operator in {TokenType.AND, TokenType.OR}:
            if left_type == right_type == DataType.BOOLEAN:
                return DataType.BOOLEAN
            return self.report_invalid_binary_operator(operator, left_type, right_type)

        self.errors.append(f"semantic error: unsupported operator {self.operator_to_text(operator)}")
        return DataType.UNKNOWN

    def get_unary_result_type(self, operator: TokenType, right_type: DataType) -> DataType:
        if right_type == DataType.UNKNOWN:
            return DataType.UNKNOWN

        if operator == TokenType.MINUS:
            if right_type == DataType.NUMBER:
                return DataType.NUMBER
            return self.report_invalid_unary_operator(operator, right_type)

        if operator == TokenType.EXCL:
            if right_type == DataType.BOOLEAN:
                return DataType.BOOLEAN
            return self.report_invalid_unary_operator(operator, right_type)

        self.errors.append(f"semantic error: unsupported operator {self.operator_to_text(operator)}")
        return DataType.UNKNOWN

    def report_invalid_binary_operator(
        self,
        operator: TokenType,
        left_type: DataType,
        right_type: DataType,
    ) -> DataType:
        self.errors.append(
            "semantic error: operator "
            f"{self.operator_to_text(operator)} is not supported for {left_type} and {right_type}"
        )
        return DataType.UNKNOWN

    def report_invalid_unary_operator(self, operator: TokenType, operand_type: DataType) -> DataType:
        self.errors.append(
            "semantic error: operator "
            f"{self.operator_to_text(operator)} is not supported for {operand_type}"
        )
        return DataType.UNKNOWN

    def operator_to_text(self, operator: TokenType) -> str:
        operators = {
            TokenType.PLUS: "+",
            TokenType.MINUS: "-",
            TokenType.STAR: "*",
            TokenType.SLASH: "/",
            TokenType.EQEQ: "==",
            TokenType.NEQ: "!=",
            TokenType.LT: "<",
            TokenType.LTEQ: "<=",
            TokenType.GT: ">",
            TokenType.GTEQ: ">=",
            TokenType.AND: "&&",
            TokenType.OR: "||",
            TokenType.EXCL: "!",
        }
        return operators.get(operator, operator.name)
