
import Parser
import TokenStream
import Runner

#+ "50 LET Y = Y + 1\n" \ # Requires expression support
test_program_1 = "20 LET X = 10\n" \
    + "10 LET Y = X\n" \
    + "30 REM allow anything valid 123456\n" \
    + "40 PRINT Y\n" \
    + "50 LET Y = 20\n" \
    + "60 GOTO 40\n"
print("Test program:")
print(test_program_1.strip())
print("")

print("Break program into statements:")
ts = TokenStream.TokenStream(test_program_1)
p = Parser.Parser(ts)
statements = p.all()
for statement in statements:
    print(statement)
print("")

# Give statements to Runner
my_vars = {}
my_runner = Runner.Runner(statements, my_vars)
if False:
    print("Program lines in-order:")
    for ln in my_runner.line_numbers:
        stmt = my_runner.lines[ln]
        print(f"{ln}: {stmt}")

max_ops = 10
ops = 0
keep_running = my_runner.next()
while ops < max_ops and keep_running:
    ops += 1
    keep_running = my_runner.next()
print("Vars:", my_vars)
