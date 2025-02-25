<?php

require_once __DIR__ . '/repl.lib.php';

function run_test($program, $granular = true, $debug = false) {
    echo "Test program:\n";
    echo rtrim($program) . "\n";
    echo "\n";

    //echo "Create token stream and parser...\n";
    $ts = new TokenStreamSkippy($program, false && $debug);
    $parser = new ParserFF($ts, $debug);
    //echo "\n";

    //echo "Parse the program into statements:\n";
    //echo "(Note: the line numbers are not sorted by Parser.)\n";
    //echo "\n";
    $statements = [];
    if ($granular) { # Granular
        try {
            // On a parse error, take_statement() throws
            // an exception with the error message.
            $stmt = $parser->take_statement();
            while ($stmt !== false) {
                $statements[] = $stmt;
                //echo "Statement: ", $stmt, "\n";
                $stmt = $parser->take_statement();
            }
        } catch (Exception $e) {
            echo "Parse error: ", $e->getMessage(), "\n";
        }
    } else {
        # all() won't get them as it parses if it crashes.
        $statements = $parser->all();
        //foreach ($parser->all() as $statement) {
        //    echo "Statement: ", $statement, "\n";
        //}
    }

    # Give statements to Runner
    $my_vars = [];
    $my_runner = new Runner($statements, $my_vars);
    if (true) {
        echo "Program lines in-order:\n";
        foreach ($my_runner->line_numbers as $ln) {
            $stmt = $my_runner->lines[$ln];
            echo "{$ln}: {$stmt}\n";
        }
        echo "\n";
    }

    echo "Running...\n";
    $max_ops = 15;
    $ops = 0;
    $keep_running = $my_runner->next();
    while ($ops < $max_ops && $keep_running) {
        $ops += 1;
        if ($ops >= $max_ops) {
            echo "Max ops reached; stopping Runner early.\n";
            break;
        }
        $keep_running = $my_runner->next();
    }
    echo "Vars:"; print_r($my_vars);
    echo "\n";
}

$test_program_1 = "10 LET X = 100\n"
    . "20 LET Y = X * 4\n";

#+ "50 LET Y = Y + 1\n" \ # Requires expression support
# Flipping 10 and 20 correctly fails due to undefined X.
$test_program_2 = "20 LET X = 100\n"
    . "10 LET Y = 77\n"
    . "40 REM comment\n"
    . "60 PRINT Y\n"
    . "80 LET Y = Y + X\n"
    . "99 GOTO 60\n";

run_test($test_program_1);
run_test($test_program_2);
