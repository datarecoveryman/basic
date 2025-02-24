<?php

require_once __DIR__ . '/repl.lib.php';

function run_test($program, $granular = true, $debug = true) {
    echo "Test program:\n";
    echo rtrim($program) . "\n";
    echo "\n";

    echo "Create token stream and parser...\n";
    $ts = new TokenStreamSkippy($program);
    $parser = new ParserFF($ts);
    echo "\n";

    echo "Parse the program into statements:\n";
    echo "(Note: the line numbers are not sorted by Parser.)\n";
    echo "\n";
    if ($granular) { # Granular
        $stmt = $p->take_statement();
        while ($stmt !== false) {
            echo "Statement:", $stmt, "\n";
            echo "\n";
            stmt = $p->take_statement();
        }
    } else {
        # all() won't get them as it parses if it crashes.
        echo "Statements:\n"
        foreach ($p->all() as $statement) {
            echo "Statement:", $statement, "\n";
            echo "\n";
        }
    }
}

function test_generic() {
    # Line numbers are mandatory
    $test_program_1 = "20 LET Y = X\n"
        + "10 LET X = 10\n"
        + "30 REM allows anything valid 123456\n"
        + "40 LET X = 40\n"
        + "50 PRINT Y\n"
        + "60 GOTO 999\n";
    run_test($test_program_1);
}

function test_take_statement() {
    $program = "10 GOTO 20\n"
        + "20 LET X = 100\n"
        + "30 LET Y = X * 4\n"
        + "15 REM \"String comment\"\n";
        //+ "40 PRINT Y\n" \
        //+ "50 GOTO 999\n"
    run_test($program);
}

test_generic();
test_take_statement();
