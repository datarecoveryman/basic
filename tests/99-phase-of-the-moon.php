<?php

// Create a phase-of-the-moon bug
$now = time();

if ($now % 2 == 0) {
    // No output so A.php has nothing to read
    //echo "The moon is full";
} else {
    // Output so A.php has something to read
    echo "The moon is not full";
}
