<?php

$request_body = file_get_contents('php://input');
$data = json_decode($request_body,TRUE);
$url = $data['url'];

$payload = http_build_query([
  'sessionId' => $data['sessionId'],
  'serviceCode' => $data['serviceCode'],
  'phoneNumber' => $data['phoneNumber'],
  'text' => $data['text']
]);


$ch = curl_init($url);
curl_setopt($ch, CURLOPT_POST, TRUE);
curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);

$response = curl_exec($ch);
curl_close($ch);

$action = substr($response,0,3);
$text = substr($response,4);

header('Content-Type: application/json');
echo json_encode( [ 'action' => $action , 'text' => $text ]);

?>
