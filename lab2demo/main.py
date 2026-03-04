from lexer.lexer import Lexer
from parser.parser import Parser
from .ast_printer import AstPrinter
from code_generator.code_generator import CodeGenerator

#source = "var x = 10; if (x > 5) print x + 1; else x = 0;"
source = CodeGenerator().generate(10)

print(f"Source:\n{source}")

lexer = Lexer(source)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()
printer = AstPrinter()

print(f"Tokens: {len(tokens)}")
print(f"AST: {len(ast)}")

printer.print(ast)

with open("lab2demo/source.txt", "w") as f:
    f.write(source)

printer.print_ast_to_file(ast, "lab2demo/ast.txt")
