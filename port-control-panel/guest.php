<?php
// Handle the form submission
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // If the switch is turned on
    if (isset($_POST["switch"]) && $_POST["switch"] == "on") {
        // Execute iptables command to enable guest network isolation
        exec("sudo iptables -A FORWARD -i eth1 -o eth0 -j DROP");
        echo "Guest network isolation enabled.";
    } else {
        // Execute iptables command to disable guest network isolation
        exec("sudo iptables -D FORWARD -i eth1 -o eth0 -j DROP");
        echo "Guest network isolation disabled.";
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Guest Network Control</title>
</head>
<body>
    <h1>Guest Network Control</h1>
    <form method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>">
        <label for="switch">Guest Network Isolation:</label>
        <input type="checkbox" id="switch" name="switch" value="on">
        <input type="submit" value="Save">
    </form>
</body>
</html>

