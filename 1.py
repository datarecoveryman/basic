
def do_command(line):
    # Check if the line is a command
    if line == "list":
        print("Listing program lines:")
        for key in sorted(lines_dict.keys()):
            print(str(key) + ": " + lines_dict[key])
        return True
    elif line == "exit":
        print("Exiting program")
        exit(0)
    elif line == "#":
        print("Next line number: " + str(next_line_number))
        return True
    return False

# Program lines
lines_dict = {}

next_line_number = 10
while True:
    # Get line from user
    line = input("> ").strip()
    if len(line) == 0:
        continue
    # If the line is a command, execute it
    if do_command(line):
        #print("Line was a command, continuing")
        continue
    else:
        # Store a new line in the program
        tokens = line.split(" ")
        # Check if the first token is a number
        if tokens[0].isnumeric():
            given_number = int(tokens[0])
            # Check if the line number is the next line
            if given_number == next_line_number:
                print("No change needed")
            else:
                print("Setting line number: " + str(given_number))
                next_line_number = given_number
        # Store the line
        lines_dict[next_line_number] = line
        print("Stored line: " + str(next_line_number) + ": " + line)
        next_line_number += 10

# Thoughts:
# Mistyping "list" as "lis" meant I added a junk line on accident.
# 2 fixes:
#   force line #s
#   change commands to use a sigil
