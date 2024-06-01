document.getElementById('signOnForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/api/signon', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    });

    const result = await response.json();

    if (result.success) {
        document.getElementById('message').style.color = 'green';
        document.getElementById('message').textContent = 'Sign-on successful! Check your email for the verification code.';
    } else {
        document.getElementById('message').textContent = result.message;
    }
});
