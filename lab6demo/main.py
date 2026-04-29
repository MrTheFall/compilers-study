from interpreter.interpreter import Interpreter
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.semantic_analyzer import SemanticAnalyzer


TEST_CASES = [
    {
        "name": "function call returns value",
        "source": (
            "fun add(x, y) {\n"
            "    return x + y;\n"
            "}\n"
            "var result = add(5, 10);\n"
            "print result;\n"
        ),
        "expected_output": ["15"],
        "expected_errors": [],
    },
    {
        "name": "function parameters are local",
        "source": (
            "var x = 100;\n"
            "fun add_to_x(x, delta) {\n"
            "    return x + delta;\n"
            "}\n"
            "print add_to_x(5, 7);\n"
            "print x;\n"
        ),
        "expected_output": ["12", "100"],
        "expected_errors": [],
    },
    {
        "name": "recursive function",
        "source": (
            "fun fact(n) {\n"
            "    if (n <= 1) return 1;\n"
            "    return n * fact(n - 1);\n"
            "}\n"
            "print fact(5);\n"
        ),
        "expected_output": ["120"],
        "expected_errors": [],
    },
    {
        "name": "wrong argument count",
        "source": (
            "fun add(x, y) {\n"
            "    return x + y;\n"
            "}\n"
            "print add(1);\n"
        ),
        "expected_output": [],
        "expected_errors": ["function add expects 2 arguments, got 1"],
    },
    {
        "name": "unknown function",
        "source": "print missing(1, 2);\n",
        "expected_output": [],
        "expected_errors": ["function missing is not declared"],
    },
    {
        "name": "return outside function",
        "source": "return 1;\n",
        "expected_output": [],
        "expected_errors": ["return is allowed only inside a function"],
    },
    {
        "name": "duplicate parameter",
        "source": (
            "fun bad(x, x) {\n"
            "    return x;\n"
            "}\n"
            "print bad(1, 2);\n"
        ),
        "expected_output": [],
        "expected_errors": ["parameter x is already declared in function bad"],
    },
]


def print_messages(title: str, messages: list[str]) -> None:
    print(f"{title}:")
    if not messages:
        print("  none")
        return

    for message in messages:
        print(f"  {message}")


def has_expected_fragments(messages: list[str], expected_fragments: list[str]) -> bool:
    if not expected_fragments:
        return not messages

    combined_messages = " ".join(messages)
    return all(fragment in combined_messages for fragment in expected_fragments)


def run_case(index: int, case: dict[str, object]) -> bool:
    print("=" * 80)
    print(f"Case {index}: {case['name']}")
    print("Source:")
    print(case["source"], end="" if str(case["source"]).endswith("\n") else "\n")

    try:
        tokens = Lexer(str(case["source"])).tokenize()
        ast = Parser(tokens).parse()
        errors, warnings = SemanticAnalyzer().analyze(ast)

        print(f"Tokens: {len(tokens)}")
        print(f"AST: {len(ast)}")
        print_messages("Semantic errors", errors)
        print_messages("Semantic warnings", warnings)

        expected_errors = case["expected_errors"]
        errors_match = has_expected_fragments(errors, expected_errors)
        if errors:
            passed = errors_match
            print_messages("Program output", [])
            print(f"Expected output: {case['expected_output']}")
            print(f"Result: {'PASS' if passed else 'FAIL'}")
            return passed

        interpreter = Interpreter()
        output = interpreter.interpret(ast)
        print_messages("Program output", output)

        passed = errors_match and output == case["expected_output"]
        print(f"Expected output: {case['expected_output']}")
        print(f"Result: {'PASS' if passed else 'FAIL'}")
        return passed
    except Exception as error:
        error_text = str(error)
        passed = has_expected_fragments([error_text], case["expected_errors"])

        print("Runtime error:")
        print(f"  {error_text}")
        print(f"Result: {'PASS' if passed else 'FAIL'}")
        return passed


def main() -> None:
    passed_cases: list[str] = []
    failed_cases: list[str] = []

    print("Lab 6 demo: functions, calls, return, parameters and recursion")

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
