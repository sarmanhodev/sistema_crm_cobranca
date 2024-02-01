from flask import *
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy
from sqlalchemy import desc, asc, func
from flask_login import *
from sqlalchemy.orm import joinedload
from tables import *
from datetime import datetime, date, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pytz
from werkzeug.security import generate_password_hash
import secrets
import string
import random


# create message object instance 
msg = MIMEMultipart()

class SQLAlchemy(_BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(self, app, options)
        options["pool_pre_ping"] = True

db = SQLAlchemy()
app = Flask(__name__, template_folder='./templates')

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}  

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:ROOT@localhost/sistema_crm"
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://sistema_crm_user:HVZBicqVS2r6fgwH6zI9hdQyRsSjqEvV@dpg-cki0f7ke1qns73cp9qa0-a.oregon-postgres.render.com/sistema_crm"

#SUPABASE DATABASE NÃO USAR
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Veh73ncYS13Ea7EF@db.tjcsvpnmjgishhsokqwn.supabase.co:5432/postgres"

#SUPABASE DATABASE
#app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.tjcsvpnmjgishhsokqwn:Veh73ncYS13Ea7EF@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

# Configuração da pasta estática
app.config['UPLOAD_FOLDER'] = '../static/documentos'

app.config["SECRET_KEY"] = 'secret'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

def gera_token():
    global token
    token = secrets.token_hex(64)
    return token

def gera_letra():
    global letra_aleatoria
    letras_minusculas = string.ascii_letters
    letra_aleatoria = random.choice(letras_minusculas)
    
    return letra_aleatoria


@login_manager.user_loader
def get_user(user_id):
    return db.session.query(Usuarios).filter(Usuarios.id==user_id).first()

#ROTA PARA FAZER O LOGIN NO SISTEMA
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method =='POST':
        email = request.form['usuarioEmail']
        pwd = request.form['usuarioSenha']
     
        user = db.session.query(Usuarios).filter(Usuarios.email==email).first()
        
        if not user or not check_password_hash(user.password, pwd):
            flash('Usuário Inválido! Verifique suas credenciais e tente novamente.')
            return redirect(url_for('login'))
        
        login_user(user)
        
        return redirect(url_for('home'))

    return render_template("login.html")



#CADASTRA NOVO USUÁRIO
@app.route("/cadastrar_usuario", methods=["GET", "POST"])
@login_required
def registrar_usuario():
    if request.method == "POST":
        nome=request.form["usuarioNome"]
        email =request.form["usuarioEmail"]
        password = request.form['usuarioSenha']
        empresa_nome = request.form['usuarioEmpresa']
        acesso_id = request.form['radio_privilegio'] 

        usuario = db.session.query(Usuarios).filter(Usuarios.nome==nome).filter(Usuarios.email==email).first()

        empresa = db.session.query(Empresa).filter(Empresa.nome_empresa==empresa_nome).first()
        if not empresa:
            nova_empresa = Empresa(nome_empresa = empresa_nome)
            db.session.add(nova_empresa)
            db.session.commit()
            print('\n Empresa cadastrada com sucesso \n')

        if not usuario:
            empresa = db.session.query(Empresa).filter(Empresa.nome_empresa==empresa_nome).first()
            user = Usuarios(nome=nome, email =email, password = password, empresa_id = empresa.id, acesso_id = acesso_id)
            db.session.add(user)
            db.session.commit()
            flash('Usuário cadastrado com sucesso!')
            print("\nUsuário cadastrado com sucesso!\n")

            message = f' Olá, {nome} !\n \n Seja muito bem-vindo(a) ao Sistema CRM. \n \n Para começar a usar o sistema, basta clicar neste link https://sistema-crm.onrender.com/login \n \n Segue, anexo a este e-mail, o manual do usuário, explicando toda funcionalidade do sistema. \n \n Em caso de dúvidas, contate o administrador através do e-mail adm.crm2023@gmail.com. \n \n Atenciosamente, \n \n **** NÃO RESPONDER ESTE E-MAIL**** \n' 
            
            # setup the parameters of the message 
            password = "mboi ugrx dang qlbe"
            msg['From'] = 'adm.crm2023@gmail.com'
            msg['To'] = user.email
            msg['Subject'] = "Seja Bem-Vindo(a) ao Sistema CRM"
            
            # add in the message body 
            msg.attach(MIMEText(message, 'plain'))   

            # Adicionando anexo ao e-mail
            nome_arquivo = 'manual_sistema_crm.pdf'
            anexo = open(nome_arquivo, 'rb')

            parte_anexo = MIMEBase('application', 'octet-stream')
            parte_anexo.set_payload((anexo).read())
            encoders.encode_base64(parte_anexo)
            parte_anexo.add_header('Content-Disposition', f"attachment; filename= {nome_arquivo}")

            msg.attach(parte_anexo)     
            #create server 
            server = smtplib.SMTP('smtp.gmail.com: 587')        
            server.starttls()
            
            # Login Credentials for sending the mail 
            server.login(msg['From'], password)        
            
            # send the message via the server. 
            server.sendmail(msg['From'], msg['To'], msg.as_string())        
            server.quit()

            print("successfully sent email to %s:" % (msg['To']))

            return redirect(url_for("painel_configuracoes", id=user.id))
        else:
            flash('Usuário já possui cadastro em nosso sistema. Verificar painel de usuários cadastrados.')
            return redirect(url_for("painel_configuracoes"))

    


@app.route("/atualiza_senha", methods = ['GET','POST'])
@login_required
def verifica_email():
    if request.method == 'POST':
        recupera_email = request.form['recupera_email']
        usuario = db.session.query(Usuarios).filter(Usuarios.email==recupera_email).first()

        if not usuario:
            flash('Usuário inexistente. Por favor entre em contato com o administrador')
            return redirect(url_for('login'))
            
        else:
            message = f'Link para redefinir sua senha pessoal https://sistema-crm.onrender.com/reset_password/{usuario.id}{gera_token()}'
            print(gera_token())
            # setup the parameters of the message 
            password = "mboi ugrx dang qlbe"
            msg['From'] = 'adm.crm2023@gmail.com'
            msg['To'] = usuario.email
            msg['Subject'] = "REDEFINA SUA SENHA DE ACESSO"
            
            # add in the message body 
            msg.attach(MIMEText(message, 'plain'))        
            #create server 
            server = smtplib.SMTP('smtp.gmail.com: 587')        
            server.starttls()
            
            # Login Credentials for sending the mail 
            server.login(msg['From'], password)        
            
            # send the message via the server. 
            server.sendmail(msg['From'], msg['To'], msg.as_string())        
            server.quit()

            print("successfully sent email to %s:" % (msg['To']))
            flash(f'Email enviado com sucesso para {usuario.email}!', 'success')        

            return redirect(url_for('login'))   
             

@app.route("/area_administrador/painel_configuracoes", methods=['GET','POST'])
@login_required
def painel_configuracoes():
    empresas = db.session.query(Empresa).order_by(asc(Empresa.id)).all()
    usuarios = db.session.query(Usuarios).order_by(asc(Usuarios.id)).group_by(Usuarios).having(Usuarios.id > 1).all()
    
    return render_template("configuracoes.html", usuarios=usuarios, empresas=empresas)


@app.route("/update_usuario/<id>", methods =['GET','POST'])
@login_required
def update_usuario(id):
    usuario = db.session.query(Usuarios).filter(Usuarios.id==id).first()

    if request.method == 'POST':
        usuario.nome = request.form['nomeusuario']
        usuario.email = request.form['emailusuario']
        usuario.acesso_id = request.form['radio_privilegio']

        db.session.commit()

        flash(f"Dados referentes ao usuário {usuario.nome} atualizados com sucesso")

        return redirect(url_for('painel_configuracoes'))

#PAINEL DE CONFIGURAÇÕES ACESSADO SOMENTE POR USUÁRIOS
@app.route("/usuario<id>/painel_configuracoes", methods=['GET','POST'])
@login_required
def painel_configuracoes_usuario(id):
    usuario = db.session.query(Usuarios).filter(Usuarios.id==id).first()

    return render_template('painel_usuario.html', usuario = usuario)


#ROTA PARA ATUALIZAR DADOS DO USUÁRIO, ACESSADOS SOMENTE POR ELE
@app.route("/update_user/<id>", methods =['GET','POST'])
@login_required
def update_user(id):
    usuario = db.session.query(Usuarios).filter(Usuarios.id==id).first()

    if request.method == 'POST':
        password = request.form['senha_usuario']
        usuario.nome = request.form['nomeusuario']
        usuario.email = request.form['emailusuario']
        usuario.password = generate_password_hash(password)

        db.session.commit()

        flash('Dados atualizados com sucesso!')

        return redirect(url_for('painel_configuracoes_usuario', id = id))



@app.route("/deletar_usuario/<id>", methods = ['GET', 'POST'])
@login_required
def delete_usuario(id):
    usuario = db.session.query(Usuarios).filter(Usuarios.id==id).first()
    db.session.delete(usuario)
    db.session.commit()

    flash("Registro excluído e e-mail encaminhado")

    message = f'Prezado(a) Sr.(a) {usuario.nome}. \n \n Estamos encaminhando este aviso para comunicar que seu acesso foi cancelado. \n \n Para mais informações, contate o administrador através do e-mail adm.crm2023@gmail.com \n \n Atenciosamente, ' 
            
    # setup the parameters of the message 
    password = "mboi ugrx dang qlbe"
    msg['From'] = 'adm.crm2023@gmail.com'
    msg['To'] = usuario.email
    msg['Subject'] = "Aviso Importante - Sistema CRM"
            
    # add in the message body 
    msg.attach(MIMEText(message, 'plain'))        
    #create server 
    server = smtplib.SMTP('smtp.gmail.com: 587')        
    server.starttls()
            
    # Login Credentials for sending the mail 
    server.login(msg['From'], password)        
            
    # send the message via the server. 
    server.sendmail(msg['From'], msg['To'], msg.as_string())        
    server.quit()

    print("successfully sent email to %s:" % (msg['To']))

    return redirect(url_for('painel_configuracoes'))


@app.route("/redefinir_password_usuario/<id>", methods = ['GET','POST'])
@login_required
def reset_password_usuario(id):
    senha_padrao = "123456789CRM"
    usuario = db.session.query(Usuarios).filter(Usuarios.id==id).first()

    usuario.password = generate_password_hash(senha_padrao)
    db.session.commit()

    flash(f"Senha do usuário {usuario.nome} redefinida como senha padrão")

    return redirect(url_for('painel_configuracoes'))

        
@app.route("/search_user/<nome>", methods = ['GET', 'POST'])
@login_required
def search_user(nome):
    usuario = db.session.query(Usuarios).filter(Usuarios.nome==nome).first()

    usuario = db.session.query(Usuarios).filter(Usuarios.nome == nome).first()

    if usuario is None:
        print('ERROR 500')
        return jsonify({'error': 'Usuário não encontrado'}), 500
    else:
        list_users = [usuario.dict_users()]
        print(list_users)
        return jsonify(list_users)
            

@app.route("/reset_password_usuario/<int:id><token_acesso>", methods = ['GET','POST'])
def reset_password(id, token_acesso):
    token_acesso = gera_token()
    if request.method == 'POST':
        
        usuario = db.session.query(Usuarios).filter(Usuarios.id==id).first()
        nova_senha = request.form['nova_senha']
        usuario.password = generate_password_hash(nova_senha)
        db.session.commit()

        return redirect(url_for('login'))
    
    return render_template("atualiza_senha.html", user =db.session.query(Usuarios).filter(Usuarios.id==id).first() , token_acesso = token_acesso)


# Manipulador de erro 404
@app.errorhandler(404)
def pagina_nao_encontrada(error):
    return render_template('404.html'), 404

# Manipulador de erro 401 (login não autorizado)
@app.errorhandler(401)
def acesso_nao_autorizado(error):
    return render_template('401.html'), 401

@app.route("/dashboard_usuario/<id>", methods=['GET','POST'])
@login_required
def dashboard_usuario(id):
    usuario = db.session.query(Usuarios).filter(Usuarios.id==id).first()
    data_atual = date.today()
    ano_atual = db.session.query(Anos).filter(Anos.ano== data_atual.year).first()
    mes_atual = db.session.query(Meses).filter(Meses.id==data_atual.month).first()
    
    token_acesso1 = gera_token()
    token_acesso2 = gera_token()

    #CRIAR CONTADOR PARA QUEM CONTRATOU O SERVIÇO
    clientes_inadimplentes_mensal= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "1").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id==mes_atual.id).all()
    clientes_inadimplentes_anual= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "1").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).all()
        
    #CRIAR CONTADOR PARA QUEM NÃO CONTRATOU O SERVIÇO
    clientes_adimplentes_mensal= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "2").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id==mes_atual.id).all()
    clientes_adimplentes_anual= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "2").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).all()       

    cliente_dados = db.session.query(Cliente_Dados).order_by(desc(Cliente_Dados.id)).options(joinedload(Cliente_Dados.cliente_dados_boleto), joinedload(Cliente_Dados.cliente_dados_cliente),\
    joinedload(Cliente_Dados.cliente_dados_contato), joinedload(Cliente_Dados.cliente_dados_mensagem), joinedload(Cliente_Dados.cliente_dados_status),\
    joinedload(Cliente_Dados.cliente_dados_topico), joinedload(Cliente_Dados.cliente_dados_usuario)).all()
        
    status = db.session.query(Status).order_by(asc(Status.id)).group_by(Status.id).having(Status.id < 3).all()
    status_total = db.session.query(Status).options(joinedload(Status.status_cliente_dados)).order_by(asc(Status.id)).all()
    

    #DADOS ANUAIS
    boletos_pendentes_anual = db.session.query(func.sum(Boleto.valor)).filter(Boleto.status_id=='1').filter(Boleto.ano_id==ano_atual.id).filter(Boleto.usuario_id==usuario.id).first()
    boletos_pagos_anual = db.session.query(func.sum(Boleto.valor_pago)).filter(Boleto.status_id=='2').filter(Boleto.ano_id==ano_atual.id).filter(Boleto.usuario_id==usuario.id).first()
        
    #DADOS MENSAIS
    boletos_pendentes_mensal = db.session.query(func.sum(Boleto.valor)).filter(Boleto.status_id=='1').filter(Boleto.ano_id==ano_atual.id).filter(Boleto.mes_id==mes_atual.id).filter(Boleto.usuario_id==usuario.id).first()
    boletos_pagos_mensal = db.session.query(func.sum(Boleto.valor_pago)).filter(Boleto.status_id=='2').filter(Boleto.ano_id==ano_atual.id).filter(Boleto.mes_id==mes_atual.id).filter(Boleto.usuario_id==usuario.id).first()

    return render_template("dashboard_usuario.html", clientes_inadimplentes_mensal=clientes_inadimplentes_mensal,clientes_inadimplentes_anual=clientes_inadimplentes_anual, token_acesso1=token_acesso1,token_acesso2=token_acesso2,
            clientes_adimplentes_mensal=clientes_adimplentes_mensal,  clientes_adimplentes_anual=clientes_adimplentes_anual, status = status, motivos = db.session.query(Topico).order_by(asc(Topico.id)).all(), usuario = usuario, 
            textos = db.session.query(Textos).all(), status_total=status_total,   mensagens = db.session.query(Mensagem).order_by(desc(Mensagem.data_envio)).all(),
            clientes = db.session.query(Cliente).order_by(desc(Cliente.id)).all(), cliente_dados=cliente_dados, ano_atual = ano_atual, mes_atual = mes_atual,
            boletos_pendentes_anual = boletos_pendentes_anual[0], boletos_pagos_anual = boletos_pagos_anual[0],boletos_pendentes_mensal=boletos_pendentes_mensal[0],boletos_pagos_mensal=boletos_pagos_mensal[0])



@app.route("/cadastrar_cliente", methods = ["GET", "POST"])
def cadastra_cliente():
    data_atual = date.today()
    ano_atual = db.session.query(Anos).filter(Anos.ano== data_atual.year).first()
    mes_atual = db.session.query(Meses).filter(Meses.id==data_atual.month).first()

    mes_ano = db.session.query(Mes_Ano).filter(Mes_Ano.ano_id==ano_atual.id).filter(Mes_Ano.mes_id==mes_atual.id).first()

    if request.method == "POST":
        seleciona_status = "Pagamento Pendente"
        status_cliente = db.session.query(Status).filter(Status.status==seleciona_status).first()
        select_topicos = request.form['select_topicos']
        data_atual = request.form['data_atual']
        data_proximo_contato = request.form['data_proximo_contato']
        usuario_id = request.form['usuario_id']
        usuario = db.session.query(Usuarios).filter(Usuarios.id==usuario_id).first()

        #DADOS CLIENTE
        nome_cliente = request.form['nome']
        cliente = db.session.query(Cliente).filter(Cliente.nome==nome_cliente).first()
        
        #DADOS BOLETO
        numero_boleto = request.form['numero_boleto']
        data_vencimento = request.form['data_vencimento']
        dt_vencimento = datetime.strptime(data_vencimento,'%Y-%m-%d').date()
        data_vencimento_formatada = datetime.strftime(dt_vencimento,'%d/%m/%Y')

        valor_boleto = request.form['valor_boleto']
        valor_multa = request.form['valor_multa']
        juros_diarios = request.form['juros_diarios']
        observacoes = request.form['observacoes']

        verifica_topico = db.session.query(Topico).filter(Topico.topico==select_topicos).first()

        if verifica_topico != None:
            print(f'\n Esse motivo já existe {verifica_topico.topico}')
        else:
            novo_topico = Topico(topico = select_topicos)
            db.session.add(novo_topico)
            db.session.commit()

        if observacoes == None:
            boleto = Boleto(numero_boleto = numero_boleto, data_vencimento = data_vencimento_formatada, data_pagamento = None, valor = valor_boleto,
                    valor_multa = valor_multa, status_id = status_cliente.id, valor_pago = None,juros_diarios=juros_diarios,ano_id = ano_atual.id,
                    mes_id = mes_atual.id, mes_ano_id = mes_ano.id, empresa_id = usuario.empresa_id, usuario_id = usuario_id, observacoes = None)
            db.session.add(boleto)
            db.session.commit()
        else:
            boleto = Boleto(numero_boleto = numero_boleto, data_vencimento = data_vencimento_formatada, data_pagamento = None, valor = valor_boleto,
                    valor_multa = valor_multa, status_id = status_cliente.id, valor_pago = None,juros_diarios=juros_diarios,ano_id = ano_atual.id,
                    mes_id = mes_atual.id, mes_ano_id = mes_ano.id, empresa_id = usuario.empresa_id, usuario_id = usuario_id, observacoes = observacoes)
            db.session.add(boleto)
            db.session.commit()

        
        contato = Data_Contato(primeiro_contato = data_atual, proximo_contato = data_proximo_contato, ultimo_contato = data_atual)
        db.session.add(contato)
        db.session.commit()

        if not cliente:
            novo_cliente = Cliente(nome = request.form['nome'], email = request.form['email'], telefone = request.form['telefone'], empresa_id = usuario.empresa_id, usuario_id = usuario_id)
            db.session.add(novo_cliente)
            db.session.commit()
            print("\nCliente adicionado ao banco com sucesso\n")


            cliente_boleto = Cliente_Boleto(cliente_id = novo_cliente.id, boleto_id = boleto.id, ano_id = ano_atual.id, mes_id = mes_atual.id)
            db.session.add(cliente_boleto)
            db.session.commit()

            topico = db.session.query(Topico).filter(Topico.topico==select_topicos).first()

            if select_topicos == None:
                cliente_dados = Cliente_Dados(cliente_id = novo_cliente.id, boleto_id = boleto.id, status_id = status_cliente.id, data_contato_id = contato.id,
                                    topico_id = None, empresa_id = usuario.empresa_id, usuario_id = usuario_id, ano_id = ano_atual.id, mes_id = mes_atual.id)
                db.session.add(cliente_dados)
                db.session.commit()
            else:
                cliente_dados = Cliente_Dados(cliente_id = novo_cliente.id, boleto_id = boleto.id, status_id = status_cliente.id, data_contato_id = contato.id,
                                    topico_id = topico.id, empresa_id = usuario.empresa_id, usuario_id = usuario_id, ano_id = ano_atual.id, mes_id = mes_atual.id)
                db.session.add(cliente_dados)
                db.session.commit()

            

            ano_cliente = Ano_Cliente(ano_id = ano_atual.id,cliente_id = novo_cliente.id)
            db.session.add(ano_cliente)
            db.session.commit()

            mes_cliente = Mes_Cliente(mes_id = mes_atual.id,cliente_id = novo_cliente.id)
            db.session.add(mes_cliente)
            db.session.commit()


            return redirect(url_for('home'))
        else:
            topico = db.session.query(Topico).filter(Topico.topico==select_topicos).first()

            cliente_boleto = Cliente_Boleto(cliente_id = cliente.id, boleto_id = boleto.id, ano_id = ano_atual.id, mes_id = mes_atual.id)
            db.session.add(cliente_boleto)
            db.session.commit()

            if select_topicos == None:
                cliente_dados = Cliente_Dados(cliente_id = cliente.id, boleto_id = boleto.id, status_id = status_cliente.id, data_contato_id = contato.id,
                                    topico_id = None, empresa_id = usuario.empresa_id, usuario_id = usuario_id, ano_id = ano_atual.id, mes_id = mes_atual.id)
                db.session.add(cliente_dados)
                db.session.commit()
            else:
                cliente_dados = Cliente_Dados(cliente_id = cliente.id, boleto_id = boleto.id, status_id = status_cliente.id, data_contato_id = contato.id,
                                    topico_id = topico.id, empresa_id = usuario.empresa_id, usuario_id = usuario_id, ano_id = ano_atual.id, mes_id = mes_atual.id)
                db.session.add(cliente_dados)
                db.session.commit()

            ano_cliente = Ano_Cliente(ano_id = ano_atual.id,cliente_id = cliente.id)
            db.session.add(ano_cliente)
            db.session.commit()

            mes_cliente = Mes_Cliente(mes_id = mes_atual.id,cliente_id = cliente.id)
            db.session.add(mes_cliente)
            db.session.commit()

            return redirect(url_for('home'))               
        


#HOME - TELA PRINCIPAL
@app.route("/home", methods = ["GET", "POST"])
@login_required
def home():
    token_acesso1 = gera_token()
    token_acesso2 = gera_token()

    data_atual = date.today()
    ano_atual = db.session.query(Anos).filter(Anos.ano== data_atual.year).first()
    mes_atual = db.session.query(Meses).filter(Meses.id==data_atual.month).first()
    
    if current_user.is_authenticated:
        usuario = db.session.query(Usuarios).filter(Usuarios.id==current_user.id).first()
        #CRIAR CONTADOR PARA QUEM CONTRATOU O SERVIÇO
        clientes_inadimplentes_mensal= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "1").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id==mes_atual.id).all()
        clientes_inadimplentes_anual= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "1").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).all()
        
        #CRIAR CONTADOR PARA QUEM NÃO CONTRATOU O SERVIÇO
        clientes_adimplentes_mensal= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "2").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id==mes_atual.id).all()
        clientes_adimplentes_anual= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "2").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).all()       
        
        cliente_dados = db.session.query(Cliente_Dados).order_by(desc(Cliente_Dados.id)).options(joinedload(Cliente_Dados.cliente_dados_boleto), joinedload(Cliente_Dados.cliente_dados_cliente),\
        joinedload(Cliente_Dados.cliente_dados_contato), joinedload(Cliente_Dados.cliente_dados_mensagem), joinedload(Cliente_Dados.cliente_dados_status),\
        joinedload(Cliente_Dados.cliente_dados_topico), joinedload(Cliente_Dados.cliente_dados_usuario)).all()
        
        status = db.session.query(Status).order_by(asc(Status.id)).group_by(Status.id).having(Status.id < 3).all()
        status_total = db.session.query(Status).options(joinedload(Status.status_cliente_dados)).order_by(asc(Status.id)).all()
        
        #DADOS ANUAIS REFERENTES A VALORES
        boletos_pendentes_anual = db.session.query(func.sum(Boleto.valor)).filter(Boleto.status_id=='1').filter(Boleto.ano_id==ano_atual.id).filter(Boleto.empresa_id==usuario.empresa_id).first()
        boletos_pagos_anual = db.session.query(func.sum(Boleto.valor_pago)).filter(Boleto.status_id=='2').filter(Boleto.ano_id==ano_atual.id).filter(Boleto.empresa_id==usuario.empresa_id).first()
        
        #DADOS MENSAIS REFERENTES A VALORES
        boletos_pendentes_mensal = db.session.query(func.sum(Boleto.valor)).filter(Boleto.status_id=='1').filter(Boleto.ano_id==ano_atual.id).filter(Boleto.mes_id==mes_atual.id).filter(Boleto.empresa_id==usuario.empresa_id).first()
        boletos_pagos_mensal = db.session.query(func.sum(Boleto.valor_pago)).filter(Boleto.status_id=='2').filter(Boleto.ano_id==ano_atual.id).filter(Boleto.mes_id==mes_atual.id).filter(Boleto.empresa_id==usuario.empresa_id).first()
        
        #DADOS ANUAIS TOTAL
        dados_boletos_pendentes_anual = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).all()
        dados_boletos_pagos_anual = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).all()

        #DADOS MENSAIS BOLETOS
        dados_boletos_pendentes_mensal = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id==mes_atual.id).all()
        dados_boletos_pagos_mensal = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id==mes_atual.id).all()

        clientes = db.session.query(Usuarios).order_by(asc(Usuarios.id)).group_by(Usuarios).having(Usuarios.acesso_id==2).all()
        motivo = db.session.query(Topico).order_by(asc(Topico.id)).group_by(Topico).having(Topico.topico != '').all()

        return render_template("home.html", motivo = motivo, clientes_inadimplentes_mensal=clientes_inadimplentes_mensal,clientes_inadimplentes_anual=clientes_inadimplentes_anual,
            clientes_adimplentes_mensal=clientes_adimplentes_mensal,  clientes_adimplentes_anual=clientes_adimplentes_anual, status = status, motivos = db.session.query(Topico).order_by(asc(Topico.id)).all(), usuario = usuario, 
            textos = db.session.query(Textos).all(), status_total=status_total,   mensagens = db.session.query(Mensagem).order_by(desc(Mensagem.data_envio)).all(),
            clientes = clientes, cliente_dados=cliente_dados, ano_atual = ano_atual, mes_atual = mes_atual, token_acesso1=token_acesso1,token_acesso2=token_acesso2,
            boletos_pendentes_anual = boletos_pendentes_anual[0], boletos_pagos_anual = boletos_pagos_anual[0],boletos_pendentes_mensal=boletos_pendentes_mensal[0],boletos_pagos_mensal=boletos_pagos_mensal[0],
            dados_boletos_pendentes_anual=dados_boletos_pendentes_anual,dados_boletos_pagos_anual=dados_boletos_pagos_anual,dados_boletos_pendentes_mensal=dados_boletos_pendentes_mensal,dados_boletos_pagos_mensal=dados_boletos_pagos_mensal)


@app.route('/apagar_registro/<cliente_id>_<boleto_id>', methods =['GET','POST'])
@login_required
def delete(cliente_id, boleto_id):
    cliente_dados = db.session.query(Cliente_Dados).filter(Cliente_Dados.cliente_id==cliente_id).filter(Cliente_Dados.boleto_id==boleto_id).first()
    db.session.delete(cliente_dados)
    db.session.commit()

    cliente_mensagens = db.session.query(Mensagem).filter(Mensagem.cliente_id==cliente_id).filter(Mensagem.cliente_dados_id==cliente_dados.id).all()
    for delete_mensagem in cliente_mensagens:
        db.session.delete(delete_mensagem)
        db.session.commit()

    cliente_boleto = db.session.query(Cliente_Boleto).filter(Cliente_Boleto.cliente_id==cliente_id).filter(Cliente_Boleto.boleto_id==boleto_id).first()
    db.session.delete(cliente_boleto)
    db.session.commit()

    boleto = db.session.query(Boleto).filter(Boleto.id==boleto_id).first()
    db.session.delete(boleto)
    db.session.commit()

    data_contato = db.session.query(Data_Contato).filter(Data_Contato.id==cliente_dados.data_contato_id).first()
    db.session.delete(data_contato)
    db.session.commit()

    """"
    EXIBINDO, NO TEMPLATE HTML, A MENSAGEM DE CONFIRMAÇÃO DA
    EXCLUSÃO DE UM REGISTRO
    
    """
    print('Registro excluído com sucesso!')
    flash('Registro excluído com sucesso!')

    return redirect(url_for('home'))


@app.route('/inserir_motivo/<int:boleto_id>', methods = ['GET', 'POST'])
@login_required
def inserir_motivo(boleto_id):
    cliente_dados = db.session.query(Cliente_Dados).filter(Cliente_Dados.boleto_id==boleto_id).first()
    boleto = db.session.query(Boleto).filter(Boleto.id==boleto_id).first()
    dados_dict = request.get_json()
    motivo = dados_dict[0]['motivo']
    topico = db.session.query(Topico).filter(Topico.topico==motivo).first()

    if not topico:
        novo_topico = Topico(topico = motivo)
        db.session.add(novo_topico)
        db.session.commit()
    
    if request.method == 'POST':
        topico = db.session.query(Topico).filter(Topico.topico==motivo).first()
        cliente_dados.topico_id = topico.id
        db.session.commit()

        flash(f'Motivo de não pagamento referente ao boleto {boleto.numero_boleto} atualizado com sucesso!')

        return redirect(url_for('home'))


@app.route('/inserir_observacao/<int:boleto_id>', methods = ['GET', 'POST'])
@login_required
def inserir_observacao(boleto_id):
    boleto = db.session.query(Boleto).filter(Boleto.id==boleto_id).first()
    dados_dict = request.get_json()
    observacao = dados_dict[0]['observacao']
    
    if request.method == 'POST':
        boleto.observacoes = observacao
        db.session.commit()

        return redirect(url_for('home'))
    

@app.route('/alterar_data_vencimento/<int:boleto_id>', methods=['GET', 'POST'])
@login_required
def alterar_data_vencimento(boleto_id):
    boleto = db.session.query(Boleto).filter(Boleto.id==boleto_id).first()
    dados_dict = request.get_json()

    if request.method == 'POST':
        boleto.data_vencimento = dados_dict[0]['data_vencimento']
        db.session.commit()

        flash(f'Data de vencimento referente ao boleto {boleto.numero_boleto} atualizada com sucesso')

        return redirect(url_for('home'))


@app.route("/cliente_contratou/<id>", methods = ['GET','POST'])
@login_required
def cliente_contratou(id):
    cliente = db.session.query(Cliente).filter(Cliente.id==id).first()
    data_contato = db.session.query(Data_Contato).filter(Data_Contato.id==cliente.contato_id).first()
    data_vencimento = request.form['data_vencimento']
    dt_obj  = datetime.strptime(data_vencimento,'%Y-%m-%d').date()
    data_vencimento_formatada = datetime.strftime(dt_obj,'%d/%m/%Y')

    if request.method == 'POST':
        data_contato.data_vencimento = data_vencimento_formatada
        cliente.contratou_servico_id = '1'
        cliente.status_id = '2'

        db.session.commit()

        return redirect(url_for('home'))
    

@app.route("/pagamento_pendente/<id>", methods=['GET','POST'])
@login_required
def pagamento_pendente(id):
    dados_dict = request.get_json()
    cliente = db.session.query(Cliente).filter(Cliente.id==id).first()

    if request.method == 'POST':
        cliente.contratou_servico_id = dados_dict[0]['contratou_servico']
        cliente.status_id = dados_dict[0]['status']

        db.session.commit()

        return redirect(url_for('home'))
    

@app.route("/pagamento_confirmado/<cliente_id>_<boleto_id>", methods=['GET','POST'])
@login_required
def pagamento_confirmado(cliente_id, boleto_id):
    dados_dict = request.get_json()
    cliente = db.session.query(Cliente_Dados).filter(Cliente_Dados.cliente_id==cliente_id).filter(Cliente_Dados.boleto_id==boleto_id).first()

    boleto = db.session.query(Boleto).filter(Boleto.id==boleto_id).first()
    
    status = db.session.query(Status).filter(Status.status==dados_dict[0]['status']).first()

    if request.method == 'POST':
        cliente.status_id = status.id
        db.session.commit()

        boleto.data_pagamento = dados_dict[0]['data_pagamento']
        boleto.status_id = status.id
        boleto.valor_pago = dados_dict[0]['valor_boleto']
        db.session.commit()
        flash('Pagamento confirmado com sucesso')

        return redirect(url_for('home'))



@app.route('/update_cliente/<id>', methods=['GET','POST'])
@login_required
def update_cliente(id):
    cliente = db.session.query(Cliente).filter(Cliente.id==id).first()
    
    if request.method == 'POST':
        cliente.nome = request.form['nome_editado']
        cliente.telefone = request.form['telefone_editado']
        cliente.email = request.form['email_editado']
        db.session.commit()
        print('Registro atualizado com sucesso!')
        flash('Registro atualizado com sucesso!')
        return redirect(url_for('home'))


@app.route('/update_proximocontato/<cliente_id>_<boleto_id>', methods=['GET','POST'])
@login_required
def update_proximocontato(cliente_id, boleto_id):
    cliente = db.session.query(Cliente_Dados).filter(Cliente_Dados.cliente_id==cliente_id).filter(Cliente_Dados.boleto_id==boleto_id).first()
    
    if request.method == 'POST':
        
        cliente.cliente_dados_contato.proximo_contato = request.form['adiciona_cinco_dias']
        
        db.session.commit()
        print('Data atualizada com sucesso!')
        flash('Data atualizada com sucesso!')
        return redirect('/home')



@app.route('/update_ultimocontato/<cliente_id>_<boleto_id>', methods=['GET','POST'])
@login_required
def update_ultimocontato(cliente_id,boleto_id):
    cliente = db.session.query(Cliente_Dados).filter(Cliente_Dados.cliente_id==cliente_id).filter(Cliente_Dados.boleto_id==boleto_id).first()
    data_ultimo_contato = request.form['ultimo_contato']
    dt_obj  = datetime.strptime(data_ultimo_contato,'%Y-%m-%d')
    data_formatada_ultimo_contato = datetime.strftime(dt_obj,'%d/%m/%Y')
    print(data_formatada_ultimo_contato)
   
    if request.method == 'POST':
        
        cliente.cliente_dados_contato.ultimo_contato = data_formatada_ultimo_contato
        
        db.session.commit()
        print('Data atualizada com sucesso!')
        flash('Data atualizada com sucesso!')
        return redirect('/home')
    

#ROTA PARA DASHBOARD DE GRÁFICOS
@app.route("/gráficos/<token_acesso1><gera_letra1>_<int:usuario_id>_<gera_letra2><token_acesso2>", methods=['GET', 'POST'])
@login_required
def graficos(token_acesso1,usuario_id,token_acesso2,gera_letra1,gera_letra2):
    data_atual = date.today()
    ano_atual = db.session.query(Anos).filter(Anos.ano== data_atual.year).first()
    mes_atual = db.session.query(Meses).filter(Meses.id==data_atual.month).first()
    token_acesso1 = gera_token()
    token_acesso2 = gera_token()
    token_acesso3 = gera_token()
    gera_letra1 = gera_letra()
    gera_letra2 = gera_letra()

    if current_user.id != usuario_id:
        logout_user()
        return render_template("acesso_negado.html")
    else:
        usuario = db.session.query(Usuarios).filter(Usuarios.id==usuario_id).first()
        #CRIAR CONTADOR PARA QUEM CONTRATOU O SERVIÇO
        clientes_inadimplentes_mensal= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "1").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id==mes_atual.id).all()
        clientes_inadimplentes_anual= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "1").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).all()
            
        #CRIAR CONTADOR PARA QUEM NÃO CONTRATOU O SERVIÇO
        clientes_adimplentes_mensal= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "2").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id==mes_atual.id).all()
        clientes_adimplentes_anual= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "2").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).all()       
                
        #DADOS ANUAIS REFERENTE A VALORES
        boletos_pendentes_anual = db.session.query(func.sum(Boleto.valor)).filter(Boleto.status_id=='1').filter(Boleto.empresa_id==usuario.empresa_id).filter(Boleto.ano_id==ano_atual.id).first()
        boletos_pagos_anual = db.session.query(func.sum(Boleto.valor_pago)).filter(Boleto.status_id=='2').filter(Boleto.empresa_id==usuario.empresa_id).filter(Boleto.ano_id==ano_atual.id).first()
        
        #DADOS MENSAIS REFERENTE A VALORES
        boletos_pendentes_mensal = db.session.query(func.sum(Boleto.valor)).filter(Boleto.status_id=='1').filter(Boleto.empresa_id==usuario.empresa_id).filter(Boleto.ano_id==ano_atual.id).filter(Boleto.mes_id==mes_atual.id).first()
        boletos_pagos_mensal = db.session.query(func.sum(Boleto.valor_pago)).filter(Boleto.status_id=='2').filter(Boleto.empresa_id==usuario.empresa_id).filter(Boleto.ano_id==ano_atual.id).filter(Boleto.mes_id==mes_atual.id).first()

        #DADOS ANUAIS TOTAL
        dados_boletos_pendentes_anual = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).all()
        dados_boletos_pagos_anual = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).all()

        #DADOS MENSAIS BOLETOS
        dados_boletos_pendentes_mensal = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id==mes_atual.id).all()
        dados_boletos_pagos_mensal = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id==mes_atual.id).all()

        boletos_pendentes_mensal_janeiro = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id==1).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Boleto.mes_id=='1').all()
        boletos_pagos_mensal_janeiro = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id==2).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Boleto.mes_id=='1').all()
        boletos_janeiro = db.session.query(Cliente_Dados).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='1').all()
            
        boletos_pendentes_mensal_fevereiro = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='2').all()
        boletos_pagos_mensal_fevereiro = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='2').all()
        boletos_fevereiro = db.session.query(Cliente_Dados).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='2').all()
        
        boletos_pendentes_mensal_marco = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='3').all()
        boletos_pagos_mensal_marco = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='3').all()
        boletos_marco = db.session.query(Cliente_Dados).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='3').all()
            
        boletos_pendentes_mensal_abril = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='4').all()
        boletos_pagos_mensal_abril = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='4').all()
        boletos_abril = db.session.query(Cliente_Dados).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='4').all()

        boletos_pendentes_mensal_maio = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='5').all()
        boletos_pagos_mensal_maio = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='5').all()
        boletos_maio = db.session.query(Cliente_Dados).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='5').all()

        boletos_pendentes_mensal_junho = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='6').all()
        boletos_pagos_mensal_junho = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='6').all()
        boletos_junho = db.session.query(Cliente_Dados).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='6').all()

        boletos_pendentes_mensal_julho = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='7').all()
        boletos_pagos_mensal_julho = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='7').all()
        boletos_julho = db.session.query(Cliente_Dados).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='7').all()

        boletos_pendentes_mensal_agosto = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='8').all()
        boletos_pagos_mensal_agosto = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='8').all()
        boletos_agosto = db.session.query(Cliente_Dados).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='8').all()

        boletos_pendentes_mensal_setembro = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='9').all()
        boletos_pagos_mensal_setembro = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='9').all()
        boletos_setembro = db.session.query(Cliente_Dados).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='9').all()

        boletos_pendentes_mensal_outubro = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='10').all()
        boletos_pagos_mensal_outubro = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='10').all()
        boletos_outubro = db.session.query(Cliente_Dados).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='10').all()

        boletos_pendentes_mensal_novembro = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='11').all()
        boletos_pagos_mensal_novembro = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='11').all()
        boletos_novembro = db.session.query(Cliente_Dados).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='11').all()

        boletos_pendentes_mensal_dezembro = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='1').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='12').all()
        boletos_pagos_mensal_dezembro = db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id=='2').filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='12').all()
        boletos_dezembro = db.session.query(Cliente_Dados).filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_atual.id).filter(Cliente_Dados.mes_id=='12').all()


        mes_ano = db.session.query(Mes_Ano).order_by(asc(Mes_Ano.id)).options(joinedload(Mes_Ano.mes_ano_boleto)).filter(Mes_Ano.ano_id==ano_atual.id).all()
        

        return render_template("relatorio.html", token_acesso1=token_acesso1,token_acesso2=token_acesso2,token_acesso3=token_acesso3,gera_letra1=gera_letra1,gera_letra2 = gera_letra2, mes_ano = mes_ano, clientes_inadimplentes_mensal=clientes_inadimplentes_mensal,clientes_inadimplentes_anual=clientes_inadimplentes_anual, ano_atual = ano_atual, mes_atual = mes_atual,
                clientes_adimplentes_mensal=clientes_adimplentes_mensal,clientes_adimplentes_anual=clientes_adimplentes_anual,status = db.session.query(Status).order_by(asc(Status.id)).all(), clientes = db.session.query(Cliente).all(), boletos_pendentes_anual = boletos_pendentes_anual[0],boletos_pagos_anual=boletos_pagos_anual[0],boletos_pendentes_mensal=boletos_pendentes_mensal[0],boletos_pagos_mensal=boletos_pagos_mensal[0],
                boletos_pendentes_mensal_janeiro=boletos_pendentes_mensal_janeiro, boletos_pagos_mensal_janeiro=boletos_pagos_mensal_janeiro,boletos_janeiro=boletos_janeiro, boletos_pendentes_mensal_fevereiro=boletos_pendentes_mensal_fevereiro, boletos_pagos_mensal_fevereiro=boletos_pagos_mensal_fevereiro, boletos_fevereiro=boletos_fevereiro,
                boletos_pendentes_mensal_marco=boletos_pendentes_mensal_marco, boletos_pagos_mensal_marco=boletos_pagos_mensal_marco,boletos_marco=boletos_marco,
                boletos_pendentes_mensal_abril=boletos_pendentes_mensal_abril,boletos_pagos_mensal_abril=boletos_pagos_mensal_abril,boletos_abril=boletos_abril, boletos_pendentes_mensal_maio=boletos_pendentes_mensal_maio,boletos_maio=boletos_maio,
                boletos_pagos_mensal_maio=boletos_pagos_mensal_maio, boletos_pendentes_mensal_junho=boletos_pendentes_mensal_junho, boletos_pagos_mensal_junho=boletos_pagos_mensal_junho,boletos_junho=boletos_junho,
                boletos_pendentes_mensal_julho=boletos_pendentes_mensal_julho,boletos_pagos_mensal_julho=boletos_pagos_mensal_julho,boletos_julho=boletos_julho,boletos_pendentes_mensal_agosto=boletos_pendentes_mensal_agosto,boletos_agosto=boletos_agosto,
                boletos_pagos_mensal_agosto=boletos_pagos_mensal_agosto, boletos_pendentes_mensal_setembro=boletos_pendentes_mensal_setembro, boletos_pagos_mensal_setembro=boletos_pagos_mensal_setembro,boletos_setembro=boletos_setembro,
                boletos_pendentes_mensal_outubro=boletos_pendentes_mensal_outubro, boletos_pagos_mensal_outubro=boletos_pagos_mensal_outubro,boletos_outubro=boletos_outubro, boletos_pendentes_mensal_novembro=boletos_pendentes_mensal_novembro,boletos_novembro=boletos_novembro,
                boletos_pagos_mensal_novembro=boletos_pagos_mensal_novembro,   boletos_pendentes_mensal_dezembro=boletos_pendentes_mensal_dezembro, boletos_pagos_mensal_dezembro=boletos_pagos_mensal_dezembro,boletos_dezembro=boletos_dezembro, 
                dados_boletos_pendentes_anual=dados_boletos_pendentes_anual,dados_boletos_pagos_anual=dados_boletos_pagos_anual,dados_boletos_pendentes_mensal=dados_boletos_pendentes_mensal,dados_boletos_pagos_mensal=dados_boletos_pagos_mensal)
#ROTA DADOS MENSAL
@app.route('/dados_mensal/<int:ano_id>_<token_acesso1>_<int:mes_id>_<token_acesso2>_<int:usuario_id>_<token_acesso3>', methods=['GET', 'POST'])
@login_required
def dados_mensal(ano_id, mes_id,token_acesso1,token_acesso2,token_acesso3, usuario_id):
    token_acesso1 = gera_token()
    token_acesso2 = gera_token()
    token_acesso3 = gera_token()

    if current_user.id != usuario_id:
        return render_template('acess_negado.html'), 403
    else:
        usuario = db.session.query(Usuarios).filter(Usuarios.id==usuario_id).first()

        mes = db.session.query(Meses).filter(Meses.id==mes_id).first()
        ano_atual = db.session.query(Anos).filter(Anos.id==ano_id).first()
        #CRIAR CONTADOR PARA QUEM CONTRATOU O SERVIÇO
        clientes_inadimplentes_mensal= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "1").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_id).filter(Cliente_Dados.mes_id==mes_id).all()
        clientes_inadimplentes_anual= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "1").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_id).all()
                    
        #CRIAR CONTADOR PARA QUEM NÃO CONTRATOU O SERVIÇO
        clientes_adimplentes_mensal= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "2").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_id).filter(Cliente_Dados.mes_id==mes_id).all()
        clientes_adimplentes_anual= db.session.query(Cliente_Dados).filter(Cliente_Dados.status_id == "2").filter(Cliente_Dados.empresa_id==usuario.empresa_id).filter(Cliente_Dados.ano_id==ano_id).all() 

        #DADOS ANUAIS
        boletos_pendentes_anual = db.session.query(func.sum(Boleto.valor)).filter(Boleto.status_id=='1').filter(Boleto.ano_id==ano_id).filter(Boleto.empresa_id==usuario.empresa_id).first()
        boletos_pagos_anual = db.session.query(func.sum(Boleto.valor_pago)).filter(Boleto.status_id=='2').filter(Boleto.ano_id==ano_id).filter(Boleto.empresa_id==usuario.empresa_id).first()
            
        #DADOS MENSAIS
        boletos_pendentes_mensal = db.session.query(func.sum(Boleto.valor)).filter(Boleto.status_id=='1').filter(Boleto.ano_id==ano_id).filter(Boleto.mes_id==mes_id).filter(Boleto.empresa_id==usuario.empresa_id).first()
        boletos_pagos_mensal = db.session.query(func.sum(Boleto.valor_pago)).filter(Boleto.status_id=='2').filter(Boleto.ano_id==ano_id).filter(Boleto.mes_id==mes_id).filter(Boleto.empresa_id==usuario.empresa_id).first()
        
        mes_ano = db.session.query(Mes_Ano).filter(Mes_Ano.ano_id==ano_id).filter(Mes_Ano.mes_id==mes_id).all()

        return render_template('mensal.html',mes_ano = mes_ano,clientes_inadimplentes_mensal=clientes_inadimplentes_mensal, clientes_adimplentes_mensal=clientes_adimplentes_mensal, clientes_inadimplentes_anual=clientes_inadimplentes_anual,
        clientes_adimplentes_anual=clientes_adimplentes_anual,token_acesso1=token_acesso1,token_acesso2=token_acesso2,token_acesso3=token_acesso3, mes = mes, ano_atual = ano_atual,
        boletos_pendentes_anual = boletos_pendentes_anual[0], boletos_pagos_anual = boletos_pagos_anual[0],boletos_pendentes_mensal=boletos_pendentes_mensal[0],boletos_pagos_mensal=boletos_pagos_mensal[0])
        

#ROTA PARA ENVIAR EMAIL
@app.route("/sendemail/<cliente_id>_<boleto_id>",methods=['GET','POST'] )
@login_required
def envia_email(cliente_id, boleto_id):
    cliente_dados = db.session.query(Cliente_Dados).filter(Cliente_Dados.cliente_id==cliente_id).filter(Cliente_Dados.boleto_id==boleto_id).first()
    cliente = db.session.query(Cliente).filter(Cliente.id==cliente_id).first()
    if request.method == 'POST':
        email_usuario_logado = request.form['email_usuario_logado']
        cliente.nome = request.form['nome']
        cliente.email = request.form['email']
        assunto_email = request.form['assunto_email']
        print(assunto_email)
        texto = request.form['texto_mensagem']              
        
        message = texto
        
        # setup the parameters of the message 
        password = "mboi ugrx dang qlbe"
        msg['From'] = 'adm.crm2023@gmail.com'
        msg['To'] = cliente.email
        msg['Subject'] = assunto_email
        
        # add in the message body 
        msg.attach(MIMEText(message, 'plain'))        
        #create server 
        server = smtplib.SMTP('smtp.gmail.com: 587')        
        server.starttls()
        
        # Login Credentials for sending the mail 
        server.login(msg['From'], password)        
        
        # send the message via the server. 
        server.sendmail(msg['From'], msg['To'], msg.as_string())        
        server.quit()

        print("successfully sent email to %s:" % (msg['To']))
        flash(f'Email enviado com sucesso para {cliente.email}!')
        
        #ADICIONA HISTÓRICO DE MENSAGENS ENVIADAS AO CLIENTE VIA EMAIL
        data_atual = datetime.now(pytz.timezone('America/Sao_Paulo'))
        data_em_texto = data_atual.strftime('%d/%m/%Y às %H:%M')
        email = Mensagem(origem = "E-mail", assunto = assunto_email, texto = texto, data_envio = data_em_texto, cliente_id = cliente.id, cliente_dados = cliente_dados.id)
        db.session.add(email)
        db.session.commit()

        print("\nDados salvos no banco\n")

        

        return redirect(url_for('home'))


#ROTA PARA CRIAR HISTÓRICO DE MENSAGENS ENVIADAS AO CLIENTE VIA WHATSAPP
@app.route("/salvar_mensagem/<cliente_id>_<boleto_id>", methods = ['GET', 'POST'])
@login_required
def salva_mensagem(cliente_id, boleto_id):
    cliente_dados = db.session.query(Cliente_Dados).filter(Cliente_Dados.cliente_id==cliente_id).filter(Cliente_Dados.boleto_id==boleto_id).first()
    cliente = db.session.query(Cliente).filter(Cliente.id==cliente_id).first()
    if request.method == 'POST':
        assunto = request.form['assuntoMensagem']
        texto = request.form['texto_mensagem']
        data = datetime.now(pytz.timezone('America/Sao_Paulo'))
        data_atual = data.strftime('%d/%m/%Y às %H:%M')
        whatsapp = Mensagem(origem = "WhatsApp", assunto = assunto, texto = texto, data_envio = data_atual, cliente_id = cliente.id, cliente_dados_id = cliente_dados.id)
        db.session.add(whatsapp)
        db.session.commit()

        print("\nDados salvos no banco\n")        

        return redirect(url_for('home'))


@app.route("/search_data/<nome>", methods = ['GET', 'POST'])
@login_required
def search_data(nome):
    res = db.session.query(Usuarios).filter(Usuarios.nome==nome).first()
    
    if res is None:
        print('ERROR 500')
        return jsonify({'error': 'Cliente não encontrado'}), 500
    else:
        list_clientes = [res.dict_users()]
        print(list_clientes)
        return jsonify(list_clientes)
            


@app.route("/get_topicos",methods=['GET','POST'])
@login_required
def get_topicos():
    topico = db.session.query(Topico).all()

    return jsonify([topico.to_dict() for topico in topico])
    

    

@app.route("/insert_novo_topico", methods=['GET', 'POST'])
@login_required
def novo_topico():
    new_topico = request.get_json()
    db.session.add(Topico(topico=new_topico))
    db.session.commit()
    return redirect(url_for('home'))

#ROTAS PARA O SISTEMA DE INSERÇÃO DE 'TEXTOS'
#PÁGINA PRINCIPAL
@app.route("/inicio", methods = ['GET','POST'])
@login_required
def inicio():

    return render_template("inicio.html", textos = db.session.query(Textos).options(joinedload(Textos.texto_topico)).order_by(asc(Textos.id)).all(),
                           topicos = db.session.query(Topico).options(joinedload(Topico.topico_texto)).order_by(asc(Topico.id)).all())


#INSERINDO NOVO TÓPICO À TABELA TÓPICOS
@app.route("/insere_topico", methods = ['GET', 'POST'])
def insere_topico():
    if request.method == 'POST':
        novo_topico = request.form['novo_topico']
        topico = Topico(topico = novo_topico)
        db.session.add(topico)
        db.session.commit()

        print("\nNovo tópico adicionado com sucesso\n")

        return redirect(url_for('inicio')) 
    

#INSERINDO TEXTO NA TABELA 'TEXTOS'
@app.route("/insere_texto", methods = ['GET', 'POST'])
def insere_texto():
    if request.method == 'POST':
        topico = request.form['novo_topico']
        texto= request.form['texto_mensagem']

        insert_texto = Textos(texto = texto , topico_id = topico)
        db.session.add(insert_texto)
        db.session.commit()

        print('\nTexto salvo com sucesso!\n')
        flash('Texto salvo com sucesso!')

        return redirect(url_for('inicio'))

#ATUALIZA UM TEXTO
@app.route('/inicio/atualiza_texto/<int:id>', methods = ['GET', 'POST'])
def atualiza_texto(id):
    update_texto = db.session.query(Textos).filter(Textos.id==id).first()
    if request.method == 'POST':
        
        update_texto.texto = request.form['texto_atualizado']
        db.session.commit()

        print('\nTexto atualizado com sucesso!\n')
        flash('Texto atualizado com sucesso!')

        return redirect('/inicio')


#EXCLUI TÓPICO
@app.route('/inicio/apaga_topico/<int:id>')
def delete_topico(id):
    
    topico_delete= db.session.query(Topico).filter(Topico.id==id).first()
    db.session.delete(topico_delete)
    db.session.commit()

    """"
    EXIBINDO, NO TEMPLATE HTML, A MENSAGEM DE CONFIRMAÇÃO DA
    EXCLUSÃO DE UM REGISTRO
    
    """
    print('\nTópico excluído com sucesso!\n')
    flash('Tópico excluído com sucesso!')

    return redirect(url_for('inicio'))

#EXCLUI TEXTO
@app.route('/inicio/apaga_texto/<int:id>')
def delete_texto(id):
    
    texto_delete= db.session.query(Textos).filter(Textos.id==id).first()
    db.session.delete(texto_delete)
    db.session.commit()

    """"
    EXIBINDO, NO TEMPLATE HTML, A MENSAGEM DE CONFIRMAÇÃO DA
    EXCLUSÃO DE UM REGISTRO
    
    """
    print('\nTexto excluído com sucesso!\n')
    flash('Texto excluído com sucesso!')

    return redirect(url_for('inicio'))


#ROTA PARA FAZER LOGOUT DO SISTEMA
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login')) #Redireciona o usuário para tela de login



if __name__=="__main__":
    app.run(debug=True,host='0.0.0.0')
