<?php

require_once dirname(__DIR__) . '/repl.lib.php';

$test_program_1 = "20 LET Y = X\n"
    . "10 LET X = 30\n"
    . "30 REM allows anything valid 123456\n"
    . "40 REM \"String comment\"\n"
    . "50 LET X = X + 10\n"
    . "60 PRINT X\n"
    . "70 GOTO 50\n";

$expect = [
    new CodeAssignment(20, 'Y', new Expression(new TokenSymbol('X', 'X'))),
    new CodeAssignment(10, 'X', new Expression(new TokenNumber(30, '30'))),
    new CodeNoop(30, [
        new TokenSymbol('ALLOWS', 'allows'),
        new TokenSymbol('ANYTHING', 'anything'),
        new TokenSymbol('VALID', 'valid'),
        new TokenNumber(123456, '123456'),
    ]),
    new CodeNoop(40, [
        new TokenString('String comment', 'String comment'),
    ]),
    new CodeAssignment(50, 'X', new Expression([
        new TokenOperator('+', '+'),
        new Expression(new TokenSymbol('X', 'X')),
        new Expression(new TokenNumber(10, '10')),
    ])),
    new CodePrint(60, new Expression(new TokenSymbol('X', 'X'))),
    new CodeGoto(70, new TokenNumber(50, '50')),
];

$ts = new TokenStreamSkippy($test_program_1);
$parser = new ParserFF($ts);

$statements = $parser->all();
//print_r($statements);
//print_r($expect);

try {
    foreach ($statements as $i => $item) {
        if (!isset($expect[$i])) {
            throw new Exception("Unexpected token at index $i: $item");
        }
        $expected = (string)$expect[$i];
        $received = (string)$item;
        if ($received !== $expected) {
            echo "Received: $received\n";
            echo "Expected: $expected\n";
            throw new Exception("Mismatch at index $i");
        }
    }
} catch (Exception $e) {
    echo "Exception: ", $e->getMessage(), "\n";
}
