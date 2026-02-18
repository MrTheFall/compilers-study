from lexer import Lexer

def main() -> None:
    source: str = "var x = 123; print x + 5;"
    lexer: Lexer = Lexer(source)
    tokens = lexer.tokenize()
    for token in tokens:
        print(token)
    

main()
