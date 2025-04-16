
# 📦 Que Larica!

Um sistema de delivery completo, desenvolvido com **Flask**, que permite o cadastro e gerenciamento de pedidos, integração de clientes, restaurantes e entregadores.

## 🚀 Funcionalidades

- **Clientes**:
  - Cadastro de conta.
  - Adição de produtos ao carrinho.
  - Acompanhamento de pedidos realizados.

- **Restaurantes**:
  - Cadastro de conta.
  - Cadastro e gerenciamento de produtos.
  - Visualização de pedidos recebidos.

- **Entregadores**:
  - Cadastro de conta.
  - Visualização de pedidos pendentes para entrega.
  - Atualização do status de pedidos.

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS
- **Banco de Dados**: SQLite


## 🗂️ Estrutura do Projeto

### `database/`
Esta pasta contém todos a base de dados armazenada localmente do projeto

### `static/`
Esta pasta contém todos os arquivos estáticos do projeto, como CSS, JavaScript e imagens.

- **img/**: Imagens utilizadas na interface da aplicação.
- **styles/**: Arquivos de estilo CSS para a aplicação.
- **scripts/**: Scripts JavaScript utilizados para funcionalidades interativas.
- **uploads/**: Uploads de imagens do usuário.

### `templates/`
Aqui ficam os arquivos HTML da aplicação, divididos por diferentes áreas (cliente, restaurante, entregador) para melhor organização.

- **cliente/**: Templates específicos para a interface do cliente.
- **restaurante/**: Templates específicos para a interface do restaurante.
- **entregador/**: Templates específicos para a interface do entregador.
- **home/**: Templates base, utilizado como estrutura comum entre as páginas.
### `app.py`
Este é o ponto onde contém todo o Backend da aplicação.
## ⚙️ Como Rodar o Projeto

1. Clone o repositório:

   ```bash
   git clone https://github.com/PedrinL27/que-larica

2. Crie e ative o ambiente virtual:
    ```bash
    python -m venv venv
    venv\Scripts\activate
3. Instale as dependências
4. Configure o banco de dados:
    ```bash
    flask db upgrade
5. Inicie o servidor local:
    ```bash
    python -m flask run
6. Acesse o sistema:
- Abra o navegador e vá para http://127.0.0.1:5000

## 🤝 Contribuindo
Contribuições são sempre bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.
