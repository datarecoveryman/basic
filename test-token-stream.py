
from TokenStream import TokenStream

test_statements = [
    "PRINT X + 12345",
    "PRINT \"Hello\"\nPRINT \"World\"",
    "PRINT 2*(10+X)\n",
    "IF X > 10 THEN\nPRINT Y!=X\nENDIF",
]
for stmt in test_statements:
    print("Statement:", stmt)
    ts = TokenStream(stmt)
    #token = ts.next()
    #while token is not None:
    #    print("Token:", token)
    #    token = ts.next()
    for token in ts.all():
        print(token)
    print("")
