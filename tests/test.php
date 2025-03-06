<?php

function filter($items, $fn) {
    return array_values(array_filter($items, $fn));
}

$dir_entries = array_map(function ($entry) {
    return __DIR__ . '/' . $entry;
}, scandir(__DIR__));
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

try {
    //$results = [];
    foreach ($php_scripts as $script) {
        echo "Running $script\n";

        // Capture output from included file
        ob_start();
        include $script;
        $output = ob_get_clean();
        if (strlen($output) > 0) {
            throw new Exception("Error in $script: $output");
        }
        //$results[basename($script)] = $output;
    }
    //echo "Results:\n";
    //print_r($results);
    echo "If you're seeing this; all tests passed\n";
} catch (Exception $e) {
    echo $e->getMessage(), "\n";
}
