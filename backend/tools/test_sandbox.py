from sandbox import run_python_sandbox


code = """
while True:
    pass
"""


result = run_python_sandbox(code)


print("STDOUT:")
print(result.stdout)

print("STDERR:")
print(result.stderr)

print("RETURN CODE:")
print(result.return_code)

print("TIMED OUT:")
print(result.timed_out)