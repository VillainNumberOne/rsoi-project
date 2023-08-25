const frontendUrl = "http://localhost:8010/authorize/"

document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const passwordError = document.getElementById('password-error');
    const signupForm = document.getElementById('signup-form');
    const signupError = document.getElementById('signup-error');

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

    const validatePasswordConfirmation = () => {
        if (passwordInput.value !== confirmPasswordInput.value) {
            showError(passwordError, "Passwords don't match.");
        } else {
            hideError(passwordError);
        }
    };

    passwordInput.addEventListener('input', validatePasswordConfirmation);
    confirmPasswordInput.addEventListener('input', validatePasswordConfirmation);

    signupForm.addEventListener('submit', event => {
        if (passwordInput.value !== confirmPasswordInput.value) {
            event.preventDefault();
            showError(passwordError, "Passwords don't match.");
        }
    });

    // ######################## SIGN UP ###########################

    signupForm.addEventListener('submit', async event => {
        event.preventDefault();
        hideError(signupError); // Hide previous error messages

        const formData = new FormData(signupForm);
        const jsonData = {
            username: formData.get('username'),
            password: formData.get('password'),
            confirm_password: formData.get('confirm_password')
        };

        try {
            const response = await fetch('/api/v1/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(jsonData),
            });

            if (response.status === 201) {
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

                document.body.appendChild(form);
                form.submit();
            } else {
                const errorBody = await response.json();
                showError(signupError, errorBody.error);
            }
        } catch (error) {
            showError(signupError, 'An error occurred. Please try again.');
        }
    });
});
