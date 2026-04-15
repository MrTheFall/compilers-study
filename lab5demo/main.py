from interpreter.interpreter import Interpreter
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.semantic_analyzer import SemanticAnalyzer


TEST_CASES = [
    {
        "name": "math with variables",
        "source": (
            "var a = 10;\n"
            "var b = 4;\n"
            "var result = (a + b) * 2 - a / 2;\n"
            "print result;\n"
        ),
        "expected_output": ["23"],
    },
    {
        "name": "assignment recalculates value",
        "source": (
            "var x = 2;\n"
            "x = x * 5 + 1;\n"
            "print x;\n"
        ),
        "expected_output": ["11"],
    },
    {
        "name": "block scope and shadowing",
        "source": (
            "var x = 10;\n"
            "{\n"
            "    var x = 3;\n"
            "    print x + 1;\n"
            "}\n"
            "print x;\n"
        ),
        "expected_output": ["4", "10"],
    },
    {
        "name": "while accumulates sum",
        "source": (
            "var total = 0;\n"
            "var i = 1;\n"
            "while (i <= 5) {\n"
            "    total = total + i;\n"
            "    i = i + 1;\n"
            "}\n"
            "print total;\n"
        ),
        "expected_output": ["15"],
    },
    {
        "name": "conditions and strings",
        "source": (
            "var total = 15;\n"
            "if (total == 15) print \"ok\"; else print \"bad\";\n"
        ),
        "expected_output": ["ok"],
    },
]


def print_messages(title: str, messages: list[str]) -> None:
    print(f"{title}:")
    if not messages:
        print("  none")
        return

    for message in messages:
        print(f"  {message}")


def print_globals(interpreter: Interpreter) -> None:
    variables = interpreter.get_global_variables()
    print("Global variables:")
    if not variables:
        print("  none")
        return

    for name, value in variables.items():
        print(f"  {name} = {interpreter.stringify(value)}")


def run_case(index: int, case: dict[str, object]) -> bool:
    print("=" * 80)
    print(f"Case {index}: {case['name']}")
    print("Source:")
    print(case["source"], end="" if str(case["source"]).endswith("\n") else "\n")

    try:
        lexer = Lexer(str(case["source"]))
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        errors, warnings = SemanticAnalyzer().analyze(ast)

        print(f"Tokens: {len(tokens)}")
        print(f"AST: {len(ast)}")
        print_messages("Semantic errors", errors)
        print_messages("Semantic warnings", warnings)

        if errors:
            print("Result: FAIL")
            return False

        interpreter = Interpreter()
        output = interpreter.interpret(ast)
        print_messages("Program output", output)
        print_globals(interpreter)

        passed = output == case["expected_output"]
        print(f"Expected output: {case['expected_output']}")
        print(f"Result: {'PASS' if passed else 'FAIL'}")
        return passed
    except Exception as error:
        print("Runtime error:")
        print(f"  {error}")
        print("Result: FAIL")
        return False


def main() -> None:
    passed_cases: list[str] = []
    failed_cases: list[str] = []

    for index, case in enumerate(TEST_CASES, start=1):
        if run_case(index, case):
            passed_cases.append(str(case["name"]))
        else:
            failed_cases.append(str(case["name"]))

    print("=" * 80)
    print("Final stats:")
    print(f"  Total: {len(TEST_CASES)}")
    print(f"  Passed: {len(passed_cases)}")
    print(f"  Failed: {len(failed_cases)}")

    print("Failed cases:")
    if not failed_cases:
        print("  none")
    else:
        for case_name in failed_cases:
            print(f"  {case_name}")


if __name__ == "__main__":
    main()
