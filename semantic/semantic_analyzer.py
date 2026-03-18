from parser.ast import *


class VariableInfo:
    def __init__(self, is_defined: bool, is_initialized: bool, is_used: bool):
        self.is_defined = is_defined
        self.is_initialized = is_initialized
        self.is_used = is_used

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

    def analyze_statement(self, statement: Statement):
        if isinstance(statement, ExpressionStatement):
            self.analyze_expression(statement.expression)
        elif isinstance(statement, PrintStatement):
            self.analyze_expression(statement.expression)
        elif isinstance(statement, VarStatement):
            is_declared = self.declare_variable(statement.name)
            if statement.initializer is not None:
                self.analyze_expression(statement.initializer)
                if is_declared:
                    self.set_variable_initialized(statement.name)
        elif isinstance(statement, BlockStatement):
            self.begin_scope()
            for nested_statement in statement.statements:
                self.analyze_statement(nested_statement)
            self.end_scope()
        elif isinstance(statement, IfStatement):
            self.analyze_expression(statement.condition)
            self.analyze_statement(statement.then_branch)
            if statement.else_branch is not None:
                self.analyze_statement(statement.else_branch)
        elif isinstance(statement, WhileStatement):
            self.analyze_expression(statement.condition)
            self.analyze_statement(statement.body)

    def analyze_expression(self, expression: Expression):
        if expression is None:
            return
        if isinstance(expression, (NumberExpression, StringExpression)):
            return
        if isinstance(expression, VariableExpression):
            if self.resolve_variable(expression.name) is None:
                self.errors.append(f"Error: variable '{expression.name}' is not declared")
            elif not self.resolve_variable(expression.name).is_initialized:
                self.errors.append(f"Error: variable '{expression.name}' is not initialized")
            self.set_variable_used(expression.name)
            return
        if isinstance(expression, BinaryExpression):
            self.analyze_expression(expression.left)
            self.analyze_expression(expression.right)
            return
        if isinstance(expression, UnaryExpression):
            self.analyze_expression(expression.right)
            return
        if isinstance(expression, AssignExpression):
            self.analyze_expression(expression.value)
            if self.resolve_variable(expression.name) is None:
                self.errors.append(f"Error: variable '{expression.name}' is not declared")
            else:
                self.set_variable_initialized(expression.name)
            return

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self) -> None:
        current_scope = self.scopes.pop()
        for name, info in current_scope.items():
            if not info.is_used:
                self.warnings.append(f"Warning: variable '{name}' is declared but never used")

    def declare_variable(self, name: str):
        current_scope = self.scopes[-1]
        if name in current_scope:
            self.errors.append(f"Error: variable '{name}' is already declared")
            return False
        current_scope[name] = VariableInfo(True, False, False)
        return True

    def resolve_variable(self, name: str) -> VariableInfo | None:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def set_variable_initialized(self, name: str):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name].is_initialized = True
                return

    def set_variable_used(self, name: str):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name].is_used = True
                return