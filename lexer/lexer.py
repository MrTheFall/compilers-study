"""
var x = 2;
print x + 5;
ops: + - * /

keywords: var print if else while true false
"""
from lexer.token import TokenType, Token 

class Lexer:
    def __init__(self, source: str):
        self.input: str = source
        self.length: int = len(source)
        self.position: int = 0
        self.line: int = 1
        self.column: int = 1
    
    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while self.position < self.length:
            token: Token | None = self.get_next_token()
            if token:
                tokens.append(token)
        tokens.append(Token(TokenType.EOF, "", self.position, self.line, self.column))
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
        current_char = self.peek()
        if self.position < self.length:
            self.position += 1
            if current_char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        return self.peek()

    def get_next_token(self) -> Token | None:
        current_char: str = self.peek()
        if current_char.isspace():
            self.next()
            return None
        elif current_char.isdigit():
            return self.tokenize_number()
        elif current_char == '"':
            return self.tokenize_string()
        elif current_char.isalpha() or current_char == '_':
            return self.tokenize_word()
        else:
            return self.tokenize_operator()

    def tokenize_number(self) -> Token:
        start_pos: int = self.position
        start_line: int = self.line
        start_column: int = self.column
        while self.peek().isdigit():
            self.next()
        if self.peek() == '.' and self.peek_next().isdigit():
            raise Exception(
                f"[Lexer Error] Line {self.line}, Col {self.column}: "
                "Float literals are not supported."
            )
        return Token(
            TokenType.NUMBER,
            self.input[start_pos:self.position],
            start_pos,
            start_line,
            start_column,
        )

    def tokenize_string(self) -> Token:
        start_pos: int = self.position
        start_line: int = self.line
        start_column: int = self.column
        self.next()

        chars: list[str] = []
        while self.peek() not in {'"', '\x00'}:
            if self.peek() == '\n':
                raise Exception(
                    f"[Lexer Error] Line {start_line}, Col {start_column}: "
                    "Unterminated string literal."
                )
            chars.append(self.peek())
            self.next()

        if self.peek() != '"':
            raise Exception(
                f"[Lexer Error] Line {start_line}, Col {start_column}: "
                "Unterminated string literal."
            )

        self.next()
        return Token(
            TokenType.STRING,
            "".join(chars),
            start_pos,
            start_line,
            start_column,
        )

    def tokenize_word(self) -> Token:
        start_pos: int = self.position
        start_line: int = self.line
        start_column: int = self.column
        while self.peek().isalnum() or self.peek() == '_':
            self.next()
        
        word: str = self.input[start_pos:self.position]
        match word:
            case 'var':
                return Token(TokenType.VAR, word, start_pos, start_line, start_column)
            case 'print':
                return Token(TokenType.PRINT, word, start_pos, start_line, start_column)
            case 'if':
                return Token(TokenType.IF, word, start_pos, start_line, start_column)
            case 'else':
                return Token(TokenType.ELSE, word, start_pos, start_line, start_column)
            case 'while':
                return Token(TokenType.WHILE, word, start_pos, start_line, start_column)
            case 'true':
                return Token(TokenType.TRUE, word, start_pos, start_line, start_column)
            case 'false':
                return Token(TokenType.FALSE, word, start_pos, start_line, start_column)
            case _:
                return Token(TokenType.ID, word, start_pos, start_line, start_column)

    def tokenize_operator(self) -> Token:
        start_pos: int = self.position
        start_line: int = self.line
        start_column: int = self.column
        current_char: str = self.peek()
        next_char: str = self.peek_next()

        match current_char:
            case '+':
                self.next()
                return Token(TokenType.PLUS, '+', start_pos, start_line, start_column)
            case '-':
                self.next()
                return Token(TokenType.MINUS, '-', start_pos, start_line, start_column)
            case '*':
                self.next()
                return Token(TokenType.STAR, '*', start_pos, start_line, start_column)
            case '/':
                self.next()
                return Token(TokenType.SLASH, '/', start_pos, start_line, start_column)
            case '=':
                if next_char == '=':
                    self.next()
                    self.next()
                    return Token(TokenType.EQEQ, '==', start_pos, start_line, start_column)
                self.next()
                return Token(TokenType.EQ, '=', start_pos, start_line, start_column)
            case '!':
                if next_char == '=':
                    self.next()
                    self.next()
                    return Token(TokenType.NEQ, '!=', start_pos, start_line, start_column)
                self.next()
                return Token(TokenType.EXCL, '!', start_pos, start_line, start_column)
            case '<':
                if next_char == '=':
                    self.next()
                    self.next()
                    return Token(TokenType.LTEQ, '<=', start_pos, start_line, start_column)
                self.next()
                return Token(TokenType.LT, '<', start_pos, start_line, start_column)
            case '>':
                if next_char == '=':
                    self.next()
                    self.next()
                    return Token(TokenType.GTEQ, '>=', start_pos, start_line, start_column)
                self.next()
                return Token(TokenType.GT, '>', start_pos, start_line, start_column)
            case '&':
                if next_char == '&':
                    self.next()
                    self.next()
                    return Token(TokenType.AND, '&&', start_pos, start_line, start_column)
                raise Exception(
                    f"[Lexer Error] Line {start_line}, Col {start_column}: "
                    f"Unknown character: {current_char}"
                )
            case '|':
                if next_char == '|':
                    self.next()
                    self.next()
                    return Token(TokenType.OR, '||', start_pos, start_line, start_column)
                raise Exception(
                    f"[Lexer Error] Line {start_line}, Col {start_column}: "
                    f"Unknown character: {current_char}"
                )
            case ';':
                self.next()
                return Token(TokenType.SEMICOLON, ';', start_pos, start_line, start_column)
            case '(':
                self.next()
                return Token(TokenType.LPAREN, '(', start_pos, start_line, start_column)
            case ')':
                self.next()
                return Token(TokenType.RPAREN, ')', start_pos, start_line, start_column)
            case '{':
                self.next()
                return Token(TokenType.LBRACE, '{', start_pos, start_line, start_column)
            case '}':
                self.next()
                return Token(TokenType.RBRACE, '}', start_pos, start_line, start_column)
            case _:
                raise Exception(
                    f"[Lexer Error] Line {start_line}, Col {start_column}: "
                    f"Unknown character: {current_char}"
                )
