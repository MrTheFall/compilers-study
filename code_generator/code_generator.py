import random


class CodeGenerator:
    def __init__(self):
        self._random = random.Random()
        self._var_names = ["x", "y", "z", "alpha", "beta", "count", "total", "index", "sum"]
        self._declared_vars: list[str] = []
        self._math_ops = ["+", "-", "*", "/"]
        self._compare_ops = ["==", "!=", "<", ">", "<=", ">="]
        self._logic_ops = ["&&", "||"]

    def generate(self, statement_count: int = 10) -> str:
        """Генерирует случайную программу."""
        self._declared_vars.clear()
        lines: list[str] = []

        # Обязательно объявляем хотя бы пару переменных в самом начале
        for _ in range(3):
            lines.append(self._generate_var_declaration(0))

        self._generate_block(lines, statement_count, 0)

        return "\n".join(lines) + "\n"

    def _generate_block(self, lines: list[str], count: int, indent_level: int) -> None:
        indent = " " * (indent_level * 4)

        for _ in range(count):
            # 0: Объявление переменной
            # 1: Присваивание
            # 2: Print
            # 3: If-Else
            # 4: While
            statement_type = self._random.randint(0, 4)

            # Ограничиваем вложенность
            if indent_level > 2 and statement_type > 2:
                statement_type = self._random.randint(0, 2)

            if statement_type == 0:
                lines.append(self._generate_var_declaration(indent_level))

            elif statement_type == 1:
                if self._declared_vars:
                    lines.append(f"{indent}{self._get_random_var()} = {self._generate_expression()};")
                else:
                    lines.append(self._generate_var_declaration(indent_level))

            elif statement_type == 2:
                lines.append(f"{indent}print {self._generate_expression()};")

            elif statement_type == 3:
                lines.append(f"{indent}if ({self._generate_condition()}) {{")
                self._generate_block(lines, self._random.randint(1, 3), indent_level + 1)

                if self._random.random() > 0.5:
                    lines.append(f"{indent}}} else {{")
                    self._generate_block(lines, self._random.randint(1, 2), indent_level + 1)

                lines.append(f"{indent}}}")

            elif statement_type == 4:
                lines.append(f"{indent}while ({self._generate_condition()}) {{")
                self._generate_block(lines, self._random.randint(1, 3), indent_level + 1)
                lines.append(f"{indent}}}")

    def _generate_var_declaration(self, indent_level: int) -> str:
        indent = " " * (indent_level * 4)
        var_name = self._random.choice(self._var_names)

        if var_name not in self._declared_vars:
            self._declared_vars.append(var_name)

        return f"{indent}var {var_name} = {self._generate_expression()};"

    def _generate_expression(self) -> str:
        if self._random.random() > 0.6 or not self._declared_vars:
            return str(self._random.randint(1, 99))

        if self._random.random() > 0.5:
            return self._get_random_var()

        left = self._get_random_var() if self._random.random() > 0.5 else str(self._random.randint(1, 99))
        right = self._get_random_var() if self._random.random() > 0.5 else str(self._random.randint(1, 99))
        op = self._random.choice(self._math_ops)

        return f"{left} {op} {right}"

    def _generate_condition(self) -> str:
        left = self._get_random_var_or_number()
        right = self._get_random_var_or_number()
        comp_op = self._random.choice(self._compare_ops)

        condition = f"{left} {comp_op} {right}"

        if self._random.random() > 0.7:
            logic_op = self._random.choice(self._logic_ops)
            extra_left = self._get_random_var_or_number()
            extra_right = self._get_random_var_or_number()
            extra_comp = self._random.choice(self._compare_ops)

            condition = f"({condition}) {logic_op} ({extra_left} {extra_comp} {extra_right})"

        return condition

    def _get_random_var(self) -> str:
        if not self._declared_vars:
            return "1"
        return self._random.choice(self._declared_vars)

    def _get_random_var_or_number(self) -> str:
        if self._declared_vars and self._random.random() > 0.5:
            return self._get_random_var()
        return str(self._random.randint(1, 99))