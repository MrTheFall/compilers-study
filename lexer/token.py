from enum import Enum, auto

class TokenType(Enum):
    # Keywords
    ID = auto()
    STRING = auto()
    NUMBER = auto()
    TRUE = auto()
    FALSE = auto()
    VAR = auto()
    
    PRINT = auto()

    IF = auto()
    ELSE = auto()
    WHILE = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQ = auto()
    EQEQ = auto()
    EXCL = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTEQ = auto()
    GTEQ = auto()
    AND = auto()
    OR = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()

    # Special
    EOF = auto()

class Token:
    def __init__(
        self,
        type: TokenType,
        value: str,
        position: int,
        line: int = 1,
        column: int = 1,
    ):
        self.type: TokenType = type
        self.value: str = value
        self.position: int = position
        self.line: int = line
        self.column: int = column

    def __repr__(self) -> str:
        return (
            "Token("
            f"type={self.type}, value={self.value!r}, position={self.position}, "
            f"line={self.line}, column={self.column})"
        )


    
