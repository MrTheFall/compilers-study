"""
var x = 2;
print x + 5;
ops: + - * /

keywords: var print if else while
"""
from token import TokenType, Token 

class Lexer:
    def __init__(self, source: str):
        self.input: str = source
        self.length: int = len(source)
        self.position: int = 0
    
    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while self.position < self.length:
            token: Token | None = self.get_next_token()
            if token:
                tokens.append(token)
        return tokens
    
    def peek(self) -> str:
        if self.position >= self.length:
            return '\x00'
        return self.input[self.position]

    def peek_next(self) -> str:
        if self.position + 1 >= self.length:
            return '\x00'
        return self.input[self.position + 1]

    def next(self) -> str:
        if self.position < self.length:
            self.position += 1
        return self.peek()

    def get_next_token(self) -> Token | None:
        current_char: str = self.peek()
        if current_char.isspace():
            self.next()
            return None
        elif current_char.isdigit():
            return self.tokenize_number()
        elif current_char.isalpha() or current_char == '_':
            return self.tokenize_word()
        else:
            return self.tokenize_operator()

    def tokenize_number(self) -> Token:
        start_pos: int = self.position
        while self.peek().isdigit():
            self.next()
        return Token(TokenType.NUMBER, self.input[start_pos:self.position], start_pos)

    def tokenize_word(self) -> Token:
        start_pos: int = self.position
        while self.peek().isalnum() or self.peek() == '_':
            self.next()
        
        word: str = self.input[start_pos:self.position]
        match word:
            case 'var':
                return Token(TokenType.VAR, word, start_pos)
            case 'print':
                return Token(TokenType.PRINT, word, start_pos)
            case 'if':
                return Token(TokenType.IF, word, start_pos)
            case 'else':
                return Token(TokenType.ELSE, word, start_pos)
            case 'while':
                return Token(TokenType.WHILE, word, start_pos)
            case _:
                return Token(TokenType.ID, word, start_pos)

    def tokenize_operator(self) -> Token:
        start_pos: int = self.position
        current_char: str = self.peek()
        next_char: str = self.peek_next()

        match current_char:
            case '+':
                self.next()
                return Token(TokenType.PLUS, '+', start_pos)
            case '-':
                self.next()
                return Token(TokenType.MINUS, '-', start_pos)
            case '*':
                self.next()
                return Token(TokenType.STAR, '*', start_pos)
            case '/':
                self.next()
                return Token(TokenType.SLASH, '/', start_pos)
            case '=':
                if next_char == '=':
                    self.next()
                    self.next()
                    return Token(TokenType.EQEQ, '==', start_pos)
                self.next()
                return Token(TokenType.EQ, '=', start_pos)
            case '!':
                if next_char == '=':
                    self.next()
                    self.next()
                    return Token(TokenType.NEQ, '!=', start_pos)
                self.next()
                return Token(TokenType.EXCL, '!', start_pos)
            case '<':
                if next_char == '=':
                    self.next()
                    self.next()
                    return Token(TokenType.LTEQ, '<=', start_pos)
                self.next()
                return Token(TokenType.LT, '<', start_pos)
            case '>':
                if next_char == '=':
                    self.next()
                    self.next()
                    return Token(TokenType.GTEQ, '>=', start_pos)
                self.next()
                return Token(TokenType.GT, '>', start_pos)
            case '&':
                if next_char == '&':
                    self.next()
                    self.next()
                    return Token(TokenType.AND, '&&', start_pos)
                raise Exception(f"Unknown character: {current_char}")
            case '|':
                if next_char == '|':
                    self.next()
                    self.next()
                    return Token(TokenType.OR, '||', start_pos)
                raise Exception(f"Unknown character: {current_char}")
            case ';':
                self.next()
                return Token(TokenType.SEMICOLON, ';', start_pos)
            case _:
                raise Exception(f"Unknown character: {current_char}")
