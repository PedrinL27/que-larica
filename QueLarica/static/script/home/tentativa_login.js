document.addEventListener('DOMContentLoaded', () => {
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const errorMessage = document.getElementById('login-error');
    const closeErrorBtn = document.getElementById('close-error');
    const errorText = document.getElementById('error-text');
    const loginButton = document.getElementById('button-loggin');

    function hideError() {
        if (errorMessage && errorMessage.style.display !== 'none') {
            errorMessage.style.display = 'none';
        }
    }

    if (closeErrorBtn) {
        closeErrorBtn.addEventListener('click', hideError);
    }

    if (emailInput && passwordInput) {
        emailInput.addEventListener('input', hideError);
        passwordInput.addEventListener('input', hideError);
    }

    loginButton.addEventListener('click', function () {
        const email = emailInput.value;
        const password = passwordInput.value;

        let userType = '';
        const container = document.getElementById('main-container');
        const bgColor = container.style.backgroundColor;

        if (bgColor.includes('76, 175, 80')) userType = 'cliente';
        else if (bgColor.includes('33, 150, 243')) userType = 'restaurante';
        else if (bgColor.includes('255, 152, 0')) userType = 'entregador';

        fetch('/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, userType })
        })
        .then(response => response.json().then(data => ({ status: response.status, body: data })))
        .then(({ status, body }) => {
            if (body.success) {
                window.location.href = body.redirect_url;
            } else {
                if (errorMessage && errorText) {
                    errorText.textContent = body.message || "Erro desconhecido.";
                    errorMessage.style.display = 'flex';
                }
            }
        })
        .catch(error => {
            console.error('Erro no login:', error);
            if (errorMessage && errorText) {
                errorText.textContent = "Erro ao conectar com o servidor.";
                errorMessage.style.display = 'flex';
            }
        });
    });
});
