<?php

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
    private $delims;
    private $spaces;
    private $newlines;
    private $var_first;
    private $var_other;

    public function __construct(string $text) {
        $this->text = $text;
        $this->idx = 0;
        $this->operators = ["=", "!", "+", "-", "*", "/", "^", "<", ">", "<=", ">=", "==", "<>"];
        $this->delims = "(),";
        $this->digits = "0123456789";
        $this->spaces = " \t";
        $this->newlines = "\n\r";
        $this->var_first = "_ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        $this->var_other = "_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    }

    public function next() {
        $p = $this->skip();
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
        while (strpos($this->spaces, $this->peek()) !== false) {
            $this->idx++;
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
            return strpos($this->digits, $char) !== false;
        };
        $build = function (string $text) {
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
            $this->idx++;
        }
        return $token;
    }
}
