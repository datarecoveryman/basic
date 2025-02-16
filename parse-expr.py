
# TODO: A version with last and taking_type instead of last_number and last_symbol

def parse_with_checks2(expression_string):
    binops = "+-*/^"
    delims = "(),"
    whitespace = " \t\r\n"
    num_paren_open = 0
    num_paren_close = 0
    taking_type = None
    tokens = []
    last = ""
    for char in expression_string:
        if char in whitespace:
            if len(last):
                raise ValueError(f"Unexpected whitespace: {char}")
        elif char in delims:
            num_paren_open = num_paren_open + 1 if char == "(" else num_paren_open
            num_paren_close = num_paren_close + 1 if char == ")" else num_paren_close
            if len(last):
                tokens.append(last)
                last = ""
                taking_type = None
            tokens.append(char)
        elif char.isdigit() or char == ".":
            if taking_type is None or isinstance(taking_type, int):
                taking_type = int(char)
                last += char
            else:
                raise ValueError(f"Unexpected digit ({char}) while reading \"{last}\"")
        elif char.isalpha():
            if taking_type is None or isinstance(taking_type, str):
                taking_type = str(char)
                last += char
            else:
                raise ValueError(f"Unexpected letter ({char}) while reading \"{last}\"")
        elif char in binops:
            if len(last):
                tokens.append(last)
                last = ""
                taking_type = None
            tokens.append(char)
        else:
            raise ValueError(f"Invalid character: {char}")
    if len(last):
        tokens.append(last)
    if num_paren_open != num_paren_close:
        raise ValueError(f"Mismatched parentheses: {num_paren_open} open, {num_paren_close} close")
    return tokens

def parse_with_checks1(expression_string):
    binops = "+-*/^"
    delims = "(),"
    whitespace = " \t\r\n"
    last_symbol = ""
    last_number = ""
    num_paren_open = 0
    num_paren_close = 0
    tokens = []
    last_char = ""
    for char in expression_string:
        if char in whitespace:
            pass
        elif char in delims:
            num_paren_open = num_paren_open + 1 if char == "(" else num_paren_open
            num_paren_close = num_paren_close + 1 if char == ")" else num_paren_close
            if len(last_number):
                tokens.append(last_number)
                last_number = ""
            elif len(last_symbol):
                tokens.append(last_symbol)
                last_symbol = ""
            tokens.append(char)
        elif char.isdigit() or char == ".": # number
            last_number += char
        elif char.isalpha(): # symbol
            last_symbol += char
        elif char in binops: # break for math
            if len(last_number):
                tokens.append(last_number)
                last_number = ""
            elif len(last_symbol):
                tokens.append(last_symbol)
                last_symbol = ""
            tokens.append(char)
        else:
            raise ValueError(f"Invalid character: {char}")
        last_char = char
    if len(last_number):
        tokens.append(last_number)
    elif len(last_symbol):
        tokens.append(last_symbol)
    if num_paren_open != num_paren_close:
        raise ValueError(f"Mismatched parentheses: {num_paren_open} open, {num_paren_close} close")
    return tokens

def parse_no_checks(expression_string):
    binops = "+-*/^"
    delims = "(),"
    whitespace = " \t\r\n"
    print("Bin ops:", binops)

    tokens = []
    last = ""
    for char in expression_string:
        if char in whitespace:
            pass
        elif char.isdigit() or char == "." or char.isalpha():
            # Append if digit
            # Append if letter (interpreter can figure out if its a variable or a function)
            last += char
        elif char in binops or char in delims:
            # Break
            if len(last):
                tokens.append(last)
                last = ""
            # Append operator/delimeter
            tokens.append(char)
        else:
            raise ValueError(f"Invalid character: {char}")
    if len(last):
        tokens.append(last)
    return tokens

def check_expr(expr):
    print("Parsing expression:", expr)
    try:
        tokens = parse_with_checks2(expr)
        return tokens
    except ValueError as e:
        print("Expression was invalid:", e)
    return None

test_expressions = [
    "X^2 + MAX(ABS(Y), 10)",
    "BROKEN(x1, 10Y)",
    "VALID(X, 20)",
]
for t in test_expressions:
    tokens = check_expr(t)
    print("Tokens:", tokens)
    print("")

if False:
    complicated_expr = "X^2 + MAX(ABS(Y), 10)"
    tokens = check_expr(complicated_expr)
    print("Test expression:", tokens)

    tokens1 = parse_no_checks(complicated_expr)
    print("Parsed tokens, no checks:", tokens1)

    invalid_expr = "TWOARGS(x1, 10Y)"
    try:
        tokens2 = parse_with_checks1(invalid_expr)
        print(f"parse_with_checks1({invalid_expr}):", tokens2)
    except ValueError as e:
        print("Expression:", invalid_expr)
        print("Expression was invalid:", e)

    valid_expr = "TWOARGS(1, 10)"
    try:
        #tokens3 = parse_with_checks2(valid_expr)
        #print(f"parse_with_checks2({valid_expr}):", tokens3)

        invalid_expr = "TWOARGS(x1, 10Y)"
        print(f"parse_with_checks2({invalid_expr})")
        tokens4 = parse_with_checks2(invalid_expr)
        print("Parsed tokens, with checks:", tokens4)
    except ValueError as e:
        print("Expression was invalid:", e)
