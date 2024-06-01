const express = require('express');
const nodemailer = require('nodemailer');
const bodyParser = require('body-parser');
const app = express();
const port = 3000;

app.use(bodyParser.json());
app.use(express.static('public'));

// Simulate user database
let users = [];

app.post('/api/signon', async (req, res) => {
    const { email, password } = req.body;

    // Simple validation
    if (!email || !password) {
        return res.json({ success: false, message: 'Email and password are required' });
    }

    // Check if user exists
    const user = users.find(user => user.email === email);

    if (user) {
        return res.json({ success: false, message: 'User already exists' });
    }

    // Simulate saving user to the database
    const verificationCode = Math.floor(100000 + Math.random() * 900000).toString(); // 6-digit code
    users.push({ email, password, verificationCode });

    // Send verification email
    const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
            user: 'your-email@gmail.com',
            pass: 'your-email-password'
        }
    });

    const mailOptions = {
        from: 'your-email@gmail.com',
        to: email,
        subject: 'Email Verification',
        text: `Your verification code is ${verificationCode}`
    };

    try {
        await transporter.sendMail(mailOptions);
        res.json({ success: true, message: 'Verification email sent' });
    } catch (error) {
        res.json({ success: false, message: 'Failed to send verification email' });
    }
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
