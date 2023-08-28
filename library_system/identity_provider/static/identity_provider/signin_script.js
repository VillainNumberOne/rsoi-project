const frontendUrl = "http://localhost:8010/authorize/"

document.addEventListener('DOMContentLoaded', () => {
    const signinForm = document.getElementById('signin-form');
    const signinError = document.getElementById('signin-error');

    // show error message
    const showError = (element, message) => {
        element.textContent = message;
        element.style.display = 'block';
    };

    // hide error message
    const hideError = element => {
        element.textContent = '';
        element.style.display = 'none';
    };

    // ######################## SIGN IN ###########################

    signinForm.addEventListener('submit', async event => {
        event.preventDefault();
        hideError(signinError); // Hide previous error messages

        const formData = new FormData(signinForm);
        const jsonData = {
            username: formData.get('username'),
            password: formData.get('password'),
        };

        try {
            const response = await fetch('/api/v1/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jsonData),
            });

            if (response.status === 200) {
                const responseBody = await response.json();

                const form = document.createElement('form');
                form.method = 'post';
                form.action = frontendUrl;

                const accessTokenInput = document.createElement('input');
                accessTokenInput.type = 'hidden';
                accessTokenInput.name = 'id_token';
                accessTokenInput.value = responseBody.id_token;
                form.appendChild(accessTokenInput);

                const refreshTokenInput = document.createElement('input');
                refreshTokenInput.type = 'hidden';
                refreshTokenInput.name = 'refresh_token';
                refreshTokenInput.value = responseBody.refresh_token;
                form.appendChild(refreshTokenInput);

                const usernameInput = document.createElement('input');
                usernameInput.type = 'hidden';
                usernameInput.name = 'username';
                usernameInput.value = jsonData.username;
                form.appendChild(usernameInput);

                document.body.appendChild(form);
                form.submit();
            } else {
                const errorBody = await response.json();
                showError(signinError, errorBody.error);
            }
        } catch (error) {
            showError(signinError, 'An error occurred. Please try again.');
        }
    });
});
