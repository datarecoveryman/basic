module Main where

import System.IO (hFlush, stdout)
import qualified Data.Map as Map

type LineNumber = Integer
type LineCode = String
--type ProgramLine = (LineNumber, LineCode)
type Program = Map.Map LineNumber LineCode


-- Example program
exampleProgram :: Program
exampleProgram = Map.fromList [(1, "print 'Hello, World!'"), (2, "print 'Goodbye!'")]


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
            "exit!" -> putStrLn "Goodbye!"
            "quit!" -> putStrLn "Goodbye!"
            "help!" -> do
                putStrLn "Available commands: exit!, help!, list!, line!, next!, run!"
                do_nothing
            "list!" -> do
                print_lines $ program_to_strings lines
                do_nothing
            "run!" -> do
                putStrLn "TODO: implement run!"
                do_nothing
            _ -> do
                let new_lines = Map.insert next_line_number line lines
                handle_line (next_line_number + 10) new_lines
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
