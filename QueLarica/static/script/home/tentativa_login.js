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

    [emailInput, passwordInput].forEach(input => {
        input.addEventListener('keypress', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                loginButton.click();
            }
        });
    });

    loginButton.addEventListener('click', function () {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        // Determina o tipo de usuário pelo background color do container
        let userType = '';
        const container = document.getElementById('main-container');
        const bgColor = container.style.backgroundColor;

        if (bgColor.includes('76, 175, 80')) userType = 'cliente';
        else if (bgColor.includes('33, 150, 243')) userType = 'restaurante';
        else if (bgColor.includes('255, 152, 0')) userType = 'entregador';

        // Verifica se os campos estão preenchidos
        if (!email || !password) {
            alert('Por favor, preencha todos os campos.');
            return;
        }

        // Envia os dados para o backend
        fetch('/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, userType })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redireciona para o dashboard do usuário
                window.location.href = data.redirect_url;
            } else {
                alert(data.message || 'Erro no login.');
            }
        })
        .catch(error => console.error('Erro ao fazer login:', error));
    });
});


