function showForm(userType) {
    const container = document.getElementById('main-container');
    const form = document.getElementById('login-form');
    const buttonChoice = document.getElementById('button-choice');
    const buttonReturn = document.getElementById('button-return');
    const buttonLogin = document.getElementById('button-loggin');
    const buttonCadastro = document.getElementById('button-cadastro');
    const roleDisplay = document.getElementById('role-display');
    const roleText = document.getElementById('role-text');

    // Esconde as opções iniciais
    if (buttonChoice) {
        buttonChoice.style.display = 'none';
    }

    // Voltar para a tela inicial
    if (userType === 'voltar') {
        form.style.display = 'none';
        buttonReturn.style.display = 'none';
        buttonChoice.style.display = 'flex';
        container.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
        roleDisplay.style.display = 'none';
        return;
    }

    // Define as cores com base no tipo de usuário
    let backgroundColor, buttonColor, cadastroUrl;
    if (userType === 'cliente') {
        backgroundColor = 'rgba(76, 175, 80, 0.2)';
        buttonColor = 'rgba(76, 175, 80)';
        cadastroUrl = 'cadastro_cliente';
        roleDisplay.style.display = 'flex';
        roleText.textContent = 'Cliente';
    } else if (userType === 'restaurante') {
        backgroundColor = 'rgba(33, 150, 243, 0.2)';
        buttonColor = 'rgba(33, 150, 243)';
        cadastroUrl = 'cadastro_restaurante';
        roleDisplay.style.display = 'flex';
        roleText.textContent = 'Restaurante';
    } else if (userType === 'entregador') {
        backgroundColor = 'rgba(255, 152, 0, 0.2)';
        buttonColor = 'rgba(255, 152, 0)';
        cadastroUrl = 'cadastro_entregador';
        roleDisplay.style.display = 'flex';
        roleText.textContent = 'Entregador';
    }

    // Aplica as cores
    container.style.backgroundColor = backgroundColor;
    buttonLogin.style.backgroundColor = buttonColor;
    buttonCadastro.style.backgroundColor = buttonColor;

    // Redireciona para a página de cadastro
    buttonCadastro.onclick = function () {
        window.location.href = cadastroUrl;
    };

    // Mostra o formulário de login
    form.style.display = 'flex';
    buttonReturn.style.display = 'flex';
}
