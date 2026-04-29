from lexer.token import TokenType

class Expression:
    pass

class NumberExpression(Expression):
    def __init__(self, value: int):
        self.value = value

class StringExpression(Expression):
    def __init__(self, value: str):
        self.value = value

class BooleanExpression(Expression):
    def __init__(self, value: bool):
        self.value = value

class VariableExpression(Expression):
    def __init__(self, name: str):
        self.name = name

class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: TokenType, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryExpression(Expression):
    def __init__(self, operator: TokenType, right: Expression):
        self.operator = operator
        self.right = right

class AssignExpression(Expression):
    def __init__(self, name: str, value: Expression):
        self.name = name
        self.value = value

class CallExpression(Expression):
    def __init__(self, callee_name: str, arguments: list[Expression]):
        self.callee_name = callee_name
        self.arguments = arguments
