<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Get form data
    $name = $_POST['name'];
    $email = $_POST['email'];
    $message = $_POST['message'];

    // Email recipient
    $to = "Sales@arizosecure.com";

    // Email subject
    $subject = "New message from $name";

    // Email content
    $email_content = "Name: $name\n";
    $email_content .= "Email: $email\n\n";
    $email_content .= "Message:\n$message\n";

    // Email headers
    $headers = "From: $name <$email>";

    // Send email
    if (mail($to, $subject, $email_content, $headers)) {
        echo "Message sent successfully.";
    } else {
        echo "Failed to send message. Please try again later.";
    }
} else {
    // If not a POST request, redirect back to the contact page
    header("Location: contact.html");
}
?>
