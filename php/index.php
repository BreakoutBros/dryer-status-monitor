<!DOCTYPE html>
<html>
<body>
<a href="http://www.breakoutbros.com">
    <img src="logo.png" alt="BreakoutBros" style="width:640px;height:225px;">
</a>
<p>
<h2>
<?php
$status_file_name = "/home/pi/dev/vibration_kookye/python/dryer_status.txt";
echo nl2br(file_get_contents($status_file_name));
?>
</h2>
</body>
</html>
