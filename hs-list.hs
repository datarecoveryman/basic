
module Main where

import System.IO (hFlush, stdout)

-- type for a line, made of a line number and a code string
type Line = (Int, String)

type Program = [Line]

print_program :: Program -> IO ()
print_program lines = do
    putStrLn "Listing program lines:"
    print_lines lines

print_line :: Line -> IO ()
print_line (line_number, line_string) = do
    putStrLn $ show line_number ++ ": " ++ line_string

print_lines :: [Line] -> IO ()
print_lines [] = return ()
print_lines (line:lines) = do
    print_line line
    print_lines lines

handle_quit :: IO ()
handle_quit = putStrLn "Goodbye!"

handle_help :: IO ()
handle_help = putStrLn "Available commands: exit!, help!, list!, line!, next!, run!"

handle_line :: Int -> [Line] -> IO ()
handle_line next_line_number lines = do
    -- prompt the user for a string
    putStr "> "
    hFlush stdout -- flush the output buffer so we get the prompt immediately
    line <- getLine
    --putStrLn $ "You entered: " ++ line
    let tokens = words line
    --putStrLn $ "Tokens: " ++ show tokens
    -- check if the first token is a command
    if null tokens
        then handle_line next_line_number lines
        else case head tokens of
            "exit!" -> handle_quit
            "quit!" -> handle_quit
            "help!" -> do
                handle_help
                handle_line next_line_number lines
            "list!" -> do
                print_program lines
                handle_line next_line_number lines
            _ -> do
                putStrLn $ "Tokens: " ++ show tokens
                -- add the line to the list of lines
                --let new_lines = (next_line_number, line) : lines
                let new_lines = lines ++ [(next_line_number, line)]
                putStrLn $ "New lines: " ++ show new_lines
                handle_line (next_line_number + 10) new_lines

main :: IO ()
main = do
    putStrLn "Hello. Commands end with ! so try help! or quit! to exit!"
    let initial_lines = []
    let first_line_number = 10
    handle_line first_line_number initial_lines
