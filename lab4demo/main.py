from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.semantic_analyzer import SemanticAnalyzer


TEST_CASES = [
    {
        "name": "number inference",
        "source": "var x = 1;\nprint x;\n",
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "string concatenation",
        "source": 'var s = "a" + "b";\nprint s;\n',
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "boolean condition",
        "source": "var flag = true;\nif (flag) print 1;\n",
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "first assignment fixes type",
        "source": "var x;\nx = 1;\nprint x;\n",
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "variable to variable inference",
        "source": "var c = 1;\nvar d = c;\nprint d;\n",
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "string equality returns boolean",
        "source": 'var is_same = "a" == "b";\nprint is_same;\n',
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "assignment type mismatch",
        "source": 'var x = 1;\nx = "test";\n',
        "expected_errors": ["cannot assign", "string", "number"],
        "expected_warnings": ["x", "never used"],
    },
    {
        "name": "string plus number is forbidden",
        "source": 'print "a" + 1;\n',
        "expected_errors": ["operator +", "string", "number"],
        "expected_warnings": [],
    },
    {
        "name": "numeric condition is forbidden",
        "source": "if (1) print 1;\n",
        "expected_errors": ["if condition", "boolean", "number"],
        "expected_warnings": [],
    },
    {
        "name": "string ordering is forbidden",
        "source": 'print "a" < "b";\n',
        "expected_errors": ["operator <", "string"],
        "expected_warnings": [],
    },
    {
        "name": "read before initialization",
        "source": "var x;\nprint x;\n",
        "expected_errors": ["x", "initialized"],
        "expected_warnings": [],
    },
    {
        "name": "boolean operators",
        "source": "var flag = true && false;\nprint flag;\n",
        "expected_errors": [],
        "expected_warnings": [],
    },
    {
        "name": "invalid boolean arithmetic",
        "source": "print true + false;\n",
        "expected_errors": ["operator +", "boolean"],
        "expected_warnings": [],
    },
    {
        "name": "float literals are rejected",
        "source": "var x = 3.1;\n",
        "expected_errors": [],
        "expected_warnings": [],
        "expected_exception": ["Float literals are not supported"],
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

    expected_exception = case.get("expected_exception", [])

    try:
        lexer = Lexer(case["source"])
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        errors, warnings = SemanticAnalyzer().analyze(ast)

        passed = (
            not expected_exception
            and has_expected_fragments(errors, case["expected_errors"])
            and has_expected_fragments(warnings, case["expected_warnings"])
        )

        print(f"Tokens: {len(tokens)}")
        print(f"AST: {len(ast)}")
        print_messages("Errors", errors)
        print_messages("Warnings", warnings)
        print(f"Result: {'PASS' if passed else 'FAIL'}")
        return passed
    except Exception as error:
        error_text = str(error)
        passed = has_expected_fragments([error_text], expected_exception)

        print("Runtime error:")
        print(f"  {error_text}")
        print(f"Result: {'PASS' if passed else 'FAIL'}")
        return passed


def main() -> None:
    passed_cases: list[str] = []
    failed_cases: list[str] = []

    for index, case in enumerate(TEST_CASES, start=1):
        if run_case(index, case):
            passed_cases.append(case["name"])
        else:
            failed_cases.append(case["name"])

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
