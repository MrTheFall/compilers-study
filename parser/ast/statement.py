from .expression import Expression

class Statement:
    pass

class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

class PrintStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

class VarStatement(Statement):
    def __init__(self, name: str, initializer: Expression):
        self.name = name
        self.initializer = initializer

class BlockStatement(Statement):
    def __init__(self, statements: list[Statement]):
        self.statements = statements

class IfStatement(Statement):
    def __init__(self, condition: Expression, then_branch: Statement, else_branch: Statement = None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: Statement):
        self.condition = condition
        self.body = body