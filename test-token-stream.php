<?php

require_once __DIR__ . '/repl.lib.php';

$test_statements = [
    "10 PRINT X + 12345",
    "20 PRINT \"Hello\"\nPRINT \"World\"",
    # Note the missing line numbers
    "PRINT 2*(10+X)\n",
    "IF X > 10 THEN\nPRINT Y!=X\nENDIF",
];

foreach ($test_statements as $statement) {
    echo "Statement: ", $statement, "\n";

    $ts = new TokenStreamSkippy($statement);

    $token = $ts->next();
    while ($token) {
        echo "  ", $token, "\n";
        $token = $ts->next();
    }
    echo "\n";
}
