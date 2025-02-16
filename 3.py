import os

def index_of(items, value):
    ret = -1
    for i in range(len(items)):
        if items[i] == value:
            ret = i
            break
    return ret

# Immediate commands end with ! and are not stored in the program.
def do_command(line):
    # Ignore case on commands
    line = line.lower()
    if line == "exit!" or line == "quit!":
        print("Exiting program")
        exit(0)
    elif line == "cls!" or line == "clear!":
        # Clear the screen
        os.system("cls" if os.name == "nt" else "clear")
        return True
    elif line == "help!":
        print("Available commands: cls!, exit!, help!, list!, line!, next!, run!")
        return True
    elif line == "list!":
        print("")
        print("Listing program lines:")
        for key in sorted(lines.keys()):
            print(str(key) + ": " + lines[key])
        print("")
        return True
    elif line == "line!" or line == "next!":
        print("Next line number: " + str(next_line_number))
        return True
    elif line == "run!":
        print("")
        print("Running program...")
        try:
            ivars = {}
            interp1(10, lines, ivars)
            if len(ivars) > 0:
                print("Variables after run:")
                for key in ivars.keys():
                    print(key + ": " + str(ivars[key]))
        except Exception as e:
            print("Error:", e)
        print("")
        return True
    return False

def interp1(remaining_ops, lines, interp_vars):
    # With the line numbers in their own list,
    # a single line_index can be used to iterate
    # without needing to know the line number.
    # But also without losing the line numbers a la array_values()
    line_numbers = sorted(lines.keys())[:]
    #print("Line numbers:", line_numbers)
    line_index = 0
    while remaining_ops > 0 and line_index < len(line_numbers):
        line_number = line_numbers[line_index]
        line = lines[line_number]
        #debug_line_prefix = "Line[" + str(line_index) + "] = Line " + str(line_number) + ":"
        #print(debug_line_prefix, line)
        debug_line_prefix = "  " + str(line_number) + ":" #"\t" # Indent subsequent debug lines instead
        tokens = line.split()
        maybe_command = tokens[0].upper()
        if maybe_command == "PRINT":
            # Print statement
            if len(tokens) == 1:
                raise Exception("Expected expression after PRINT")
            # if the first letter is a quote, then it's a string and we should keep printing
            # tokens until we find the closing quote
            if tokens[1][0] == "\"":
                # TODO: strip the quotes
                #print(" ".join(tokens[1:]))
                print(debug_line_prefix, " ".join(tokens[1:])[1:-1]) # <- yes officer, this right here.
            else:
                # Print the remaining tokens
                for token in tokens[1:]:
                    if token in interp_vars:
                        print(debug_line_prefix, token + " =", interp_vars[token])
                        #print(interp_vars[token])
                    else:
                        print(debug_line_prefix, token)
        elif maybe_command == "GOTO":
            # GOTO statement
            if len(tokens) != 2:
                raise Exception("Expected a line number after GOTO")
            if not tokens[1].isnumeric():
                raise Exception("Line numbers for GOTO must be numeric, though variable GOTOs would be rad!")
            # Find the index of the line number, if present
            line_index = index_of(line_numbers, int(tokens[1]))
            #print("Line index for", tokens[1], "is", line_index)
            if line_index < 0:
                raise Exception("Line number not found: " + tokens[1])
            print(debug_line_prefix, "Jumped to line:", tokens[1])
            #print("Line referred to", lines[line_numbers[line_index]])
            remaining_ops -= 1
            continue
        elif maybe_command == "LET":
            # Assignment statement, e.g. ["LET","X","=","5"]
            if tokens[2] != "=":
                raise Exception("Expected = as 3rd token in LET statement")
            var_name = tokens[1]
            #print("Assigning var:", var_name)
            # Read the last token as an integer literal
            # TODO: Handle literal expressions (e.g., 2 + 2)
            if not tokens[-1].isnumeric():
                raise Exception("Expected integer literal after LET")
            assign_val = int(tokens[-1])
            #print("Assigning val:", assign_val)
            interp_vars[var_name] = assign_val
            #print("Vars:", interp_vars)
            print(debug_line_prefix, "Assigned", var_name, "=", assign_val)
        elif maybe_command == "REM":
            # REM statement; ignore the line
            #print(debug_line_prefix, "Comment:", " ".join(tokens[1:]))
            pass
        else:
            raise Exception("Unrecognized statement: " + line)
        # Move to the next line
        line_index += 1
        remaining_ops -= 1
    return remaining_ops

print("Hello. Commands end with ! so try help! or quit! to exit!")

lines = {}
next_line_number = 10
while True:
    # Get line from user
    line = input("> ").strip()
    if len(line) == 0:
        continue
    tokens = line.split(" ")
    if "!" in tokens[0]:
        # Assert: is a command
        if not do_command(line):
            print("Unrecognized command: " + line)
        continue
    # Store a new line in the program
    # A leading number sets this line's number
    if tokens[0].isnumeric():
        next_line_number = int(tokens[0])
        remaining = " ".join(tokens[1:])
    else:
        remaining = line
    lines[next_line_number] = remaining
    print("Stored line " + str(next_line_number) + ": " + remaining)
    next_line_number += 10
