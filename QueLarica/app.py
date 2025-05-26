from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_babel import Babel, get_locale
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_25'

# Configuração do Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'pt'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

# Define qual idioma usar com base na sessão
def get_locale():
    return session.get('lang', 'pt')

# Cria o Babel passando a função get_locale
babel = Babel(app, locale_selector=get_locale)

# Injeta o idioma atual nos templates
@app.context_processor
def inject_locale():
    return dict(current_locale=session.get('lang', 'pt'))

# Rota para definir idioma
@app.route('/set_language', methods=['POST'])
def set_language():
    lang = request.form.get('language')
    session['lang'] = lang
    return redirect(request.referrer)


# Configuração do banco de dados SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'database', 'delivery.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'check_same_thread': False}
}

# Configuração do uploads de imagem
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Inicializa a extensão SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Criacao das tabelas do banco de dados
class Restaurante(db.Model):
    __tablename__ = 'restaurantes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(50), nullable=False)
    cnpj = db.Column(db.String(20), nullable=False, unique=True)
    endereco = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Boolean, default=False) 
    produtos = db.relationship('Produto', back_populates='restaurante', lazy=True)
    fotoperfil = db.Column(db.String(200), nullable=True)
    
    @hybrid_property
    def media_avaliacoes(self):
        avaliacoes = [pedido.avaliacao for pedido in self.pedidos if pedido.avaliacao]
        if avaliacoes:
            return sum(avaliacoes) / len(avaliacoes)
        return 0

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(50), nullable=False)
    cpf = db.Column(db.String(15), nullable=False, unique=True)
    endereco = db.Column(db.String(100), nullable=False)

class Entregador(db.Model):
    __tablename__ = 'entregadores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(50), nullable=False)
    cpf = db.Column(db.String(15), nullable=False, unique=True)
    status = db.Column(db.Boolean, default=False)  # False para disponível, True para ocupado

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(255), nullable=True)
    restaurante_id = db.Column(db.Integer, db.ForeignKey('restaurantes.id', name='fk_produto_restaurante'), nullable=False)
    restaurante = db.relationship('Restaurante', back_populates='produtos')

class Carrinho(db.Model):
    __tablename__ = 'carrinhos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id', name='fk_carrinho_cliente'), nullable=False)
    cliente = db.relationship('Cliente', backref='carrinhos')
    total = db.Column(db.Float, default=0.0)

class ItemCarrinho(db.Model):
    __tablename__ = 'itens_carrinho'
    id = db.Column(db.Integer, primary_key=True)
    carrinho_id = db.Column(db.Integer, db.ForeignKey('carrinhos.id', name='fk_item_carrinho_carrinho'), nullable=False)
    carrinho = db.relationship('Carrinho', backref='itens')
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id', name='fk_item_carrinho_produto'), nullable=False)
    produto = db.relationship('Produto', backref='itens_carrinho')
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    subtotal = db.Column(db.Float, nullable=False)
    
class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    restaurante_id = db.Column(db.Integer, db.ForeignKey('restaurantes.id'), nullable=False)
    entregador_id = db.Column(db.Integer, db.ForeignKey('entregadores.id'), nullable=True)
    status = db.Column(db.String(20), default="Aguardando Confirmação")  
    data_pedido = db.Column(db.DateTime, default=datetime.now)
    avaliacao = db.Column(db.Integer) 
    forma_pagamento = db.Column(db.String(20), nullable=True)
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)
    cliente = db.relationship('Cliente', backref='pedidos')
    restaurante = db.relationship('Restaurante', backref='pedidos')
    entregador = db.relationship('Entregador', backref='pedidos')

class ItemPedido(db.Model):
    __tablename__ = 'itens_pedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

# Comando para criar as tabelas no banco de dados
with app.app_context():
   db.create_all()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('home'))  # Redireciona para a tela de login
        return f(*args, **kwargs)
    return decorated_function

#Rota principal
@app.route("/", methods=['GET', 'POST'])
def home():
    
    if 'user_id' in session:
        user_type = session.get('user_type')
        if user_type == 'cliente':
            return redirect(url_for('dashboard_cliente'))
        elif user_type == 'restaurante':
            return redirect(url_for('dashboard_restaurante'))
        elif user_type == 'entregador':
            return redirect(url_for('dashboard_entregador'))
        
    if request.method == 'POST':
        
        data = request.json  # Recebe os dados do JavaScript (JSON)
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('userType')  # 'cliente', 'restaurante' ou 'entregador'
        
        user = None
        if user_type == 'cliente':
            user = Cliente.query.filter_by(email=email, senha=password).first()
        elif user_type == 'restaurante':
            user = Restaurante.query.filter_by(email=email, senha=password).first()
        elif user_type == 'entregador':
            user = Entregador.query.filter_by(email=email, senha=password).first()

        if user:
            session['user_id'] = user.id
            session['user_type'] = user_type
            session['user_name'] = user.nome
        
            if user_type == 'cliente':
                return {"success": True, "redirect_url": "/dashboard_cliente"}, 200
            elif user_type == 'restaurante':
                return {"success": True, "redirect_url": "/dashboard_restaurante"}, 200
            elif user_type == 'entregador':
                return {"success": True, "redirect_url": "/dashboard_entregador"}, 200
        else:
            return {"success": False, "message": "Email ou Senha Incorretos"}, 401
    
    return render_template("home/home.html")

@app.route('/logout')
def logout():

    session.clear()  
    return redirect(url_for('home'))

@app.route('/cadastro_cliente', methods=['GET', 'POST'])
def cadastro_cliente():
    if request.method == 'POST':
        # Pega os dados do formulário
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        cpf = request.form['cpf']
        endereco = request.form['endereco']

        if Cliente.query.filter_by(email=email).first() and Cliente.query.filter_by(cpf=cpf).first():
            return render_template('restaurante/cadastro.html', error_message="Email ou CPF já cadastrado. Tente outra vez.")
        
        novo_cliente = Cliente(
            nome=nome,
            email=email,
            senha=senha,
            cpf=cpf,
            endereco=endereco
        )

        try:
            db.session.add(novo_cliente)
            db.session.commit()
            flash("Cadastro realizado com sucesso!", "success")
        except IntegrityError:
            db.session.rollback()  # Reverte a transação se ocorrer erro
            return render_template('cliente/cadastro.html', error_message="Erro ao salvar: CPF ou Email já cadastrados.")
    
    return render_template('cliente/cadastro.html')

@app.route('/cadastro_restaurante', methods=['GET', 'POST'])
def cadastro_restaurante():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        cnpj = request.form['cnpj']
        endereco = request.form['endereco']

        if Restaurante.query.filter_by(email=email).first() and Restaurante.query.filter_by(cnpj=cnpj).first():
            return render_template('restaurante/cadastro.html', error_message="Email ou CNPJ já cadastrado. Tente outra vez.")
        
        novo_restaurante = Restaurante(
            nome=nome,
            email=email,
            senha=senha,
            cnpj=cnpj,
            endereco=endereco
        )

        try:
            db.session.add(novo_restaurante)
            db.session.commit()
            flash("Cadastro realizado com sucesso!", "success")
        except IntegrityError:
            db.session.rollback()  
            return render_template('restaurante/cadastro.html', error_message="Erro ao salvar: CNPJ ou Email já cadastrados.")


    return render_template('restaurante/cadastro.html')

@app.route('/cadastro_entregador', methods=['GET', 'POST'])
def cadastro_entregador():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        cpf = request.form['cpf']

        if Entregador.query.filter_by(email=email).first() and Entregador.query.filter_by(cpf=cpf).first():
            return render_template('restaurante/cadastro.html', error_message="Email ou CPF já cadastrado. Tente outra vez.")
        
        novo_entregador = Entregador(
            nome=nome,
            email=email,
            senha=senha,
            cpf=cpf,
        )

        try:
            db.session.add(novo_entregador)
            db.session.commit()
            flash("Cadastro realizado com sucesso!", "success")
        except IntegrityError:
            db.session.rollback()  
            return render_template('entregador/cadastro.html', error_message="Erro ao salvar: CPF ou Email já cadastrados.")

    return render_template('entregador/cadastro.html')

@app.route('/dashboard_cliente')
@login_required
def dashboard_cliente():
    # Verifica se o usuário está logado e é do tipo correto
    if 'user_id' not in session or session['user_type'] != 'cliente':
        return redirect(url_for('home'))

    # Busca o cliente no banco de dados
    cliente = Cliente.query.get(session['user_id'])
    restaurantes = Restaurante.query.filter_by(status=True).all() 

    if not cliente:
        return redirect(url_for('home'))

    # Renderiza o dashboard com os dados do cliente
    return render_template('cliente/dashboard.html', cliente=cliente, restaurantes=restaurantes)

@app.route('/<int:restaurante_id>/cardapio')
@login_required
def cardapio(restaurante_id):
    cliente = Cliente.query.get(session['user_id'])
    restaurante = Restaurante.query.get_or_404(restaurante_id)
    produtos = Produto.query.filter_by(restaurante_id=restaurante_id).all()
    
    if not restaurante.status:
        return "Restaurante não encontrado"
    
    return render_template('cliente/cardapio.html', cliente=cliente, restaurante=restaurante, produtos=produtos)

@app.route('/carrinho', methods=['GET'])
@login_required
def carrinho():
    if session['user_type'] != 'cliente':
        return redirect('/')

    cliente_id = session['user_id']
    cliente = Cliente.query.get(cliente_id)
    carrinho = Carrinho.query.filter_by(cliente_id=cliente_id).first()

    if not carrinho:
        carrinho = Carrinho(cliente_id=cliente_id, total=0.0)
        db.session.add(carrinho)
        db.session.commit()

    itens = ItemCarrinho.query.filter_by(carrinho_id=carrinho.id).all()

    return render_template('cliente/carrinho.html', cliente=cliente, carrinho=carrinho, itens=itens)

@app.route('/adicionar_ao_carrinho', methods=['POST'])
@login_required
def adicionar_ao_carrinho():
    if session['user_type'] != 'cliente':
        return redirect('/')

    produto_id = request.form.get('produto_id')  # Obtém o ID do produto do formulário
    cliente_id = session['user_id']

    # Lógica para adicionar ao carrinho
    carrinho = Carrinho.query.filter_by(cliente_id=cliente_id).first()
    if not carrinho:
        carrinho = Carrinho(cliente_id=cliente_id, total=0.0)
        db.session.add(carrinho)
        db.session.commit()

    produto = Produto.query.get(produto_id)
    if not produto:
        return "Produto não encontrado", 404

    # Verifica se o carrinho já contém itens
    if carrinho.itens:
        # Obtém o restaurante do primeiro item no carrinho
        restaurante_atual = carrinho.itens[0].produto.restaurante_id
        if restaurante_atual != produto.restaurante_id:
            # Impede a adição se o restaurante for diferente
            return "Você só pode adicionar itens do mesmo restaurante ao carrinho.", 400

    # Verifica se o item já está no carrinho
    item = ItemCarrinho.query.filter_by(carrinho_id=carrinho.id, produto_id=produto_id).first()
    if item:
        item.quantidade += 1
        item.subtotal = item.quantidade * produto.preco
    else:
        item = ItemCarrinho(
            carrinho_id=carrinho.id,
            produto_id=produto_id,
            quantidade=1,
            subtotal=produto.preco
        )
        db.session.add(item)

    # Atualiza o total do carrinho
    carrinho.total += produto.preco
    db.session.commit()

    return redirect('/carrinho')

@app.route('/remover_do_carrinho', methods=['POST'])
@login_required
def remover_do_carrinho():
    if session['user_type'] != 'cliente':
        return redirect('/')

    cliente_id = session['user_id']
    produto_id = request.form.get('produto_id')  # Obtém o ID do produto do formulário

    carrinho = Carrinho.query.filter_by(cliente_id=cliente_id).first()
    if not carrinho:
        return redirect('/carrinho')

    # Procura o item no carrinho
    item = ItemCarrinho.query.filter_by(carrinho_id=carrinho.id, produto_id=produto_id).first()
    if not item:
        return redirect('/carrinho')

    if item.quantidade > 1:
        # Reduz a quantidade e atualiza o subtotal
        item.quantidade -= 1
        item.subtotal = item.quantidade * item.produto.preco
        carrinho.total -= item.produto.preco
    else:
        # Remove o item completamente se a quantidade for 1
        carrinho.total -= item.subtotal
        db.session.delete(item)

    db.session.commit()

    return redirect('/carrinho')  # Redireciona para o carrinho atualizado

def atualizar_pedidos_e_limpar_carrinho(forma_pagamento):
    cliente_id = session['user_id']
    carrinho = Carrinho.query.filter_by(cliente_id=cliente_id).first()
    restaurante_id = carrinho.itens[0].produto.restaurante_id 

    if not carrinho or not carrinho.itens:
        return None  # Retorna None se o carrinho estiver vazio

    # Criar o pedido
    pedido = Pedido(cliente_id=cliente_id, restaurante_id=restaurante_id, forma_pagamento=forma_pagamento)
    db.session.add(pedido)
    db.session.commit()

    # Associar os itens do carrinho ao pedido
    for item in carrinho.itens:
        item_pedido = ItemPedido(
            pedido_id=pedido.id,
            produto_nome=item.produto.nome,
            quantidade=item.quantidade,
            subtotal=item.subtotal
        )
        db.session.add(item_pedido)

    # Limpar o carrinho
    for item in carrinho.itens:
        db.session.delete(item)
    db.session.delete(carrinho)
    db.session.commit()

    return pedido


@app.route('/finalizar_pedido', methods=['POST'])
@login_required
def finalizar_pedido():
    if session['user_type'] != 'cliente':
        return redirect('/')

    forma_pagamento = request.form.get('forma_pagamento')

    if forma_pagamento == "pix":
        return redirect(url_for('pagina_pix'))
    else:
        atualizar_pedidos_e_limpar_carrinho("Cartao")
        return redirect(url_for('meus_pedidos'))
    
@app.route('/pagina_pix', methods=['GET', 'POST'])
@login_required
def pagina_pix():
    cliente_id = session['user_id']
    cliente = Cliente.query.get(cliente_id)
    # Exibe o QR Code e botão de confirmação de pagamento

    if request.method == 'POST':
        atualizar_pedidos_e_limpar_carrinho("PIX")
        db.session.commit()
        return redirect(url_for('meus_pedidos'))

    return render_template('cliente/pix.html', cliente=cliente)

@app.route('/meus_pedidos')
@login_required
def meus_pedidos():
    if session['user_type'] != 'cliente':
        return redirect('/')

    cliente_id = session['user_id']

    # Obter os dados do cliente
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return redirect('/')  # Redirecionar se o cliente não for encontrado

    # Obter os pedidos do cliente
    pedidos = Pedido.query.filter_by(cliente_id=cliente_id).all()

    pedidos_invertidos = pedidos[::-1] 
    # Adicionar detalhes aos pedidos
    pedidos_detalhados = []
    for pedido in pedidos_invertidos:
        # Obter os itens do pedido
        itens = ItemPedido.query.filter_by(pedido_id=pedido.id).all()
        total_pedido = sum(item.subtotal for item in itens)

        # Formatar a data do pedido
        pedido.data_pedido_formatada = pedido.data_pedido.strftime('%d/%m/%Y, %H:%M')

        # Adicionar as informações detalhadas do pedido
        pedidos_detalhados.append({
            'id': pedido.id,
            'status': pedido.status,
            'pedido': pedido,
            'itens': itens,
            'total': total_pedido
        })

    return render_template('cliente/pedidos.html', cliente=cliente, pedidos=pedidos_detalhados)

@app.route('/configuracoes_cliente', methods=['GET', 'POST'])
@login_required
def configuracoes_cliente():
    if session['user_type'] != 'cliente':
        return redirect(url_for('home'))

    cliente_id = session['user_id']
    cliente = Cliente.query.get(cliente_id)

    if not cliente:
        flash('Cliente não encontrado.', 'error')
        return redirect(url_for('dashboard_cliente'))

    if request.method == 'POST':
        try:
            cliente.nome = request.form.get('nome')
            cliente.email = request.form.get('email')
            cliente.cpf = request.form.get('cpf')
            cliente.endereco = request.form.get('endereco')

            db.session.commit()
            flash('Dados atualizados com sucesso!', 'success')
            return redirect(url_for('dashboard_cliente'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao atualizar os dados: {str(e)}', 'error')
            return redirect(url_for('configuracoes_cliente'))

    return render_template('cliente/configuracoes.html', cliente=cliente)


@app.route('/avaliar_pedido', methods=['POST'])
@login_required
def avaliar_pedido():
    if session['user_type'] != 'cliente':
        return redirect('/')

    pedido_id = request.form.get('pedido_id')
    nota_str = request.form.get('avaliacao')  # Agora nota_str está definida
    
    try:
        nota = int(nota_str)
    except (TypeError, ValueError):
        flash('Você precisa escolher uma nota de 1 a 5 estrelas.', 'error')
        return redirect(url_for('meus_pedidos'))

    if not pedido_id:
        flash('Pedido inválido.', 'error')
        return redirect(url_for('meus_pedidos'))

    pedido = Pedido.query.get(pedido_id)

    if pedido and pedido.cliente_id == session['user_id'] and pedido.status == 'Concluído' and not pedido.avaliacao:
        pedido.avaliacao = nota
        db.session.commit()
        flash('Avaliação registrada com sucesso!', 'success')
    else:
        flash('Erro ao registrar avaliação.', 'error')

    return redirect(url_for('meus_pedidos'))

@app.route('/dashboard_restaurante')
@login_required
def dashboard_restaurante():
    if 'user_id' not in session or session['user_type'] != 'restaurante':
        return redirect(url_for('home'))

    restaurante = Restaurante.query.get(session['user_id'])
    itens_menu = Produto.query.filter_by(restaurante_id=restaurante.id).all()

    if not restaurante:
        return redirect(url_for('home'))

    return render_template('restaurante/dashboard.html', restaurante=restaurante, itens_menu=itens_menu)

@app.route('/cadastro_produto', methods=['GET', 'POST'])
@login_required
def cadastro_produto():
    if 'user_id' not in session or session['user_type'] != 'restaurante':
        return redirect(url_for('home'))

    restaurante = Restaurante.query.get(session['user_id'])

    if not restaurante:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = float(request.form['preco'])
        imagem = request.files['imagem']

        # Verifica se a imagem foi fornecida
        imagem = None
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                imagem = filename

        if imagem == None:
            novo_produto = Produto(
                nome=nome,
                descricao=descricao,
                preco=preco,
                restaurante_id=session['user_id']  # Obtém o id do restaurante logado
            )
        else:
            novo_produto = Produto(
                nome=nome,
                descricao=descricao,
                preco=preco,
                imagem=filename,
                restaurante_id=session['user_id']  # Obtém o id do restaurante logado
            )

        try:
            db.session.add(novo_produto)
            db.session.commit()
            return redirect(url_for('dashboard_restaurante'))
        except Exception as e:
            db.session.rollback()
            return f"Erro ao cadastrar produto: {e}"
        finally:
            db.session.remove() 

    return render_template('restaurante/cadastrar_item.html', restaurante=restaurante)

@app.route('/editar_produto/<int:item_id>', methods=['GET', 'POST'])
@login_required
def editar_produto(item_id):
    if 'user_id' not in session or session['user_type'] != 'restaurante':
        return redirect(url_for('home'))

    restaurante = Restaurante.query.get(session['user_id'])
    produto = Produto.query.get(item_id)

    if not restaurante or not produto or produto.restaurante_id != restaurante.id:
        flash("Produto não encontrado ou você não tem permissão.", "error")
        return redirect(url_for('dashboard_restaurante'))

    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.descricao = request.form['descricao']
        produto.preco = float(request.form['preco'])

        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                produto.imagem = filename

        try:
            db.session.commit()
            flash("Produto atualizado com sucesso!", "success")
            return redirect(url_for('dashboard_restaurante'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar produto: {e}", "error")
        finally:
            db.session.remove()

    return render_template('restaurante/editar.html', restaurante=restaurante, produto=produto)

@app.route('/excluir_item/<int:item_id>', methods=['POST'])
@login_required
def excluir_item(item_id):
    try:
        item = Produto.query.get(item_id)
        if not item:
            flash("Item não encontrado.", "error")
            return redirect(url_for('dashboard_restaurante'))

        restaurante_id = session.get('user_id')
        if item.restaurante_id != restaurante_id:
            flash("Você não tem permissão para excluir este item.", "error")
            return redirect(url_for('dashboard_restaurante'))

        db.session.delete(item)
        db.session.commit()
        flash("Item excluído com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir item: {str(e)}", "error")

    return redirect(url_for('dashboard_restaurante'))

@app.route('/pedidos_restaurante')
@login_required
def pedidos_restaurante():
    if session['user_type'] != 'restaurante':
        return redirect('/')

    restaurante_id = session['user_id']

    # Obter todos os pedidos relacionados ao restaurante
    pedidos = Pedido.query.filter_by(restaurante_id=restaurante_id).all()
    restaurante = Restaurante.query.get(session['user_id'])
    
    pedidos_invertidos = pedidos[::-1] 

    # Adicionar detalhes ao template
    pedidos_detalhados = []
    for pedido in pedidos_invertidos:
        cliente = Cliente.query.get(pedido.cliente_id)
        itens = ItemPedido.query.filter_by(pedido_id=pedido.id).all()
        total_pedido = sum(item.subtotal for item in itens)

        pedidos_detalhados.append({
            'pedido': pedido,
            'cliente': cliente,
            'itens': itens,
            'total': total_pedido
        })

    return render_template('restaurante/pedidos.html', restaurante=restaurante, pedidos=pedidos_detalhados)

@app.route('/aceitar_pedido', methods=['POST'])
@login_required
def aceitar_pedido():
    if session['user_type'] != 'restaurante':
        return redirect('/')

    pedido_id = request.form.get('pedido_id')  
    pedido = Pedido.query.get(pedido_id)
    if pedido:
        pedido.status = "Confirmado"
        db.session.commit()

    return redirect(url_for('pedidos_restaurante'))

@app.route('/recusar_pedido', methods=['POST'])
@login_required
def recusar_pedido():
    if session['user_type'] != 'restaurante':
        return redirect('/')

    pedido_id = request.form.get('pedido_id')  # Obter o pedido_id do formulário
    pedido = Pedido.query.get(pedido_id)
    if pedido:
        pedido.status = "Recusado"
        db.session.commit()

    return redirect(url_for('pedidos_restaurante'))

@app.route('/enviar_para_entrega', methods=['POST'])
@login_required
def enviar_para_entrega():
    if session['user_type'] != 'restaurante':
        return redirect('/')

    pedido_id = request.form.get('pedido_id')
    pedido = Pedido.query.get(pedido_id)

    if pedido and pedido.status == 'Confirmado':
        pedido.status = 'Pedido Pronto Para Entrega'
        db.session.commit()
        flash('Pedido enviado para entrega!', 'success')

    return redirect(url_for('meus_pedidos'))

@app.route('/relatorios', methods=['GET', 'POST'])
@login_required
def relatorios():
    if session['user_type'] != 'restaurante':
        return redirect('/')

    restaurante_id = session['user_id']
    restaurante = Restaurante.query.get(restaurante_id)

    data_inicio = request.form.get('data_inicio')
    data_fim = request.form.get('data_fim')

    pedidos_query = Pedido.query.filter_by(restaurante_id=restaurante_id)

    if data_inicio and data_fim:
        try:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim_dt = datetime.combine(data_fim_dt, datetime.max.time())  # inclui o dia todo
            pedidos_query = pedidos_query.filter(Pedido.data_pedido.between(data_inicio_dt, data_fim_dt))
        except ValueError:
            flash('Formato de data inválido.', 'error')

    pedidos = pedidos_query.all()

    pedidos_detalhados = []
    total_vendas = 0
    for pedido in pedidos:
        cliente = Cliente.query.get(pedido.cliente_id)
        itens = ItemPedido.query.filter_by(pedido_id=pedido.id).all()
        total_pedido = sum(item.subtotal for item in itens)
        total_vendas += total_pedido

        pedidos_detalhados.append({
            'pedido': pedido,
            'cliente': cliente,
            'itens': itens,
            'total': total_pedido
        })

    return render_template(
        'restaurante/relatorios.html',
        restaurante=restaurante,
        pedidos=pedidos_detalhados,
        total_vendas=total_vendas,
        data_inicio=data_inicio,
        data_fim=data_fim
    )


@app.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    restaurante = Restaurante.query.get(session['user_id'])
    
    if request.method == 'POST':
        try:
            # Alternar o status
            restaurante.status = not restaurante.status
            db.session.commit()
            flash(f"Status atualizado para {'Online' if restaurante.status else 'Offline'}", 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar status: {str(e)}", 'error')

    return render_template('restaurante/configuracoes.html', restaurante=restaurante)

@app.route('/configuracoes/status', methods=['POST'])
@login_required
def atualizar_status():
    restaurante = Restaurante.query.get(session['user_id'])
    try:
        # Alternar o status com base no valor enviado
        novo_status = request.json.get('status')
        restaurante.status = novo_status
        db.session.commit()
        return {'success': True, 'status': 'Online' if novo_status else 'Offline'}, 200
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500

@app.route('/configuracoes/upload_foto_restaurante/<int:restaurante_id>', methods=['POST'])
@login_required
def upload_foto_restaurante(restaurante_id):
    restaurante = Restaurante.query.get_or_404(restaurante_id)
    
    # Verifica se a imagem foi enviada
    if 'foto' not in request.files:
        return "Nenhum arquivo enviado", 400
    
    file = request.files['foto']
    
    # Verifica se o arquivo foi selecionado
    if file.filename == '':
        return "Nenhum arquivo selecionado", 400
    
    # Se o arquivo for válido
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Atualiza a foto do restaurante no banco de dados
        restaurante.fotoperfil = filename
        db.session.commit()

        # Redireciona para a página de configurações ou dashboard
        return redirect(url_for('configuracoes', restaurante_id=restaurante.id))

    return "Tipo de arquivo não permitido", 400


@app.route('/dashboard_entregador')
@login_required
def dashboard_entregador():
    
    if 'user_id' not in session or session['user_type'] != 'entregador':
        return redirect(url_for('home'))

    entregador = Entregador.query.get(session['user_id'])

    if not entregador:
        return redirect(url_for('home'))
    
    pedidos = Pedido.query.filter_by(status='Pedido Pronto Para Entrega').all()
    
    pedidos_resultado = []
    for pedido in pedidos:
        # Obter os itens do pedido
        itens = ItemPedido.query.filter_by(pedido_id=pedido.id).all()
        total_pedido = sum(item.subtotal for item in itens)

        pedidos_resultado.append({
            'id': pedido.id,
            'restaurante': {
                'nome': pedido.restaurante.nome,
                'endereco': pedido.restaurante.endereco,
            },
            'cliente': {
                'nome': pedido.cliente.nome,
                'endereco': pedido.cliente.endereco,
            },
            'total': total_pedido,
        })

    return render_template('entregador/dashboard.html', entregador=entregador, pedidos=pedidos_resultado)

@app.route('/entrega')
@login_required
def entrega():
    if session['user_type'] != 'entregador':
        return redirect('/')

    entregador_id = session['user_id']
    entregador = Entregador.query.get(session['user_id'])

    pedidos = Pedido.query.filter_by(entregador_id=entregador_id).all()
    pedidos_invertidos = pedidos[::-1]
    
    pedidos_resultado = []
    for pedido in pedidos_invertidos:
        itens = ItemPedido.query.filter_by(pedido_id=pedido.id).all()
        total_pedido = sum(item.subtotal for item in itens)

        pedidos_resultado.append({
            'id': pedido.id,
            'status': pedido.status,
            'restaurante': {
                'nome': pedido.restaurante.nome,
                'endereco': pedido.restaurante.endereco,
            },
            'cliente': {
                'nome': pedido.cliente.nome,
                'endereco': pedido.cliente.endereco,
            },
            'itens': itens,  # Passando os itens para o template
            'total': total_pedido,
        })

    return render_template('entregador/entrega.html', entregador=entregador, pedidos=pedidos_resultado)

@app.route('/configuracoes_entregador', methods=['GET', 'POST'])
@login_required
def configuracoes_entregador():
    if session['user_type'] != 'entregador':
        return redirect(url_for('home'))

    entregador = Entregador.query.get(session['user_id'])

    if not entregador:
        flash('Cliente não encontrado.', 'error')
        return redirect(url_for('dashboard_entregador'))

    if request.method == 'POST':
        try:
            entregador.nome = request.form.get('nome')
            entregador.email = request.form.get('email')
            entregador.cpf = request.form.get('cpf')

            db.session.commit()
            flash('Dados atualizados com sucesso!', 'success')
            return redirect(url_for('dashboard_entregador'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao atualizar os dados: {str(e)}', 'error')
            return redirect(url_for('configuracoes_entregador'))

    return render_template('entregador/configuracoes.html', entregador=entregador)


@app.route('/aceitar_entrega', methods=['POST'])
@login_required
def aceitar_entrega():
    if session['user_type'] != 'entregador':
        return redirect('/')
    
    pedido_id = request.form.get('pedido_id')
    pedido = Pedido.query.get(pedido_id)

    if pedido and pedido.status == 'Pedido Pronto Para Entrega':
        pedido.status = 'Em Transporte'
        pedido.entregador_id = session['user_id']
        db.session.commit()
        flash('Você aceitou a entrega!', 'success')

    return redirect(url_for('entrega'))

@app.route('/finalizar_entrega', methods=['POST'])
@login_required
def finalizar_entrega():
    if session['user_type'] != 'entregador':
        return redirect('/')

    pedido_id = request.form.get('pedido_id')
    pedido = Pedido.query.get(pedido_id)

    if pedido and pedido.status == 'Em Transporte':
        pedido.status = 'Concluído'
        db.session.commit()

    return redirect(url_for('dashboard_entregador'))

if __name__ == "__main__":
    app.run(debug=True)
