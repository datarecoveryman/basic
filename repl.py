import os

import Parser
import Runner
import TokenStream

def do_command(lines, all_tokens):
    cmd = all_tokens[0]
    cmd_lower = cmd.value.lower()
    if cmd_lower == "exit" or cmd_lower == "quit":
        print("Exiting program")
        exit(0)
    elif cmd_lower == "cls" or cmd_lower == "clear":
        # Clear the screen
        os.system("cls" if os.name == "nt" else "clear")
        return True
    elif cmd_lower == "help":
        cmds = ["cls", "exit", "help", "list", "next", "run"]
        cmds_bang = [c + "!" for c in cmds]
        print("Available commands: " + ", ".join(cmds_bang))
        return True
    elif cmd_lower == "list":
        print("")
        print("Listing program lines:")
        for key in sorted(lines.keys()):
            #value_line = " ".join([str(t.value) for t in lines[key]])
            ##original_line = " ".join([str(t.original) for t in lines[key]])
            #print(str(key) + ": " + value_line)
            print(f"{key}: {lines[key]}")
        print("")
        return True
    elif cmd_lower == "run":
        print("")
        print("Giving lines to Runner...")
        my_vars = {}
        my_runner = Runner.Runner(lines.values(), my_vars)
        print("")
        print("Running program...")
        max_ops = 15
        ops = 0
        keep_running = my_runner.next()
        while ops < max_ops and keep_running:
            ops += 1
            if ops >= max_ops:
                print("Max ops reached; stopping Runner early.")
                break
            keep_running = my_runner.next()
        print("Vars:", my_vars)
        print("")
        return True
    # Everything else should return before here
    print("Unknown command:", cmd)
    return False

def repl():
    lines = {}
    while True:
        # Get Line from user
        line = input("> ").strip()
        if len(line) == 0:
            continue
        #print("Line:", line)
        ts1 = TokenStream.TokenStreamSkippy(line + "\n")
        all_tokens = ts1.remaining()
        #print("Line Tokens:", all_tokens)
        #if len(all_tokens) <= 0:
        #    continue
        if len(all_tokens) >= 2 and isinstance(all_tokens[0], TokenStream.TokenSymbol) \
            and isinstance(all_tokens[1], TokenStream.TokenOperator) \
            and all_tokens[1].value == "!":
            do_command(lines, all_tokens)
            continue
        # Parse the Line
        ts2 = TokenStream.TokenStreamSkippy(line + "\n")
        p = Parser.ParserFF(ts2)
        try:
            stmt = p.take_statement()
            if stmt is None:
                print("Error parsing statement")
                continue
            print("Parsed:\n  ", stmt)
            lines[stmt.ln] = stmt
        except Parser.ParserError as e:
            print("Parser error:", e)

print("Hello. Commands end with ! so try help! or quit! to exit!")

repl()
