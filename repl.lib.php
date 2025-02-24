<?php

abstract class Code {
    protected $line_number;
    protected $statement;

    public function __construct($line_number) {
        $this->line_number = $line_number;
    }

    public function __toString() {
        return $this->line_number . ':' . get_class($this) . "()";
    }
}

class CodeAssignment extends Code {
    protected $variable;
    protected $expression;
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
    protected $target;
    public function __construct($line_number, $target) {
        parent::__construct($line_number);
        $this->target = $target;
    }
    public function __toString() {
        return $this->line_number . ':' . get_class($this) . "($this->target)";
    }
}

class CodePrint extends Code {
    protected $expression;
    public function __construct($line_number, $expression) {
        parent::__construct($line_number);
        $this->expression = $expression;
    }
    public function __toString() {
        return $this->line_number . ':' . get_class($this) . "($this->expression)";
    }
}

class Expression {
    protected $expr;
    public function __construct($expr) {
        $this->expr = $expr;
    }
    public function __toString() {
        return get_class($this) . "($this->expr)";
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

    private function _debug_print(...$msg) {
        if ($this->debug) {
            foreach ($msg as $m) {
                echo $m . " ";
            }
            echo "\n";
        }
    }
    
    public function all() {
        $statements = [];
        $stmt = $this->take_statement();
        while ($stmt !== null) {
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
        if ($line_number_token === null) {
            // No start, no statement
            return null;
        }
        $line_number = $line_number_token->value;
        $this->_debug_print("Line number:", $line_number);
        $verb = $this->tokens->take_symbol();
        if ($verb === null) {
            throw new Exception("Expected verb");
        }
        $this->_debug_print("Verb:", $verb);
        $code = null;
        if ($verb->value == "GOTO") {
            # GOTO 123
            $target_line_number = $this->tokens->take_number();
            if ($target_line_number === null) {
                throw new Exception("Expected line number after GOTO");
            }
            $this->_debug_print("GOTO line number:", $target_line_number);
            $code = new CodeGoto($line_number, $target_line_number);
        } elseif ($verb->value == "LET") {
            // LET X = 5
            $var = $this->tokens->take_symbol();
            if ($var === null) {
                throw new Exception("Expected variable after LET");
            }
            $this->_debug_print("LET variable:", $var);
            $equals = $this->tokens->take_operator();
            if ($equals === null || $equals->value != "=") {
                throw new Exception("Expected = after variable in LET");
            }
            $this->_debug_print("LET equals:", $equals);
            $expr = $this->take_expression();
            $code = new CodeAssignment($line_number, $var->value, $expr);
        } elseif ($verb.value == "PRINT") {
            # PRINT "Hello"
            $expr = $this->take_expression();
            $code = new CodePrint($line_number, $expr);
        } elseif ($verb.value == "REM") {
            // REM anything "is fine" here
            $comment_tokens = $this->tokens->take_until_newline();
            $this->_debug_print("take_until_newline:", $comment_tokens);
            if ($comment_tokens === null) {
                throw new Exception("Expected string after REM");
            }
            $this->_debug_print("REM comment:", $comment_tokens);
            // I don't like putting token/string processing in here.
            // Leave that to CodeNoop.
            $code = new CodeNoop($line_number, $comment_tokens);
        } else {
            throw new Exception("Unknown verb: " . (string)$verb);
        }
        if ($verb->value != "REM") {
            $newline = $this->tokens->take_newline();
            if ($newline === null) {
                throw new Exception("Expected trailing newline");
            }
        }
        return $code;
    }

    public function take_expression() {
        return $this->parse_expression();
    }

    public function get_precedence($token) {
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
    
    public function parse_primary() {
        $first = $this->tokens->skip();
        $this->_debug_print("parse_primary: first:", $first);
        // the "primary" in an expression can be a number, a variable,
        // a string, or a parenthesized expression (recursive).
        // But, with multiple options, the "demanding" approach has
        // to be flexible.
        $n = $this->tokens->next();
        $this->_debug_print("Next token:", $n);
        if ($n instanceof TokenString) {
            $this->_debug_print("parse_primary: string:", $n);
            return new Expression($n);
        }
        if ($n instanceof TokenNumber || $n instanceof TokenSymbol) {
            $this->_debug_print("parse_primary: number/symbol:", $n);
            return new Expression($n);
        }
        if ($n instanceof TokenDelimiter && $n->value == '(') {
            $expr = $this->parse_expression();
            $closing_paren = $this->tokens->take_delimiter();
            if (!($closing_paren instanceof TokenDelimiter) || $closing_paren->value != ')') {
                throw new Exception("Expected closing parenthesis");
            }
            return $expr;
        }
        throw new Exception("Unexpected token: " . str($n));
    }

    public function parse_expression($precedence = 0) {
        $left_expr = $this->parse_primary();
        while (true) {
            // parse_expression() always creates a left_expr, the first term.
            $this->_debug_print("left_expr: " . $left_expr);
            $peek = $this->tokens->peek();
            $this->_debug_print("peek: " . $peek);
            if ($peek === null) {
                throw new Exception("Expected operator or newline, got None");
            }
            if ($peek === "\n") {
                $this->_debug_print("parse_expression: found newline, ending expression");
                break;
            }
            $op = $this->tokens->take_operator();
            if ($op === null) {
                throw new Exception("Expected operator, got " . $peek);
            }
            $this->_debug_print("parse_expression: operator: " . $op);
            $op_precedence = $this->get_precedence($op);
            if ($op_precedence < $precedence) {
                break;
            }
            $right_expr = $this->parse_expression($op_precedence + 1);
            $left_expr = new Expression([$op, $left_expr, $right_expr]);
        }
        return $left_expr;
    }
}

abstract class Token {
    protected $value;
    protected $original;

    public function __construct($value, $original) {
        $this->value = $value;
        $this->original = $original;
    }

    public function __toString() {
        $value = is_string($this->value) ? '"' . $this->value . '"' : $this->value;
        return get_class($this) . "($value, $this->original)";
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
}
class TokenOperator extends Token {
}
class TokenSymbol extends Token {
}
class TokenString extends Token {
}

class TokenStreamSkippy {
    private $text;
    private $idx;
    private $operators;
    private $debug;
    private $delims;
    private $digits;
    private $spaces;
    private $newlines;
    private $var_first;
    private $var_other;

    public function __construct(string $text, $debug = false) {
        $this->text = $text;
        $this->idx = 0;
        $this->operators = ["=", "!", "+", "-", "*", "/", "^", "<", ">", "<=", ">=", "==", "<>"];
        $this->delims = "(),";
        $this->digits = "0123456789";
        $this->spaces = " \t";
        $this->newlines = "\n\r";
        $this->var_first = "_ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        $this->var_other = "_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
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
        $this->_debug_print('p', $p);
        if ($p === false) {
            return false;
        }
        // Guess based off the first non-space character
        if (strpos($this->newlines, $p) !== false) {
            return $this->take_newline();
        }
        if ($p === '"') {
            return $this->take_string();
        }
        if (strpos($this->digits, $p) !== false) {
            return $this->take_number();
        }
        if (strpos($this->delims, $p) !== false) {
            return $this->take_delim();
        }
        if (in_array($p, $this->operators)) {
            return $this->take_operator();
        }
        if (strpos($this->var_first, $p) !== false) {
            return $this->take_symbol();
        }
        throw new Exception("Unexpected character: $p");
    }

    public function peek() {
        if ($this->idx < mb_strlen($this->text)) {
            $ret = mb_substr($this->text, $this->idx, 1);
            if (mb_strlen($ret) < 1) {
                throw new Exception("Peek expected to be able to return a character; bad idx math?");
            }
            return $ret;
        }
        return false;
    }

    public function remaining() {
        $tokens = [];
        $token = $this->next();
        while ($token) {
            $tokens[] = $token;
            $token = $this->next();
        }
        return $tokens;
    }

    public function skip() {
        while ($this->peek() !== false && strpos($this->spaces, $this->peek()) !== false) {
            $this->idx++;
            $this->_debug_print('skip: idx', $this->idx);
        }
        return $this->peek();
    }

    public function take_delim() {
        $delim = $this->skip();
        if (strpos($this->delims, $delim) === false) {
            return false;
        }
        $this->idx++;
        return new TokenDelimiter($delim, $delim);
    }
    
    public function take_newline() {
        $nl = $this->skip();
        if ($nl !== "\n") {
            return false;
        }
        $this->idx++;
        return new TokenNewline($nl, $nl);
    }

    public function take_number() {
        $test_num = function ($char) {
            $this->_debug_print('take_number: test_num', $char);
            return strpos($this->digits, $char) !== false;
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
            return in_array($char, $this->operators);
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
        $test_sym = function ($char) {
            return strpos($this->var_other, $char) !== false;
        };
        $build = function (string $text) {
            return new TokenSymbol(strtoupper($text), $text);
        };
        return $this->take_while($test_sym, $build);
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
