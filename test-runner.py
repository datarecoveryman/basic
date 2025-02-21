
import Parser
import TokenStream
import Runner

#+ "50 LET Y = Y + 1\n" \ # Requires expression support
# Flipping 10 and 20 correctly fails due to undefined X.
test_program_1 = "10 LET X = 100\n" \
    + "20 LET Y = 777\n" \
    + "40 REM comment\n" \
    + "60 PRINT Y\n" \
    + "80 LET Y = Q + 10\n" \
    + "99 GOTO 60\n"

test_program_2 = "10 LET X = 100\n" \
    + "20 LET Y = X * 4\n"

print("Test program:")
print(test_program_2.strip())
print("")

print("Break program into statements:")
ts = TokenStream.TokenStream(test_program_2)
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
