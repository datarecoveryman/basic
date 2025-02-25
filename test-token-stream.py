import TokenStream

test_statements = [
    #"10 PRINT X + 12345",
    #"20 PRINT \"Hello\"\nPRINT \"World\"",
    # Note the missing line numbers
    #"PRINT 2*(10+X)\n",
    #"IF X > 10 THEN\nPRINT Y!=X\nENDIF",
    "10 If X >= 123 Then Print Foo(X, \"Bar\")\n"
]

for stmt in test_statements:
    print("Statement:", stmt.rstrip())

    if False: # Legacy TokenStream
        ts = TokenStream.TokenStream(stmt)
    else: # New TokenStreamSkippy
        ts = TokenStream.TokenStreamSkippy(stmt)
    
    if True: # Granular
        token = ts.next()
        while token is not None:
            print(" ", token)
            token = ts.next()
    else: # All
        for token in ts.all():
            print(" ", token)
    print("")
