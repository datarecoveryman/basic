
# This one is going with the "special character in commands" idea.

def do_command(line):
    # Ignore case on commands
    line = line.lower()
    if line == "exit!" or line == "quit!":
        print("Exiting program")
        exit(0)
    elif line == "help!":
        print("Available commands: exit!, help!, list!, line!, next!, run!")
        return True
    elif line == "list!":
        print("Listing program lines:")
        for key in sorted(lines_dict.keys()):
            print(str(key) + " " + lines_dict[key])
        return True
    elif line == "line!" or line == "next!":
        print("Next line number: " + str(next_line_number))
        return True
    elif line == "run!":
        print("TODO: run program")
        return True
    return False

print("Hello. Commands end with ! so try help! or quit! to exit!")

# Program lines
lines_dict = {}

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
    lines_dict[next_line_number] = remaining
    print("Stored line: " + str(next_line_number) + " " + remaining)
    next_line_number += 10
