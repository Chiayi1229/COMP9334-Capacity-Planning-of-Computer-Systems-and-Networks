import subprocess

def execute_test_case(index):
    print(f"\n>>> Starting Test Case #{index}")
    
    result = subprocess.run(
        ["./run_test.sh", str(index)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(f"[run_test.sh Error] {result.stderr.strip()}")

    if result.returncode != 0:
        print(f"[run_test.sh] Test {index} exited with code {result.returncode}")

    compare = subprocess.run(
        ["python3", "cf_output_with_ref.py", str(index)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if compare.stdout:
        print(compare.stdout.strip())
    if compare.stderr:
        print(f"[cf_output_with_ref.py Error] {compare.stderr.strip()}")

    if compare.returncode != 0:
        print(f"[Comparison] Test {index} failed (return code {compare.returncode})")


def batch_run_tests(start=1, end=8):
    for test_id in range(start, end):
        execute_test_case(test_id)


if __name__ == "__main__":
    batch_run_tests()
