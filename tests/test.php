<?php

function filter($items, $fn) {
    return array_values(array_filter($items, $fn));
}

define('TEST_ROOT', __DIR__);
echo "Test root: " . TEST_ROOT . "\n";

// Collect all (other) PHP files in this file's directory
$dir_entries = array_map(function ($entry) {
    return TEST_ROOT . '/' . $entry;
}, scandir(TEST_ROOT));
//print_r($dir_entries);
$files = filter($dir_entries, function ($entry) {
    // To PHP, a "regular file" does not include directories.
    return is_file($entry);
});
//print_r($files);
$php_scripts = filter($files, function ($file) {
    $path_lower = strtolower($file);
    return preg_match('/\.php$/', $path_lower) && $file !== __FILE__;
});
//echo "PHP test scripts:\n";
//print_r($php_scripts);

// Run each test script
try {
    //$results = [];
    foreach ($php_scripts as $script) {
        $relative = basename($script);
        echo "Running $relative\n";

        // Capture output from included file
        ob_start();
        include $script;
        $output = ob_get_clean();
        if (strlen($output) > 0) {
            throw new Exception("Error in $relative: $output");
        }
        //$results[basename($script)] = $output;
    }
    //echo "Results:\n";
    //print_r($results);
    echo "All tests passed!\n";
} catch (Exception $e) {
    echo $e->getMessage(), "\n";
}
