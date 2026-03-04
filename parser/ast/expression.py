from lexer.token import TokenType

class Expression:
    pass

class NumberExpression(Expression):
    def __init__(self, value: float):
        self.value = value

class StringExpression(Expression):
    def __init__(self, value: str):
        self.value = f"{value}"

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
