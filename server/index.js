
const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const port = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public/index.html');
});

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    // Burada giriş doğrulaması yapın
    res.send('Giriş Başarılı');
});

app.post('/send-message', (req, res) => {
    const { message } = req.body;
    // Burada mesajı kaydedin
    res.send('Mesaj Gönderildi');
});

app.listen(port, () => {
    console.log(`Server started on http://localhost:${port}`);
});
