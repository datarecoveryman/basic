module Main where

import System.IO (hFlush, stdout)
import qualified Data.Map as Map

type LineNumber = Integer
type LineCode = String
--type ProgramLine = (LineNumber, LineCode)
type Program = Map.Map LineNumber LineCode


-- Example program
exampleProgram :: Program
exampleProgram = Map.fromList [(10, "print 'Hello, World!'"), (20, "print 'Goodbye!'")]


print_lines :: [String] -> IO ()
print_lines [] = return ()
print_lines (x:xs) = do
    putStrLn x
    print_lines xs

-- Program lines in just whatever order; no idea, maybe random.
-- I think they're randomized in Swift, lol.
program_to_strings :: Program -> [String]
program_to_strings p = "Listing program lines:" : lines_fkin_however
    where
        lines_fkin_however = (map lineString $ Map.toList p)
        lineString :: (LineNumber, LineCode) -> String
        lineString (k, v) = show k ++ ": " ++ v

-- Program lines in line-number order.
program_strings_sorted :: Program -> [String]
program_strings_sorted p = "Listing program lines: " : lines_sorted
    where
        lines_sorted = map lineString $ Map.toAscList p
        lineString :: (LineNumber, LineCode) -> String
        lineString (k, v) = show k ++ ": " ++ v

read_line_number :: LineNumber -> [String] -> LineNumber
read_line_number fallback_number tokens =
    if null tokens
        then fallback_number
        else read (head tokens)

handle_line :: LineNumber -> Program -> IO ()
handle_line next_line_number lines = do
    -- prompt the user for a string
    putStr "> "
    hFlush stdout -- flush the output buffer so we get the prompt immediately
    line <- getLine
    let tokens = words line
    -- check if the first token is a command
    if null tokens
        then handle_line next_line_number lines
        else case head tokens of
            "exit!" -> return () --putStrLn "Goodbye!"
            "quit!" -> return () --putStrLn "Goodbye!"
            "help!" -> do
                putStrLn "Available commands: exit!, help!, list!, line!, next!, run!"
                do_nothing
            "list!" -> do
                --print_lines $ program_to_strings lines
                print_lines $ program_strings_sorted lines
                do_nothing
            "next!" -> do
                putStrLn $ "Next line number: " ++ (show next_line_number)
                do_nothing
            "run!" -> do
                putStrLn "TODO: implement run!"
                do_nothing
            _ -> do
                --putStrLn "About to add a line; use the line number, if given."
                let line_words = words line
                --putStrLn (show line_words)
                let line_number = read_line_number (next_line_number + 10) line_words
                --putStrLn $ "Line number: " ++ (show line_number)
                let line_remaining = unwords (tail line_words)
                let new_lines = Map.insert line_number line_remaining lines
                putStrLn $ "Stored line " ++ (show line_number) ++ ": " ++ line_remaining
                handle_line (line_number + 10) new_lines
    where
        do_nothing = handle_line next_line_number lines

main :: IO ()
main = do
    putStrLn "Hello. Commands end with ! so try help! or quit! to exit!"
    --putStrLn "Here is an example program:"
    --print_lines $ program_to_strings exampleProgram
    --print_lines $ program_to_strings new_program
    handle_line initial_line_number initial_program
    where
        new_program = Map.insert 20 "goto 10" exampleProgram
        initial_line_number = 10
        initial_program = Map.empty
