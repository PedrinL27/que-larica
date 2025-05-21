function showForm(userType) {
    const container = document.getElementById('main-container');
    const form = document.getElementById('login-form');
    const buttonChoice = document.getElementById('button-choice');
    const buttonReturn = document.getElementById('button-return');
    const buttonLogin = document.getElementById('button-loggin');
    const buttonCadastro = document.getElementById('button-cadastro');
    const roleDisplay = document.getElementById('role-display');
    const roleText = document.getElementById('role-text');

    // Função auxiliar para aplicar transição suave de cor
    function changeBackgroundColor(color) {
        container.style.transition = 'background-color 0.7s ease';
        requestAnimationFrame(() => {
            container.style.backgroundColor = color;
        });
    }

    // Voltar para a tela inicial
    if (userType === 'voltar') {
        form.style.display = 'none';
        buttonReturn.style.display = 'none';
        buttonChoice.style.display = 'flex';
        roleDisplay.style.display = 'none';

        changeBackgroundColor('rgba(255, 255, 255, 0.2)');
        return;
    }

    // Oculta as opções iniciais
    buttonChoice.style.display = 'none';

    // Define cores e texto com base no tipo de usuário
    let backgroundColor, buttonColor, cadastroUrl;
    if (userType === 'cliente') {
        backgroundColor = 'rgba(76, 175, 80, 0.2)';
        buttonColor = 'rgba(76, 175, 80)';
        cadastroUrl = 'cadastro_cliente';
        roleText.textContent = translations.cliente;
    } else if (userType === 'restaurante') {
        backgroundColor = 'rgba(33, 150, 243, 0.2)';
        buttonColor = 'rgba(33, 150, 243)';
        cadastroUrl = 'cadastro_restaurante';
        roleText.textContent = translations.restaurante;
    } else if (userType === 'entregador') {
        backgroundColor = 'rgba(255, 152, 0, 0.2)';
        buttonColor = 'rgba(255, 152, 0)';
        cadastroUrl = 'cadastro_entregador';
        roleText.textContent = translations.entregador;
    }

    // Aplica cores com suavidade
    changeBackgroundColor(backgroundColor);
    buttonLogin.style.backgroundColor = buttonColor;
    buttonCadastro.style.backgroundColor = buttonColor;

    // Atualiza evento de cadastro
    buttonCadastro.onclick = () => window.location.href = cadastroUrl;

    // Mostra o formulário e botões
    form.style.display = 'flex';
    buttonReturn.style.display = 'flex';
    roleDisplay.style.display = 'flex';
}
