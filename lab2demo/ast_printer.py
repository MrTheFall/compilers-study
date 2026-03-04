from parser.ast import (
    Statement, VarStatement, PrintStatement, IfStatement, 
    WhileStatement, BlockStatement, ExpressionStatement,
    BinaryExpression, UnaryExpression, AssignExpression, 
    NumberExpression, VariableExpression
)

class AstPrinter:
    def __init__(self):
        pass

    def print(self, statements: list[Statement]) -> None:
        for statement in statements:
            self.print_node(statement, "", True)

    def print_node(self, node: object, indent: str, is_last: bool) -> None:
        if node is None:
            return

        marker = "└── " if is_last else "├── "
        child_indent = indent + ("    " if is_last else "│   ")

        if isinstance(node, VarStatement):
            print(f"{indent}{marker}VarStatement: {node.name}")
            if node.initializer is not None:
                self.print_node(node.initializer, child_indent, True)
        elif isinstance(node, PrintStatement):
            print(f"{indent}{marker}PrintStatement")
            self.print_node(node.expression, child_indent, True)
        elif isinstance(node, IfStatement):
            print(f"{indent}{marker}IfStatement")
            self.print_node(node.condition, child_indent, False)
            self.print_node(node.then_branch, child_indent, node.else_branch is None)
            if node.else_branch is not None:
                self.print_node(node.else_branch, child_indent, True)
        elif isinstance(node, WhileStatement):
            print(f"{indent}{marker}WhileStatement")
            self.print_node(node.condition, child_indent, False)
            self.print_node(node.body, child_indent, True)
        elif isinstance(node, BlockStatement):
            print(f"{indent}{marker}BlockStatement")
            for i, statement in enumerate(node.statements):
                self.print_node(statement, child_indent, i == len(node.statements) - 1)
        elif isinstance(node, ExpressionStatement):
            print(f"{indent}{marker}ExpressionStatement")
            self.print_node(node.expression, child_indent, True)
        elif isinstance(node, BinaryExpression):
            print(f"{indent}{marker}BinaryExpression: {node.operator}")
            self.print_node(node.left, child_indent, False)
            self.print_node(node.right, child_indent, True)
        elif isinstance(node, UnaryExpression):
            print(f"{indent}{marker}UnaryExpression: {node.operator}")
            self.print_node(node.right, child_indent, True)
        elif isinstance(node, AssignExpression):
            print(f"{indent}{marker}AssignExpression: {node.name} =")
            self.print_node(node.value, child_indent, True)
        elif isinstance(node, NumberExpression):
            print(f"{indent}{marker}Number: {node.value}")
        elif isinstance(node, VariableExpression):
            print(f"{indent}{marker}Variable: {node.name}")
        else:
            print(f"{indent}{marker}Unknown Node: {type(node).__name__}")

    def print_ast_to_file(self, statements: list[Statement], filename: str) -> None:
        with open(filename, "w") as f:
            for statement in statements:
                self._print_node_to_file(statement, f, "", True)

    def _print_node_to_file(self, node: object, file: str, indent: str, is_last: bool) -> None:
        if node is None:
            return

        marker = "└── " if is_last else "├── "
        child_indent = indent + ("    " if is_last else "│   ")

        if isinstance(node, VarStatement):
            file.write(f"{indent}{marker}VarStatement: {node.name}\n")
            if node.initializer is not None:
                self._print_node_to_file(node.initializer, file, child_indent, True)
        elif isinstance(node, PrintStatement):
            file.write(f"{indent}{marker}PrintStatement\n")
            self._print_node_to_file(node.expression, file, child_indent, True)
        elif isinstance(node, IfStatement):
            file.write(f"{indent}{marker}IfStatement\n")
            self._print_node_to_file(node.condition, file, child_indent, False)
            self._print_node_to_file(node.then_branch, file, child_indent, node.else_branch is None)
            if node.else_branch is not None:
                self._print_node_to_file(node.else_branch, file, child_indent, True)
        elif isinstance(node, WhileStatement):
            file.write(f"{indent}{marker}WhileStatement\n")
            self._print_node_to_file(node.condition, file, child_indent, False)
            self._print_node_to_file(node.body, file, child_indent, True)
        elif isinstance(node, BlockStatement):
            file.write(f"{indent}{marker}BlockStatement\n")
            for i, statement in enumerate(node.statements):
                self._print_node_to_file(statement, file, child_indent, i == len(node.statements) - 1)
        elif isinstance(node, ExpressionStatement):
            file.write(f"{indent}{marker}ExpressionStatement\n")
            self._print_node_to_file(node.expression, file, child_indent, True)
        elif isinstance(node, BinaryExpression):
            file.write(f"{indent}{marker}BinaryExpression: {node.operator}\n")
            self._print_node_to_file(node.left, file, child_indent, False)
            self._print_node_to_file(node.right, file, child_indent, True)
        elif isinstance(node, UnaryExpression):
            file.write(f"{indent}{marker}UnaryExpression: {node.operator}\n")
            self._print_node_to_file(node.right, file, child_indent, True)
        elif isinstance(node, AssignExpression):
            file.write(f"{indent}{marker}AssignExpression: {node.name} =\n")
            self._print_node_to_file(node.value, file, child_indent, True)
        elif isinstance(node, NumberExpression):
            file.write(f"{indent}{marker}Number: {node.value}\n")
        elif isinstance(node, VariableExpression):
            file.write(f"{indent}{marker}Variable: {node.name}\n")
        else:
            file.write(f"{indent}{marker}Unknown Node: {type(node).__name__}\n")