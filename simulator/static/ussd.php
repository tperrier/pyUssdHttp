<?php

// Reads the variables sent via POST from our gateway
$sessionId   = $_POST["sessionId"];
$serviceCode = $_POST["serviceCode"];
$phoneNumber = $_POST["phoneNumber"];
$text        = $_POST["text"];

if ( $text == "" ) {
    // This is the first request. Note how we start the response with CON
    $response  = "CON Select One\n";
    $response .= "1. POST Vars\n";
    $response .= "2. Help";
} else if ( $text == "1" ) {
    $response = "END ";
    foreach( $_POST as $key => $value) {
        $response .= "$key => $value\n";
    }
} else if ( $text == "2") {
    $response = "END help: verb (used with object) \n";
    $response .= "to be useful or profitable to:\n";
    $response .= "Her quick mind helped her career.";
}

// Print the response onto the page so that our gateway can read it
header('Content-type: text/plain');
echo $response;

?>
