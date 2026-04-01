from lexer.token import Token, TokenType
from parser.ast.expression import Expression, NumberExpression, StringExpression, BooleanExpression, VariableExpression, BinaryExpression, UnaryExpression, AssignExpression
from parser.ast.statement import Statement, ExpressionStatement, PrintStatement, VarStatement, BlockStatement, IfStatement, WhileStatement

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    def parse(self) -> list[Statement]:
        statements = []
        while not self.is_at_end():
            statements.append(self.parse_declaration())
        return statements

    def parse_declaration(self) -> Statement:
        if self.match(TokenType.VAR):
            return self.parse_var_declaration()
        return self.parse_statement()

    def parse_statement(self) -> Statement:
        if self.match(TokenType.IF):
            return self.parse_if_statement()
        if self.match(TokenType.WHILE):
            return self.parse_while_statement()
        if self.match(TokenType.PRINT):
            return self.parse_print_statement()
        if self.match(TokenType.LBRACE):
            return BlockStatement(self.parse_block())
        return self.parse_expression_statement()

    def parse_var_declaration(self) -> Statement:
        name = self.consume(TokenType.ID, "Ожидается имя переменной.")
        initializer = None
        if self.match(TokenType.EQ):
            initializer = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Ожидается ';' после объявления переменной.")
        return VarStatement(name.value, initializer)

    def parse_if_statement(self) -> Statement:
        self.consume(TokenType.LPAREN, "Ожидается '(' после 'if'.")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Ожидается ')' после условия 'if'.")
        then_branch = self.parse_statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.parse_statement()
        return IfStatement(condition, then_branch, else_branch)

    def parse_while_statement(self) -> Statement:
        self.consume(TokenType.LPAREN, "Ожидается '(' после 'while'.")
        condition = self.parse_expression()
        self.consume(TokenType.RPAREN, "Ожидается ')' после условия 'while'.")
        body = self.parse_statement()
        return WhileStatement(condition, body)

    def parse_print_statement(self) -> Statement:
        value = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Ожидается ';' после значения.")
        return PrintStatement(value)

    def parse_expression_statement(self) -> Statement:
        expr = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Ожидается ';' после выражения.")
        return ExpressionStatement(expr)

    def parse_block(self) -> list[Statement]:
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.parse_declaration())
        self.consume(TokenType.RBRACE, "Ожидается '}' после блока.")
        return statements

    def parse_expression(self) -> Expression:
        return self.parse_assignment()

    def parse_assignment(self) -> Expression:
        expr = self.parse_logical_or()
        if self.match(TokenType.EQ):
            equals = self.previous()
            value = self.parse_assignment()
            if isinstance(expr, VariableExpression):
                return AssignExpression(expr.name, value)
            raise Exception(f"[Parser Error] Line {equals.line}, Col {equals.column}: Недопустимая цель для присваивания.")
        return expr

    def parse_logical_or(self) -> Expression:
        expr = self.parse_logical_and()
        while self.match(TokenType.OR):
            op = self.previous().type
            right = self.parse_logical_and()
            expr = BinaryExpression(expr, op, right)
        return expr

    def parse_logical_and(self) -> Expression:
        expr = self.parse_equality()
        while self.match(TokenType.AND):
            op = self.previous().type
            right = self.parse_equality()
            expr = BinaryExpression(expr, op, right)
        return expr

    def parse_equality(self) -> Expression:
        expr = self.parse_comparison()
        while self.match(TokenType.EQEQ, TokenType.NEQ):
            op = self.previous().type
            right = self.parse_comparison()
            expr = BinaryExpression(expr, op, right)
        return expr

    def parse_comparison(self) -> Expression:
        expr = self.parse_term()
        while self.match(TokenType.LT, TokenType.LTEQ, TokenType.GT, TokenType.GTEQ):
            op = self.previous().type
            right = self.parse_term()
            expr = BinaryExpression(expr, op, right)
        return expr

    def parse_term(self) -> Expression:
        expr = self.parse_factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.previous().type
            right = self.parse_factor()
            expr = BinaryExpression(expr, op, right)
        return expr

    def parse_factor(self) -> Expression:
        expr = self.parse_unary()
        while self.match(TokenType.STAR, TokenType.SLASH):
            op = self.previous().type
            right = self.parse_unary()
            expr = BinaryExpression(expr, op, right)
        return expr

    def parse_unary(self) -> Expression:
        if self.match(TokenType.EXCL, TokenType.MINUS):
            op = self.previous().type
            right = self.parse_unary()
            return UnaryExpression(op, right)
        return self.parse_primary()

    def parse_primary(self) -> Expression:
        if self.match(TokenType.NUMBER):
            value = int(self.previous().value)
            return NumberExpression(value)
        if self.match(TokenType.STRING):
            return StringExpression(self.previous().value)
        if self.match(TokenType.TRUE):
            return BooleanExpression(True)
        if self.match(TokenType.FALSE):
            return BooleanExpression(False)
        if self.match(TokenType.ID):
            return VariableExpression(self.previous().value)
        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Ожидается ')' после выражения.")
            return expr
        raise Exception(f"[Parser Error] Line {self.peek().line}, Col {self.peek().column}: Ожидается выражение.")

    def match(self, *types: TokenType) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def check(self, t: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == t

    def advance(self) -> Token:
        if not self.is_at_end():
            self.position += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.position]

    def previous(self) -> Token:
        return self.tokens[self.position - 1]

    def consume(self, t: TokenType, message: str) -> Token:
        if self.check(t):
            return self.advance()
        token = self.peek()
        raise Exception(f"[Parser Error] Line {token.line}, Col {token.column}: {message}")
