<!DOCTYPE html>
<html>
<body>
<a href="http://www.breakoutbros.com">
    <img src="logo.png" alt="BreakoutBros" style="width:640px;height:225px;">
</a>
<p>
<h2>
<?php echo 'Dryer status: '; ?>
<?php
$status_file_name = "/home/pi/dev/vibration_kookye/python/dryer_status.txt";
# $myfile = fopen("/home/pi/dev/vibration_kookye/dryer_status.txt", "r") or die("Unable to open file!");
# echo fread($myfile,filesize("/home/pi/dev/vibration_kookye/dryer_status.txt"));
echo nl2br(file_get_contents($status_file_name));
?>
</h2>
</body>
</html>
