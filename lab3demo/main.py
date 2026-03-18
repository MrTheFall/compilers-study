from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.semantic_analyzer import SemanticAnalyzer


TEST_CASES = [
    {
        "name": "initialized variable",
        "source": "var x = 1;\nprint x;\n",
        "expected": "ok: no errors, no warnings",
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "parent scope is visible",
        "source": "var x = 1;\n{\n    print x;\n}\n",
        "expected": "ok: inner block can read x from parent scope",
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "inner scope is hidden outside",
        "source": "{\n    var y = 2;\n}\nprint y;\n",
        "expected": "semantic error: y is not declared outside the block",
        "expected_errors": ["y", "declared"],
        "expected_warnings": ["y", "never used"],
    },
    {
        "name": "read before initialization",
        "source": "var x;\nprint x;\n",
        "expected": "semantic error: x is declared but not initialized",
        "expected_errors": ["x", "initialized"],
        "expected_warnings": [],
    },
    {
        "name": "assignment initializes variable",
        "source": "var x;\nx = 5;\nprint x;\n",
        "expected": "ok: assignment marks x as initialized",
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "unused variable",
        "source": "var x = 1;\n",
        "expected": "warning: x is declared but never used",
        "expected_errors": [],
        "expected_warnings": ["x", "never used"],
    },
    {
        "name": "assign to undeclared variable",
        "source": "x = 5;\n",
        "expected": "semantic error: x is not declared",
        "expected_errors": ["x", "declared"],
        "expected_warnings": [],
    },
    {
        "name": "duplicate declaration in same scope",
        "source": "var x = 1;\nvar x = 2;\nprint x;\n",
        "expected": "semantic error: x is already declared in this scope",
        "expected_errors": ["x", "already declared"],
        "expected_warnings": [],
    },
    {
        "name": "shadowing in inner scope",
        "source": "var x = 1;\n{\n    var x = 2;\n    print x;\n}\nprint x;\n",
        "expected": "ok: inner scope may shadow outer variable",
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "if without block uses outer scope",
        "source": "var x = 1;\nif (x == 1) print x;\n",
        "expected": "ok: single statement if can read outer variable",
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "if with block uses outer scope",
        "source": "var x = 1;\nif (x == 1) {\n    var y = x;\n    print y;\n}\nprint x;\n",
        "expected": "ok: block inside if can read outer variable and use local one",
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "if with block hides local variable outside",
        "source": "var x = 1;\nif (x == 1) {\n    var y = x;\n}\nprint y;\n",
        "expected": "semantic error: y is not declared outside if block",
        "expected_errors": ["y", "declared"],
        "expected_warnings": ["y", "never used"],
    },
    {
        "name": "while without block updates outer variable",
        "source": "var x = 1;\nwhile (x < 3) x = x + 1;\nprint x;\n",
        "expected": "ok: single statement while can read and assign outer variable",
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "self initialization is not allowed",
        "source": "var x = x;\n",
        "expected": "semantic error: x is not initialized in its own initializer",
        "expected_errors": ["x", "initialized"],
        "expected_warnings": [],
    },
    {
        "name": "use before later declaration",
        "source": "var x = y;\nvar y = 1;\n",
        "expected": "semantic error: y is not declared when x initializer is analyzed",
        "expected_errors": ["y", "declared"],
        "expected_warnings": ["x", "y", "never used"],
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


def print_case_result(errors: list[str], warnings: list[str], case: dict[str, object]) -> None:
    errors_ok = has_expected_fragments(errors, case["expected_errors"])
    warnings_ok = has_expected_fragments(warnings, case["expected_warnings"])

    print("Result:")
    print(f"  {'PASS' if errors_ok and warnings_ok else 'FAIL'}")


def case_passed(errors: list[str], warnings: list[str], case: dict[str, object]) -> bool:
    errors_ok = has_expected_fragments(errors, case["expected_errors"])
    warnings_ok = has_expected_fragments(warnings, case["expected_warnings"])
    return errors_ok and warnings_ok


def print_final_stats(passed_cases: list[str], failed_cases: list[str]) -> None:
    total_cases = len(passed_cases) + len(failed_cases)

    print("=" * 80)
    print("Final stats:")
    print(f"  Total: {total_cases}")
    print(f"  Passed: {len(passed_cases)}")
    print(f"  Failed: {len(failed_cases)}")

    print("Passed cases:")
    if not passed_cases:
        print("  none")
    else:
        for case_name in passed_cases:
            print(f"  {case_name}")

    print("Failed cases:")
    if not failed_cases:
        print("  none")
    else:
        for case_name in failed_cases:
            print(f"  {case_name}")


def run_case(index: int, case: dict[str, object]) -> bool:
    print("=" * 80)
    print(f"Case {index}: {case['name']}")
    print("Expected:")
    print(case["expected"])
    print("Source:")
    print(case["source"], end="" if case["source"].endswith("\n") else "\n")

    try:
        lexer = Lexer(case["source"])
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        errors, warnings = SemanticAnalyzer().analyze(ast)
        passed = case_passed(errors, warnings, case)

        print(f"Tokens: {len(tokens)}")
        print(f"AST: {len(ast)}")
        print_messages("Errors", errors)
        print_messages("Warnings", warnings)
        print_case_result(errors, warnings, case)
        return passed
    except Exception as error:
        print("Runtime error:")
        print(f"  {error}")
        print("Result:")
        print("  FAIL")
        return False


def main() -> None:
    passed_cases: list[str] = []
    failed_cases: list[str] = []

    for index, case in enumerate(TEST_CASES, start=1):
        if run_case(index, case):
            passed_cases.append(case["name"])
        else:
            failed_cases.append(case["name"])

    print_final_stats(passed_cases, failed_cases)


if __name__ == "__main__":
    main()
