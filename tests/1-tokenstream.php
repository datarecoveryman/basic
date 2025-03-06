<?php

require_once dirname(__DIR__) . '/repl.lib.php';

// One big catch-all statement
$test_statement = "10 If X >= 123 then PRINT Foo(\"Bar\",Y)\n";

$expect = [
    new TokenNumber(10, '10'),
    new TokenSymbol('IF', 'If'),
    new TokenSymbol('X', 'X'),
    new TokenOperator('>=', '>='),
    new TokenNumber(123, '123'),
    new TokenSymbol('THEN', 'then'),
    new TokenSymbol('PRINT', 'PRINT'),
    new TokenSymbol('FOO', 'Foo'),
    new TokenDelimiter('(', '('),
    new TokenString('Bar', 'Bar'),
    new TokenDelimiter(',', ','),
    new TokenSymbol('Y', 'Y'),
    new TokenDelimiter(')', ')'),
    new TokenNewline("\n", "\n"),
];
//echo "Expected:\n";
//print_r($expect);

$ts = new TokenStreamSkippy($test_statement);
$tokens = $ts->remaining();
//echo "Received:\n";
//print_r($tokens);

//echo "Test statement: $test_statement";
try {
    foreach ($tokens as $i => $token) {
        if (!isset($expect[$i])) {
            throw new Exception("Unexpected token at index $i: $token");
        }
        $expected = (string)$expect[$i];
        $received = (string)$token;
        if ($received !== $expected) {
            echo "Received: $received\n";
            echo "Expected: $expected\n";
            throw new Exception("Mismatch at index $i");
        }
    }
    //echo "Passed\n";
} catch (Exception $e) {
    echo "Exception: ", $e->getMessage(), "\n";
}
