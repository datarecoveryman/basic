<?php

abstract class Code {
    public readonly int $line_number;
    //public readonly $statement;

    public function __construct($line_number) {
        $this->line_number = $line_number;
    }

    public function __toString() {
        return $this->line_number . ':' . get_class($this) . "()";
    }
}

class CodeAssignment extends Code {
    public readonly string $variable;
    public readonly Expression $expression;
    public function __construct($line_number, $variable, $expression) {
        parent::__construct($line_number);
        $this->variable = $variable;
        $this->expression = $expression;
    }
    public function __toString() {
        return $this->line_number . ':' . get_class($this) . "($this->variable, $this->expression)";
    }
}

class CodeGoto extends Code {
    public readonly TokenNumber $target;
    public function __construct($line_number, $target) {
        parent::__construct($line_number);
        $this->target = $target;
    }
    public function __toString() {
        return $this->line_number . ':' . get_class($this) . "($this->target)";
    }
}

class CodeNoop extends Code {
    public readonly array $tokens;
    public function __construct($line_number, $tokens) {
        parent::__construct($line_number);
        $this->tokens = $tokens;
    }
    public function __toString() {
        //return $this->line_number . ':' . get_class($this) . "($this->tokens)";
        $token_strs = array_map('strval', $this->tokens);
        $token_str = implode(' ', $token_strs);
        return $this->line_number . ':' . get_class($this) . "($token_str)";
    }
}

class CodePrint extends Code {
    public readonly Expression $expression;
    public function __construct($line_number, $expression) {
        parent::__construct($line_number);
        $this->expression = $expression;
    }
    public function __toString() {
        return $this->line_number . ':' . get_class($this) . "($this->expression)";
    }
}

class Expression {
    public $expr;
    public function __construct($expr) {
        $this->expr = $expr;
    }
    public function __toString() {
        $expr_str = is_array($this->expr) ? implode(' ', $this->expr) : strval($this->expr);
        return get_class($this) . "($expr_str)";
    }
    public function get_value($vars_dict) {
        if ($this->expr instanceof TokenNumber) {
            return $this->expr->value;
        }
        if ($this->expr instanceof TokenString) {
            return $this->expr->value;
        }
        if ($this->expr instanceof TokenSymbol) {
            if (isset($vars_dict[$this->expr->value])) {
                return $vars_dict[$this->expr->value];
            }
            throw new Exception("Variable not found: " . $this->expr->value);
        }
        if (is_array($this->expr)) {
            if (!($this->expr[0] instanceof TokenOperator)) {
                throw new Exception("Expected operator, got: " . $op);
            }
            $op = $this->expr[0];
            if (!($this->expr[1] instanceof Expression)) {
                throw new Exception("Expected expression, got: " . $this->expr[1]);
            }
            $left = $this->expr[1]->get_value($vars_dict);
            if (!($this->expr[2] instanceof Expression)) {
                throw new Exception("Expected expression, got: " . $this->expr[2]);
            }
            $right = $this->expr[2]->get_value($vars_dict);
            switch ($op->value) {
                case '+':
                    return $left + $right;
                case '-':
                    return $left - $right;
                case '*':
                    return $left * $right;
                case '/':
                    return $left / $right;
                case '^':
                    return pow($left, $right);
                default:
                    throw new Exception("Unknown operator: " . $op->value);
            }
        }
        throw new Exception("Unknown expression type: " . get_class($this->expr));
    }
}

// ParserFF class
class ParserFF {
    private $tokens;
    private $debug;

    public function __construct($token_stream, $debug = false) {
        if (!($token_stream instanceof TokenStreamSkippy)) {
            throw new Exception("Expected TokenStreamSkippy");
        }
        $this->tokens = $token_stream;
        $this->debug = $debug; // Show the debug print()s
    }

    private function _debug_print(string $label, $msg) {
        if ($this->debug) {
            echo "$label: ";
            if (is_array($msg)) {
                print_r($msg);
            } else {
                echo is_string($msg) ? "\"$msg\"" : $msg;
            }
            echo "\n";
        }
    }
    
    protected function _get_precedence(TokenOperator $token) {
        if ($token->value == '+' || $token->value == '-') {
            return 1;
        }
        if ($token->value == '*' || $token->value == '/') {
            return 2;
        }
        if ($token->value == '^') {
            return 3;
        }
        return 0;
    }

    protected function _parse_expression($precedence = 0) {
        // parse_expression() always creates a left_expr, the first term.
        $left_expr = $this->_parse_primary();
        while (true) {
            $this->_debug_print("left_expr", $left_expr);
            $peek = $this->tokens->peek();
            //$this->_debug_print("peek", $peek);
            if ($peek === false) {
                throw new Exception("Expected operator or newline, got None");
            }
            if ($peek === "\n") { // Normal end of a single-term expression
                //$this->_debug_print("parse_expression: found newline, ending expression", '');
                break;
            }
            //$op = $this->tokens->take_operator();
            //if ($op === false) {
            //    throw new Exception("Expected operator, got " . $peek);
            //}
            $op = $this->_take_x_or_throw('operator', "Expected operator, got " . $peek);
            $this->_debug_print("parse_expression: operator", $op);
            $op_precedence = $this->_get_precedence($op);
            if ($op_precedence < $precedence) {
                break;
            }
            $right_expr = $this->_parse_expression($op_precedence + 1);
            $left_expr = new Expression([$op, $left_expr, $right_expr]);
        }
        return $left_expr;
    }

    protected function _parse_primary() {
        // the "primary" in an expression can be a number, a variable,
        // a string, or a parenthesized expression (recursive).
        // But, with multiple options, the "demanding" approach has
        // to be flexible.
        $n = $this->tokens->next();
        $this->_debug_print("Next token", $n);
        if ($n instanceof TokenString) {
            $this->_debug_print("parse_primary: string", $n);
            return new Expression($n);
        }
        if ($n instanceof TokenNumber || $n instanceof TokenSymbol) {
            $this->_debug_print("parse_primary: number/symbol", $n);
            return new Expression($n);
        }
        if ($n instanceof TokenDelimiter && $n->value == '(') {
            $expr = $this->_parse_expression();
            $closing_paren = $this->tokens->take_delimiter();
            if (!($closing_paren instanceof TokenDelimiter) || $closing_paren->value != ')') {
                throw new Exception("Expected closing parenthesis");
            }
            return $expr;
        }
        //throw new Exception("Unexpected token: " . strval($n));
        throw new Exception("Expected value or expression, got: " . strval($n));
    }

    protected function _take_x_or_throw(string $x, $ex_or_string) {
        $method = "take_$x";
        //$this->_debug_print("take_x_or_throw: method", $method);
        if (!method_exists($this->tokens, $method)) {
            throw new Exception("Method $method does not exist");
        }
        $token = $this->tokens->$method();
        //$this->_debug_print("take_x_or_throw: token", $token);
        if ($token === false) {
            throw is_string($ex_or_string) ? new Exception($ex_or_string) : $ex_or_string;
        }
        return $token;
    }

    public function all() {
        $statements = [];
        $stmt = $this->take_statement();
        while ($stmt !== false) {
            $statements[] = $stmt;
            $stmt = $this->take_statement();
        }
        return $statements;
    }

    public function take_statement() {
        // Consume one statement's worth of tokens,
        // which is variable, since it depends on the statement.
        // General structure: <line number> <verb> <args...> <newline>
        $line_number_token = $this->tokens->take_number();
        if ($line_number_token === false) {
            // No start, no statement
            return false;
        }
        $line_number = $line_number_token->value;
        $this->_debug_print("Line number", $line_number);
        $verb = $this->_take_x_or_throw('symbol', "Expected verb after $line_number");
        $this->_debug_print("Verb", $verb);
        $code = false;
        if ($verb->value == "GOTO") {
            # GOTO 123
            $target_line_number = $this->_take_x_or_throw('number', "Expected line number after GOTO");
            $this->_debug_print("GOTO line number", $target_line_number);
            $code = new CodeGoto($line_number, $target_line_number);
        } elseif ($verb->value == "LET") {
            // LET X = 5
            $var = $this->_take_x_or_throw('symbol', "Expected variable after LET");
            $this->_debug_print("LET variable", $var);
            $equals = $this->tokens->take_operator();
            if ($equals === false || $equals->value != "=") {
                throw new Exception("Expected = after LET {$var->value}");
            }
            //$this->_debug_print("LET equals:", $equals);
            $expr = $this->_parse_expression();
            $this->_debug_print("LET expression", $expr);
            $code = new CodeAssignment($line_number, $var->value, $expr);
        } elseif ($verb->value == "PRINT") {
            # PRINT "Hello"
            $expr = $this->_parse_expression();
            $code = new CodePrint($line_number, $expr);
        } elseif ($verb->value == "REM") {
            // REM anything "is fine" here
            $comment_tokens = $this->tokens->take_until_newline();
            if ($comment_tokens === false) {
                throw new Exception("Expected string after REM");
            }
            $this->_debug_print("REM comment", $comment_tokens);
            // I don't like putting token/string processing in here.
            // Leave that to CodeNoop.
            $code = new CodeNoop($line_number, $comment_tokens);
        //} else {
        //    throw new Exception("Unknown verb: " . (string)$verb);
        }
        if ($code === false) {
            throw new Exception("Unknown verb: " . (string)$verb);
        }
        if ($verb->value != "REM") {
            $newline = $this->_take_x_or_throw('newline', "Expected trailing newline");
        }
        return $code;
    }
}

abstract class Token {
    public $value;
    public readonly string $original;

    public function __construct($value, $original) {
        $this->value = $value;
        $this->original = $original;
    }

    public function __toString() {
        $value = is_string($this->value) ? '"' . $this->value . '"' : $this->value;
        return get_class($this) . "($value, \"$this->original\")";
    }
}

class TokenDelimiter extends Token {
}
class TokenNewline extends Token {
    public function __toString() {
        return get_class($this) . "()";
    }
}
class TokenNumber extends Token {
    public function __toString() {
        return get_class($this) . "($this->value, \"$this->original\")";
    }
}
class TokenOperator extends Token {
}
class TokenSymbol extends Token {
    public function __toString() {
        return get_class($this) . "($this->value, \"$this->original\")";
    }
}
class TokenString extends Token {
}

class TokenStreamSkippy {
    private string $text;
    private int $idx;
    private bool $debug;

    public const DELIMS = "(),";
    public const DIGITS = "0123456789";
    public const NEWLINES = "\n\r";
    public const OPERATORS = "= ! + - * / ^ < > <= >= == <>";
    public const SPACES = " \t";
    public const VAR_FIRST = "_ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    public const VAR_OTHER = "_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";

    public function __construct(string $text, $debug = false) {
        $this->text = $text;
        $this->idx = 0;
        $this->debug = $debug;
    }

    protected function _debug_print(string $label, $value) {
        if ($this->debug) {
            echo "$label: ";
            if (is_array($value)) {
                print_r($value);
            } else {
                echo $value;
            }
            echo "\n";
        }
    }

    public function next() {
        $p = $this->skip();
        $this->_debug_print('next: p', $p);
        if ($p === false) {
            return false;
        }
        // Guess based off the first non-space character
        if (strpos(self::NEWLINES, $p) !== false) {
            return $this->take_newline();
        }
        if ($p === '"') {
            return $this->take_string();
        }
        if (strpos(self::DIGITS, $p) !== false) {
            return $this->take_number();
        }
        if (strpos(self::DELIMS, $p) !== false) {
            return $this->take_delim();
        }
        if (in_array($p, explode(' ', self::OPERATORS))) {
            return $this->take_operator();
        }
        if (strpos(self::VAR_FIRST, strtoupper($p)) !== false) {
            return $this->take_symbol();
        }
        throw new Exception("Unexpected character: $p");
    }

    public function peek() {
        if ($this->idx < mb_strlen($this->text)) {
            $ret = mb_substr($this->text, $this->idx, 1);
            //echo "peek ret: "; var_dump($ret);
            if (mb_strlen($ret) < 1) {
                throw new Exception("Peek expected to be able to return a character; bad idx math?");
            }
            return $ret;
        }
        return false;
    }

    public function remaining() {
        throw new Exception('TODO: Find what uses this.');
        $tokens = [];
        $token = $this->next();
        while ($token) {
            $tokens[] = $token;
            $token = $this->next();
        }
        return $tokens;
    }

    public function skip() {
        while ($this->peek() !== false && strpos(self::SPACES, $this->peek()) !== false) {
            $this->idx++;
            $this->_debug_print('skip: idx', $this->idx);
        }
        return $this->peek();
    }

    public function take_delim() {
        $delim = $this->skip();
        if (strpos(self::DELIMS, $delim) === false) {
            return false;
        }
        $this->idx++;
        return new TokenDelimiter($delim, $delim);
    }
    
    public function take_newline() {
        $nl = $this->skip();
        //if ($nl !== "\n")
        if (strpos(self::NEWLINES, $nl) === false) {
            return false;
        }
        $this->idx++;
        return new TokenNewline($nl, $nl);
    }

    public function take_number() {
        $test_num = function ($char) {
            $this->_debug_print('take_number: test_num', $char);
            return strpos(self::DIGITS, $char) !== false;
        };
        $build = function (string $text) {
            $this->_debug_print('take_number: build', $text);
            return new TokenNumber((int)$text, $text);
        };
        return $this->take_while($test_num, $build);
    }

    public function take_operator() {
        $test_op = function ($char) {
            //return strpos($this->operators, $char) !== false;
            return in_array($char, explode(' ', self::OPERATORS));
        };
        $build = function (string $text) {
            return new TokenOperator($text, $text);
        };
        return $this->take_while($test_op, $build);
    }

    public function take_string() {
        $open_quote = $this->skip();
        if ($open_quote !== '"') {
            return false;
        }
        $this->idx++;
        $contents = '';
        while ($this->peek() !== false && $this->peek() !== '"') {
            $contents .= $this->peek();
            $this->idx++;
        }
        if ($this->peek() !== '"') {
            throw new Exception("Unmatched quote in string");
        }
        $this->idx++;
        return new TokenString($contents, $contents);
    }

    public function take_symbol() {
        //$test_sym = function ($char) {
        //    return strpos(self::VAR_OTHER, strtoupper($char)) !== false;
        //};
        //$build = function (string $text) {
        //    return new TokenSymbol(strtoupper($text), $text);
        //};
        //return $this->take_while($test_sym, $build);
        // Take one character from var_first
        $first = $this->skip();
        $this->_debug_print('take_symbol: first', $first);
        if ($first === false || strpos(self::VAR_FIRST, strtoupper($first)) === false) {
            $this->_debug_print('take_symbol: abandoning after', $first);
            return false;
        }
        $this->idx++;
        $text = $first;
        // Take any number of characters from var_other
        while ($this->peek() !== false && strpos(self::VAR_OTHER, strtoupper($this->peek())) !== false) {
            $text .= $this->peek();
            $this->idx++;
        }
        return new TokenSymbol(strtoupper($text), $text);
    }

    public function take_until_newline() { # Read <not newlines> until the end of the line
        # Intended for reading everything after a REM,
        # even an empty REM would still have the trailing newline.
        # Because this returns the consumed tokens, it also has to
        # consume the newline.
        $n = $this->next();
        //$this->_debug_print('take_until_newline: n', $n);
        //if ($n === false) {
        //    return false; # must have trailing newline
        //}
        $tokens = [];
        while ($n !== false && !($n instanceof TokenNewline)) {
            $tokens[] = $n;
            $n = $this->next();
        }
        if ($n === false) {
            throw new Exception("Unterminated line");
        }
        return $tokens;
    }

    public function take_while($test, $build) {
        $this->skip();
        if ($this->peek() === false || !$test($this->peek())) {
            return false;
        }
        $token = '';
        while ($this->peek() !== false && $test($this->peek())) {
            $token .= $this->peek();
            $this->_debug_print('take_while: token', $token);
            $this->idx++;
        }
        return $build($token);
    }
}
