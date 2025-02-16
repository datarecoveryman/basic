module Main where

import qualified Data.Map as Map

type LineNumber = Integer
type LineCode = String
type Program = Map.Map LineNumber LineCode
type Vars = Map.Map String Integer

print_lines :: [String] -> IO ()
print_lines [] = return ()
print_lines (x:xs) = do
    putStrLn x
    print_lines xs

-- Program lines in line-number order.
program_strings_sorted :: Program -> [String]
program_strings_sorted p = "Listing program lines: " : lines_sorted
    where
        lines_sorted = map lineString $ Map.toAscList p
        lineString :: (LineNumber, LineCode) -> String
        lineString (k, v) = show k ++ ": " ++ v

testProgram1 :: Program
testProgram1 = Map.fromList [
    (10, "LET X = 5"),
    (15, "REM This is a comment"),
    (20, "PRINT X"),
    (40, "GOTO 20")
    ]

interp1 :: Integer -> Program -> Vars -> IO Integer
interp1 max_ops program vars = do
    --let (result, remaining_ops) = runProgram max_ops program vars 10
    --print result
    -- TODO: implement the interpreter
    let remaining_ops = max_ops
    return remaining_ops

main :: IO ()
main = do
    putStrLn "Given a program like testProgram1, run it for up to max_ops operations."
    --print testProgram1
    print_lines $ program_strings_sorted testProgram1
    putStrLn "Running program..."
    remaining_ops <- interp1 max_ops testProgram1 initial_vars
    putStrLn $ "Program finished; remaining ops: " ++ show remaining_ops
    where
        max_ops = 10
        initial_vars = Map.empty
