
if False:
    expression_tests = [
        "1 + 1",
        "3 > 2",
        "10 + 2 * 3",
    ]

    for expr in expression_tests:
        print("Evaluating:", expr)

def resolve_pair(expr_vars, stack):
    a = stack.pop()
    b = stack.pop()
    ar = a if isinstance(a, int) else (expr_vars[a] if a in expr_vars else None)
    if ar is None:
        raise Exception("Unrecognized variable: " + a)
    br = b if isinstance(b, int) else (expr_vars[b] if b in expr_vars else None)
    if br is None:
        raise Exception("Unrecognized variable: " + b)
    return ar, br

def eval_expr(expr_vars, expr_stack):
    stack = []
    for token in expr_stack:
        if isinstance(token, int):
            # Just append the number
            stack.append(token)
        elif token == "+":
            a, b = resolve_pair(expr_vars, stack)
            stack.append(b + a)
        elif token == "-":
            a, b = resolve_pair(expr_vars, stack)
            stack.append(b - a)
        elif token == "*":
            a, b = resolve_pair(expr_vars, stack)
            stack.append(b * a)
        elif token == "/":
            a, b = resolve_pair(expr_vars, stack)
            stack.append(b // a)
        elif token == "<":
            a, b = resolve_pair(expr_vars, stack)
            stack.append(1 if b < a else 0)
        elif token == ">":
            a, b = resolve_pair(expr_vars, stack)
            stack.append(1 if b > a else 0)
        else:
            #raise Exception("Unrecognized token: " + token)
            # Keep as-is
            stack.append(token)
    return stack[0]

exprs_stacks = [
    [1, 1, "+"],
    [3, 2, ">"],
    [17, 5, "/"],
    [2, 3, "*", 10, "+"],
    ["X", 1, "+"],
    ["X", "Y", "*"],
]

expr_vars = {
    "X": 5,
    "Y": 10,
}

for expr_stack in exprs_stacks:
    print("Evaluating:", expr_stack)
    result = eval_expr(expr_vars, expr_stack)
    print("Result:", result)
