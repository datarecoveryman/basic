import os

import Parser
import TokenStream

def do_command(lines, next_line_number, cmd, ts):
    cmd_lower = cmd.value.lower()
    if cmd_lower == "exit" or cmd_lower == "quit":
        print("Exiting program")
        exit(0)
    elif cmd_lower == "cls" or cmd_lower == "clear":
        # Clear the screen
        os.system("cls" if os.name == "nt" else "clear")
        return True
    elif cmd_lower == "help":
        cmds = ["cls", "exit", "help", "list", "line", "next", "run"]
        cmds_bang = [c + "!" for c in cmds]
        print("Available commands: " + ", ".join(cmds_bang))
        return True
    elif cmd_lower == "line" or cmd_lower == "next":
        print("Next line number: " + str(next_line_number))
        return True
    elif cmd_lower == "list":
        print("")
        print("Listing program lines:")
        for key in sorted(lines.keys()):
            value_line = " ".join([str(t.value) for t in lines[key]])
            #original_line = " ".join([str(t.original) for t in lines[key]])
            print(str(key) + ": " + value_line)
        print("")
        return True
    elif cmd_lower == "run":
        print("")
        print("TODO: Running program...")
        print("")
        return True
    return False

def repl():
    lines = {}
    next_line_number = 10
    while True:
        # Get line from user
        line = input("> ").strip()
        if len(line) == 0:
            continue
        print("Lexing line:", line)
        ts = TokenStream.TokenStream(line + "\n")
        cmd = ts.take_symbol()
        #print("Cmd:", cmd)
        #print("Peek:", ts.peek())
        if cmd is not None and ts.peek() == "!":
            do_command(lines, next_line_number, cmd, ts)
            continue
        ts.reset()
        line_number = ts.take_number()
        if line_number is not None:
            next_line_number = line_number.value
            print("Set line number:", next_line_number)
        tokens = ts.remaining()
        for t in tokens:
            print(t)
        lines[next_line_number] = tokens
        print("Lines:")
        for key in sorted(lines.keys()):
            print(str(key) + ": " + " ".join([str(t.original) for t in lines[key]]))
        next_line_number += 10

print("Hello. Commands end with ! so try help! or quit! to exit!")

repl()
