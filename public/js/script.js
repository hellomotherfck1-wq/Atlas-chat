document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    // Burada giriş işlemi yapın
    alert(`Giriş Yaptınız: ${username}`);
});

document.getElementById('sendButton').addEventListener('click', function() {
    const message = document.getElementById('messageInput').value;
    if (message) {
        // Burada mesajı gönderin
        document.getElementById('messages').innerHTML += `<p>${message}</p>`;
        document.getElementById('messageInput').value = '';
    }
});
