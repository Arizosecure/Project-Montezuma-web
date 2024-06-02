const express = require('express');
const nodemailer = require('nodemailer');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;

// Use body-parser to parse JSON bodies
app.use(bodyParser.json());

// In-memory store for simplicity (Use a database in production)
const verificationCodes = {};

// Nodemailer transporter (configure with your email service)
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: 'your-email@gmail.com',
        pass: 'your-email-password'
    }
});

app.post('/send_verification_code', (req, res) => {
    const { email } = req.body;
    const verificationCode = Math.floor(100000 + Math.random() * 900000).toString();
    
    verificationCodes[email] = verificationCode;

    const mailOptions = {
        from: 'your-email@gmail.com',
        to: email,
        subject: 'Your Verification Code',
        text: `Your verification code is: ${verificationCode}`
    };

    transporter.sendMail(mailOptions, (error, info) => {
        if (error) {
            console.log(error);
            return res.json({ success: false });
        } else {
            console.log('Email sent: ' + info.response);
            return res.json({ success: true });
        }
    });
});

app.post('/verify_code', (req, res) => {
    const { email, code } = req.body;
    if (verificationCodes[email] && verificationCodes[email] === code) {
        delete verificationCodes[email]; // Clear the code after successful verification
        return res.json({ success: true });
    } else {
        return res.json({ success: false });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
