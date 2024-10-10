// script.js

document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const outputDiv = document.getElementById('output');

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent the default form submission

        const formData = new FormData(form);
        const uploadURL = '/upload';

        fetch(uploadURL, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                outputDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            } else {
                const { transcribed_text, questions_and_answers, file_length } = data.response;
                outputDiv.innerHTML = `
                    <h3>Transcribed Text:</h3>
                    <p>${transcribed_text}</p>
                    <h3>Generated Questions and Answers:</h3>
                    <pre>${questions_and_answers}</pre>
                    <h3>File Length: ${file_length.toFixed(2)} seconds</h3>
                `;
            }
        })
        .catch(error => {
            outputDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        });
    });
});
