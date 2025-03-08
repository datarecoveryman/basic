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
$expect_vars = (object)[
    'X' => 70,
    'Y' => 30,
];

$ts = new TokenStreamSkippy($test_program_1);
$parser = new ParserFF($ts);

$statements = $parser->all();
//print_r($statements);
//print_r($expect);

try {
    # Give statements to Runner
    $my_vars = (object)[
        //'foo' => 'bar',
    ];
    $my_runner = new Runner($statements, $my_vars);
    if (false) {
        echo "Program lines in-order:\n";
        foreach ($my_runner->line_numbers as $ln) {
            $stmt = $my_runner->lines[$ln];
            echo "{$ln}: {$stmt}\n";
        }
        echo "\n";
    }

    //echo "Running...\n";
    // Use output buffering to capture all the print statements
    ob_start();
    $max_ops = 15;
    $ops = 0;
    $keep_running = $my_runner->next();
    while ($ops < $max_ops && $keep_running) {
        $ops += 1;
        if ($ops >= $max_ops) {
            //echo "Max ops reached; stopping Runner early.\n";
            break;
        }
        $keep_running = $my_runner->next();
    }
    //print_r($my_runner);
    //echo "Vars:"; print_r($my_vars);
    //echo "\n";
    $output = ob_get_clean();
    //echo "Output: \"$output\"\n";
    //if (strlen($output) > 0) {
    //   throw new Exception("Output: $output");
    //}

    foreach ($expect_vars as $var => $value) {
        if (!isset($my_vars->$var)) {
            throw new Exception("Expected variable '$var' not found");
        }
        if ($my_vars->$var !== $value) {
            throw new Exception("Expected variable '$var' to be $value, but got {$my_vars->$var}");
        }
        //echo "Variable '$var' is $value\n";
    }

} catch (Exception $e) {
    echo "Exception: ", $e->getMessage(), "\n";
}
