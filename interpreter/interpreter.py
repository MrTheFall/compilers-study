from __future__ import annotations

from lexer.token import TokenType
from parser.ast import (
    AssignExpression,
    BinaryExpression,
    BlockStatement,
    BooleanExpression,
    CallExpression,
    Expression,
    ExpressionStatement,
    FunctionStatement,
    IfStatement,
    NumberExpression,
    PrintStatement,
    ReturnStatement,
    Statement,
    StringExpression,
    UnaryExpression,
    VarStatement,
    VariableExpression,
    WhileStatement,
)


RuntimeValue = int | float | str | bool | None


class InterpreterRuntimeError(Exception):
    pass


class ReturnSignal(Exception):
    def __init__(self, value: RuntimeValue):
        self.value = value


_UNINITIALIZED = object()


class Interpreter:
    def __init__(self, max_loop_iterations: int = 10000):
        self.max_loop_iterations = max_loop_iterations
        self.scopes: list[dict[str, RuntimeValue | object]] = []
        self.function_scopes: list[dict[str, FunctionStatement]] = []
        self.output: list[str] = []

    def interpret(self, statements: list[Statement]) -> list[str]:
        self.scopes = [{}]
        self.function_scopes = [{}]
        self.output = []

        try:
            for statement in statements:
                self.execute_statement(statement)
        except ReturnSignal as error:
            raise InterpreterRuntimeError(
                "[Interpreter Error] return is allowed only inside a function"
            ) from error

        return self.output.copy()

    def get_global_variables(self) -> dict[str, RuntimeValue]:
        if not self.scopes:
            return {}

        return {
            name: value
            for name, value in self.scopes[0].items()
            if value is not _UNINITIALIZED
        }

    def execute_statement(self, statement: Statement) -> None:
        if isinstance(statement, ExpressionStatement):
            self.evaluate_expression(statement.expression)
            return

        if isinstance(statement, PrintStatement):
            value = self.evaluate_expression(statement.expression)
            self.output.append(self.stringify(value))
            return

        if isinstance(statement, VarStatement):
            value: RuntimeValue | object = _UNINITIALIZED
            if statement.initializer is not None:
                value = self.evaluate_expression(statement.initializer)
            self.declare_variable(statement.name, value)
            return

        if isinstance(statement, FunctionStatement):
            self.declare_function(statement.name, statement)
            return

        if isinstance(statement, ReturnStatement):
            value = None
            if statement.value is not None:
                value = self.evaluate_expression(statement.value)
            raise ReturnSignal(value)

        if isinstance(statement, BlockStatement):
            self.execute_block(statement.statements)
            return

        if isinstance(statement, IfStatement):
            condition = self.require_boolean(
                self.evaluate_expression(statement.condition),
                "if condition",
            )
            if condition:
                self.execute_statement(statement.then_branch)
            elif statement.else_branch is not None:
                self.execute_statement(statement.else_branch)
            return

        if isinstance(statement, WhileStatement):
            iterations = 0
            while self.require_boolean(
                self.evaluate_expression(statement.condition),
                "while condition",
            ):
                if iterations >= self.max_loop_iterations:
                    raise InterpreterRuntimeError(
                        "[Interpreter Error] while loop exceeded "
                        f"{self.max_loop_iterations} iterations"
                    )
                self.execute_statement(statement.body)
                iterations += 1
            return

        raise InterpreterRuntimeError(
            f"[Interpreter Error] Unsupported statement {type(statement).__name__}"
        )

    def execute_block(self, statements: list[Statement]) -> None:
        self.begin_scope()
        try:
            for statement in statements:
                self.execute_statement(statement)
        finally:
            self.end_scope()

    def evaluate_expression(self, expression: Expression) -> RuntimeValue:
        if isinstance(expression, NumberExpression):
            return expression.value

        if isinstance(expression, StringExpression):
            return expression.value

        if isinstance(expression, BooleanExpression):
            return expression.value

        if isinstance(expression, VariableExpression):
            return self.get_variable(expression.name)

        if isinstance(expression, AssignExpression):
            value = self.evaluate_expression(expression.value)
            self.assign_variable(expression.name, value)
            return value

        if isinstance(expression, CallExpression):
            return self.evaluate_call(expression)

        if isinstance(expression, UnaryExpression):
            return self.evaluate_unary(expression)

        if isinstance(expression, BinaryExpression):
            return self.evaluate_binary(expression)

        raise InterpreterRuntimeError(
            f"[Interpreter Error] Unsupported expression {type(expression).__name__}"
        )

    def evaluate_call(self, expression: CallExpression) -> RuntimeValue:
        function = self.get_function(expression.callee_name)
        if len(expression.arguments) != len(function.parameters):
            raise InterpreterRuntimeError(
                "[Interpreter Error] Function "
                f"{expression.callee_name} expects {len(function.parameters)} arguments, "
                f"got {len(expression.arguments)}"
            )

        arguments = [
            self.evaluate_expression(argument)
            for argument in expression.arguments
        ]

        self.begin_scope()
        try:
            for parameter, argument in zip(function.parameters, arguments, strict=True):
                self.declare_variable(parameter, argument)

            try:
                for statement in function.body.statements:
                    self.execute_statement(statement)
            except ReturnSignal as signal:
                return signal.value
        finally:
            self.end_scope()

        return None

    def evaluate_unary(self, expression: UnaryExpression) -> RuntimeValue:
        value = self.evaluate_expression(expression.right)

        if expression.operator == TokenType.MINUS:
            self.require_number(value, expression.operator)
            return -value

        if expression.operator == TokenType.EXCL:
            return not self.require_boolean(value, "operator !")

        raise InterpreterRuntimeError(
            "[Interpreter Error] Unsupported unary operator "
            f"{self.operator_to_text(expression.operator)}"
        )

    def evaluate_binary(self, expression: BinaryExpression) -> RuntimeValue:
        if expression.operator == TokenType.OR:
            left = self.require_boolean(
                self.evaluate_expression(expression.left),
                "operator ||",
            )
            if left:
                return True
            return self.require_boolean(
                self.evaluate_expression(expression.right),
                "operator ||",
            )

        if expression.operator == TokenType.AND:
            left = self.require_boolean(
                self.evaluate_expression(expression.left),
                "operator &&",
            )
            if not left:
                return False
            return self.require_boolean(
                self.evaluate_expression(expression.right),
                "operator &&",
            )

        left = self.evaluate_expression(expression.left)
        right = self.evaluate_expression(expression.right)
        operator = expression.operator

        if operator == TokenType.PLUS:
            if self.is_number(left) and self.is_number(right):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            self.raise_invalid_binary_operator(operator, left, right)

        if operator == TokenType.MINUS:
            self.require_numbers(left, right, operator)
            return left - right

        if operator == TokenType.STAR:
            self.require_numbers(left, right, operator)
            return left * right

        if operator == TokenType.SLASH:
            self.require_numbers(left, right, operator)
            if right == 0:
                raise InterpreterRuntimeError("[Interpreter Error] Division by zero")
            return left / right

        if operator in {TokenType.LT, TokenType.LTEQ, TokenType.GT, TokenType.GTEQ}:
            self.require_numbers(left, right, operator)
            if operator == TokenType.LT:
                return left < right
            if operator == TokenType.LTEQ:
                return left <= right
            if operator == TokenType.GT:
                return left > right
            return left >= right

        if operator in {TokenType.EQEQ, TokenType.NEQ}:
            if self.value_type(left) != self.value_type(right):
                self.raise_invalid_binary_operator(operator, left, right)
            if operator == TokenType.EQEQ:
                return left == right
            return left != right

        raise InterpreterRuntimeError(
            "[Interpreter Error] Unsupported binary operator "
            f"{self.operator_to_text(operator)}"
        )

    def begin_scope(self) -> None:
        self.scopes.append({})
        self.function_scopes.append({})

    def end_scope(self) -> None:
        self.scopes.pop()
        self.function_scopes.pop()

    def declare_variable(self, name: str, value: RuntimeValue | object) -> None:
        current_scope = self.scopes[-1]
        if name in current_scope or name in self.function_scopes[-1]:
            raise InterpreterRuntimeError(
                f"[Interpreter Error] Variable {name} is already declared in this scope"
            )
        current_scope[name] = value

    def declare_function(self, name: str, function: FunctionStatement) -> None:
        current_scope = self.function_scopes[-1]
        if name in current_scope or name in self.scopes[-1]:
            raise InterpreterRuntimeError(
                f"[Interpreter Error] Function {name} is already declared in this scope"
            )
        current_scope[name] = function

    def get_function(self, name: str) -> FunctionStatement:
        for index in range(len(self.function_scopes) - 1, -1, -1):
            if name in self.scopes[index]:
                break
            if name in self.function_scopes[index]:
                return self.function_scopes[index][name]

        raise InterpreterRuntimeError(
            f"[Interpreter Error] Function {name} is not declared"
        )

    def assign_variable(self, name: str, value: RuntimeValue) -> None:
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return

        raise InterpreterRuntimeError(
            f"[Interpreter Error] Variable {name} is not declared"
        )

    def get_variable(self, name: str) -> RuntimeValue:
        for scope in reversed(self.scopes):
            if name in scope:
                value = scope[name]
                if value is _UNINITIALIZED:
                    raise InterpreterRuntimeError(
                        f"[Interpreter Error] Variable {name} is not initialized"
                    )
                return value

        raise InterpreterRuntimeError(
            f"[Interpreter Error] Variable {name} is not declared"
        )

    def require_numbers(
        self,
        left: RuntimeValue,
        right: RuntimeValue,
        operator: TokenType,
    ) -> None:
        if self.is_number(left) and self.is_number(right):
            return
        self.raise_invalid_binary_operator(operator, left, right)

    def require_number(self, value: RuntimeValue, operator: TokenType) -> None:
        if self.is_number(value):
            return
        raise InterpreterRuntimeError(
            "[Interpreter Error] Operator "
            f"{self.operator_to_text(operator)} is not supported for {self.value_type(value)}"
        )

    def require_boolean(self, value: RuntimeValue, context: str) -> bool:
        if isinstance(value, bool):
            return value
        raise InterpreterRuntimeError(
            f"[Interpreter Error] {context} expects boolean, got {self.value_type(value)}"
        )

    def raise_invalid_binary_operator(
        self,
        operator: TokenType,
        left: RuntimeValue,
        right: RuntimeValue,
    ) -> None:
        raise InterpreterRuntimeError(
            "[Interpreter Error] Operator "
            f"{self.operator_to_text(operator)} is not supported for "
            f"{self.value_type(left)} and {self.value_type(right)}"
        )

    def is_number(self, value: RuntimeValue) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    def value_type(self, value: RuntimeValue) -> str:
        if isinstance(value, bool):
            return "boolean"
        if self.is_number(value):
            return "number"
        if isinstance(value, str):
            return "string"
        return type(value).__name__

    def stringify(self, value: RuntimeValue) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

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
