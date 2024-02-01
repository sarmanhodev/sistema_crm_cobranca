from main import db, app
from flask_login import UserMixin
from sqlalchemy import Text, DECIMAL
from werkzeug.security import generate_password_hash, check_password_hash
from main import login_manager
from datetime import datetime



@login_manager.user_loader
def get_user(user_id):
    return Usuarios.query.filter_by(id=user_id).first()

class Usuarios (db.Model, UserMixin):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(256), unique = True, nullable= False)
    email = db.Column(db.String(50), unique = True, nullable=False)
    telefone = db.Column(db.String(256), unique = True, nullable= True)
    password = db.Column(db.String(250), unique=True, nullable = False)
    empresa_id = db.Column(db.Integer,db.ForeignKey("empresa.id"), unique = False, nullable = False)
    acesso_id = db.Column(db.Integer, unique=False, nullable = False)
   
    
    usuario_boleto = db.relationship('Boleto', back_populates = 'boleto_usuario', lazy = True)
    usuario_empresa = db.relationship('Empresa', back_populates = 'empresa_usuario', lazy = True)
    usuarios_cliente = db.relationship("Cliente", back_populates="cliente_usuario", lazy = True)
    usuario_cliente_dados = db.relationship('Cliente_Dados', back_populates = 'cliente_dados_usuario', lazy = True)

    user_processo = db.relationship('Usuario_Processo', back_populates="processo_user", lazy = True)
    usuario_processo_secondary = db.relationship('Controle_Processos', secondary = 'usuario_processo', back_populates="processo_usuario_secondary", lazy = True)

    def __init__(self, nome, email,telefone, password,empresa_id,acesso_id):
        self.nome = nome
        self.password = generate_password_hash(password)
        self.email = email
        self.telefone = telefone
        self.empresa_id = empresa_id
        self.acesso_id = acesso_id
    
    def verifica_senha(self, password):
        return check_password_hash(self.password, password)

    def dict_users(self):
        return {"id":self.id, "nome": self.nome, "email": self.email, "telefone":self.telefone, "empresa_id":self.empresa_id, "acesso_id":self.acesso_id} 


class Empresa(db.Model, UserMixin):
    __tablename__ = 'empresa'
    id = db.Column(db.Integer, primary_key = True)
    nome_empresa = db.Column(db.String(256), unique=True, nullable=False)

    empresa_usuario = db.relationship('Usuarios', back_populates = 'usuario_empresa', lazy = True)
    empresa_cliente = db.relationship("Cliente", back_populates="cliente_empresa", lazy = True)
    empresa_cliente_dados = db.relationship('Cliente_Dados', back_populates = 'cliente_dados_empresa', lazy = True)
    empresa_boleto = db.relationship('Boleto', back_populates = 'boleto_empresa', lazy = True)



class Mes_Ano(db.Model,UserMixin):
    __tablename__="mes_ano"
    id = db.Column(db.Integer, primary_key=True)
    mes_id=db.Column(db.Integer,db.ForeignKey("meses.id"), unique=False)
    ano_id=db.Column(db.Integer,db.ForeignKey("anos.id"), unique=False)

    mes_mes_ano = db.relationship('Meses', back_populates = 'mes_mes_mes', lazy = True)
    mes_ano_ano = db.relationship('Anos', back_populates = 'ano_ano_ano', lazy = True)
    mes_ano_boleto = db.relationship('Boleto', back_populates = 'boleto_mes_ano', lazy = True)


class Anos(db.Model,UserMixin):
    __tablename__="anos"
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, unique=True, nullable=False)

    ano_ano_ano = db.relationship('Mes_Ano', back_populates = 'mes_ano_ano', lazy = True)
    ano_mes=db.relationship('Meses', secondary="mes_ano", back_populates="mes_ano", lazy=True, overlaps="mes_mes_ano, ano_ano_ano,mes_ano_ano")
    ano_cliente_dados = db.relationship('Cliente_Dados', back_populates = 'cliente_dados_ano', lazy = True)
    ano_ano_cliente = db.relationship('Ano_Cliente', back_populates = 'ano_cliente_ano', lazy = True)
    ano_boleto = db.relationship('Boleto', back_populates= 'boleto_ano', lazy = True)
    ano_cliente_boleto = db.relationship('Cliente_Boleto', back_populates = 'cliente_boleto_ano', lazy = True)
    ano_clientes = db.relationship('Cliente', secondary = 'ano_cliente', back_populates = 'clientes_ano', lazy = True, overlaps="ano_ano_cliente")


class Meses(db.Model,UserMixin):
    __tablename__="meses"
    id = db.Column(db.Integer, primary_key=True)
    mes = db.Column(db.String(256), unique=True, nullable=False)

    mes_mes_mes = db.relationship('Mes_Ano', back_populates = 'mes_mes_ano', lazy = True,overlaps="mes_mes_ano,mes_mes_mes, ano_mes")
    mes_ano=db.relationship('Anos', secondary="mes_ano", back_populates="ano_mes", lazy=True, overlaps="ano_ano_ano,mes_ano_ano,mes_mes_ano,mes_mes_mes")  
    mes_cliente_dados = db.relationship('Cliente_Dados', back_populates = 'cliente_dados_mes', lazy = True)
    mes_mes_cliente = db.relationship('Mes_Cliente', back_populates = 'mes_cliente_mes', lazy = True)
    mes_boleto = db.relationship('Boleto', back_populates = 'boleto_mes', lazy = True)
    meses_cliente = db.relationship('Cliente', secondary = 'mes_cliente', back_populates = 'cliente_mes', lazy = True, overlaps="mes_mes_cliente")
    mes_cliente_boleto = db.relationship('Cliente_Boleto', back_populates = 'cliente_boleto_mes', lazy = True)


class Cliente (db.Model, UserMixin):
    __tablename__ = "cliente"    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable = False)
    nome = db.Column(db.String(256), unique = False, nullable= False)
    email = db.Column(db.String(50), unique = False, nullable=False)
    telefone = db.Column(db.String(50), unique = False, nullable=False)
    empresa_id = db.Column(db.Integer,db.ForeignKey("empresa.id"))
    usuario_id = db.Column(db.Integer,db.ForeignKey("usuarios.id"))     
   
    cliente_mensagem = db.relationship("Mensagem", back_populates="mensagem_cliente", lazy = True)
    cliente_empresa = db.relationship("Empresa", back_populates="empresa_cliente", lazy = True)
    cliente_usuario = db.relationship("Usuarios", back_populates="usuarios_cliente", lazy = True)
    cliente_cliente_dados = db.relationship('Cliente_Dados', back_populates = 'cliente_dados_cliente', lazy = True)
    cliente_cliente_boleto = db.relationship('Cliente_Boleto', back_populates = 'cliente_boleto_cliente', lazy = True)
    clientes_boleto = db.relationship('Boleto', secondary = 'cliente_boleto', back_populates = 'boleto_cliente', lazy = True, overlaps="cliente_cliente_boleto")
    cliente_mes_cliente = db.relationship('Mes_Cliente', back_populates = 'mes_cliente_cliente', lazy = True, overlaps="meses_cliente")
    cliente_ano_cliente = db.relationship('Ano_Cliente', back_populates = 'ano_cliente_cliente', lazy = True, overlaps="ano_clientes")
    cliente_mes = db.relationship('Meses', secondary = 'mes_cliente', back_populates = 'meses_cliente', lazy = True, overlaps="mes_mes_cliente, cliente_mes_cliente")
    clientes_ano = db.relationship('Anos', secondary = 'ano_cliente', back_populates = 'ano_clientes', lazy = True,overlaps="ano_ano_cliente, cliente_ano_cliente")

    def as_dict(self):
        return {'id':self.id,'nome': self.nome, 'email':self.email,'telefone':self.telefone,'mensagem': {'origem':[c.origem for c in self.cliente_mensagem], 'assunto':[c.assunto for c in self.cliente_mensagem],'texto':[c.texto for c in self.cliente_mensagem],
            'data_envio':[c.data_envio for c in self.cliente_mensagem]}}


class Ano_Cliente(db.Model,UserMixin):
    __tablename__ = 'ano_cliente'
    id = db.Column(db.Integer, primary_key=True)
    ano_id = db.Column(db.Integer,db.ForeignKey("anos.id"))
    cliente_id = db.Column(db.Integer,db.ForeignKey("cliente.id"))

    ano_cliente_cliente = db.relationship('Cliente', back_populates = 'cliente_ano_cliente', lazy = True, overlaps="ano_clientes,clientes_ano")
    ano_cliente_ano = db.relationship('Anos', back_populates = 'ano_ano_cliente', lazy = True, overlaps="ano_clientes,clientes_ano")


class Mes_Cliente(db.Model,UserMixin):
    __tablename__ = 'mes_cliente'
    id = db.Column(db.Integer, primary_key=True)
    mes_id = db.Column(db.Integer,db.ForeignKey("meses.id"))
    cliente_id = db.Column(db.Integer,db.ForeignKey("cliente.id"))

    mes_cliente_cliente = db.relationship('Cliente', back_populates = 'cliente_mes_cliente', lazy = True, overlaps="cliente_mes,meses_cliente")
    mes_cliente_mes = db.relationship('Meses', back_populates = 'mes_mes_cliente', lazy = True, overlaps="cliente_mes,meses_cliente")


class Boleto(db.Model, UserMixin):
    __tablename__ = "boleto"
    id = db.Column(db.Integer, primary_key = True)
    numero_boleto = db.Column(db.String(256), unique = False, nullable = False)
    data_vencimento = db.Column(db.String(256), unique = False, nullable = True)
    data_pagamento = db.Column(db.String(256), unique = False, nullable = True)
    valor = db.Column(db.DECIMAL(10,2), unique = False, nullable = False)
    valor_multa = db.Column(db.DECIMAL(10,2), unique = False, nullable = False)
    status_id = db.Column(db.Integer,db.ForeignKey("status.id"))
    valor_pago = db.Column(db.DECIMAL(10,2), unique = False, nullable = True)
    juros_diarios = db.Column(db.DECIMAL(10,2), unique = False, nullable = True)
    ano_id = db.Column(db.Integer,db.ForeignKey("anos.id"))
    mes_id = db.Column(db.Integer,db.ForeignKey("meses.id"))
    mes_ano_id = db.Column(db.Integer,db.ForeignKey("mes_ano.id"))
    usuario_id = db.Column(db.Integer,db.ForeignKey("usuarios.id"))
    empresa_id = db.Column(db.Integer,db.ForeignKey("empresa.id"))
    observacoes = db.Column(db.Text, unique = False, nullable = True)

    boleto_cliente_boleto = db.relationship('Cliente_Boleto', back_populates = 'cliente_boleto_boleto', lazy = True, overlaps="clientes_boleto")
    boleto_cliente = db.relationship('Cliente', secondary = 'cliente_boleto', back_populates = 'clientes_boleto', lazy = True, overlaps="cliente_cliente_boleto, boleto_cliente_boleto")
    boleto_cliente_dados = db.relationship('Cliente_Dados', back_populates = 'cliente_dados_boleto', lazy = True)
    boleto_status = db.relationship('Status', back_populates = 'status_boleto', lazy = True)
    boleto_mes = db.relationship('Meses',back_populates = 'mes_boleto', lazy =True)
    boleto_ano = db.relationship('Anos', back_populates = 'ano_boleto', lazy = True)
    boleto_mes_ano = db.relationship('Mes_Ano', back_populates = 'mes_ano_boleto', lazy = True)
    boleto_usuario = db.relationship('Usuarios', back_populates = 'usuario_boleto', lazy = True)
    boleto_empresa = db.relationship('Empresa', back_populates = 'empresa_boleto', lazy = True)


class Cliente_Boleto(db.Model, UserMixin):
    __tablename__ = "cliente_boleto"
    id = db.Column(db.Integer, primary_key = True)
    cliente_id = db.Column(db.Integer,db.ForeignKey("cliente.id"))
    boleto_id = db.Column(db.Integer,db.ForeignKey("boleto.id"))
    ano_id = db.Column(db.Integer,db.ForeignKey("anos.id"), unique=False)
    mes_id = db.Column(db.Integer,db.ForeignKey("meses.id"), unique=False)

    cliente_boleto_cliente = db.relationship('Cliente', back_populates = 'cliente_cliente_boleto', lazy = True,overlaps="boleto_cliente,clientes_boleto")
    cliente_boleto_boleto = db.relationship('Boleto', back_populates = 'boleto_cliente_boleto', lazy = True,overlaps="boleto_cliente,clientes_boleto")
    cliente_boleto_ano = db.relationship('Anos', back_populates = 'ano_cliente_boleto', lazy = True)
    cliente_boleto_mes = db.relationship('Meses', back_populates = 'mes_cliente_boleto', lazy = True)


class Data_Contato (db.Model, UserMixin):
    __tablename__="data_contato" 
    id = db.Column(db.Integer, primary_key = True)
    primeiro_contato = db.Column(db.String(256), unique = False, nullable = False)
    proximo_contato = db.Column(db.String(256), unique = False, nullable = True)
    ultimo_contato = db.Column(db.String(256), unique = False, nullable = True)  
    
    contato_cliente_dados = db.relationship('Cliente_Dados', back_populates = 'cliente_dados_contato', lazy = True)

    
class Status (db.Model, UserMixin):
    __tablename__ = "status"
    id = id = db.Column(db.Integer, primary_key = True)
    status = db.Column(db.String(256), unique = True, nullable = False)

   
    status_cliente_dados = db.relationship('Cliente_Dados', back_populates = 'cliente_dados_status', lazy = True)
    status_boleto = db.relationship('Boleto', back_populates = 'boleto_status', lazy = True)

    def __len__(self):
        return len(self.status_cliente)
    

class Cliente_Dados(db.Model, UserMixin):
    __tablename__ = "cliente_dados"
    id = db.Column(db.Integer, primary_key = True)
    cliente_id = db.Column(db.Integer,db.ForeignKey("cliente.id"))
    boleto_id = db.Column(db.Integer,db.ForeignKey("boleto.id"))
    status_id = db.Column(db.Integer,db.ForeignKey("status.id"))
    data_contato_id = db.Column(db.Integer,db.ForeignKey("data_contato.id"))
    topico_id = db.Column(db.Integer,db.ForeignKey("topico.id"))
    empresa_id = db.Column(db.Integer,db.ForeignKey("empresa.id"))
    usuario_id = db.Column(db.Integer,db.ForeignKey("usuarios.id"))
    ano_id = db.Column(db.Integer,db.ForeignKey("anos.id"))
    mes_id = db.Column(db.Integer,db.ForeignKey("meses.id"))

    #RELACIONAMENTOS
    cliente_dados_empresa = db.relationship('Empresa', back_populates = 'empresa_cliente_dados', lazy = True)
    cliente_dados_usuario = db.relationship('Usuarios', back_populates = 'usuario_cliente_dados', lazy = True)
    cliente_dados_cliente = db.relationship('Cliente', back_populates = 'cliente_cliente_dados', lazy= True)
    cliente_dados_boleto = db.relationship('Boleto', back_populates = 'boleto_cliente_dados', lazy = True)
    cliente_dados_contato = db.relationship('Data_Contato', back_populates = 'contato_cliente_dados', lazy = True)
    cliente_dados_status = db.relationship('Status', back_populates = 'status_cliente_dados', lazy = True)
    cliente_dados_topico = db.relationship('Topico', back_populates = 'topico_cliente_dados', lazy = True)
    cliente_dados_mensagem = db.relationship('Mensagem', back_populates = 'mensagem_cliente_dados', lazy = True)
    cliente_dados_ano = db.relationship('Anos', back_populates = 'ano_cliente_dados', lazy = True)
    cliente_dados_mes = db.relationship('Meses', back_populates = 'mes_cliente_dados', lazy = True)

class Mensagem (db.Model, UserMixin):
    __tablename__ = "mensagens"
    id = db.Column(db.Integer, primary_key = True)
    origem = db.Column(db.String(256), unique = False, nullable = True)
    assunto = db.Column(db.String(256), unique = False, nullable = True)
    texto = db.Column(db.Text, unique = False, nullable = False)
    data_envio = db.Column(db.Text, unique = False, nullable = True)    
    #CHAVE ESTRANGEIRA DA TABELA CLIENTE
    cliente_id = db.Column(db.Integer,db.ForeignKey("cliente.id"))
    cliente_dados_id = db.Column(db.Integer,db.ForeignKey("cliente_dados.id"))

    #RELACIONAMENTO ENTRE AS TABELAS MENSAGEM E CLIENTE
    mensagem_cliente = db.relationship("Cliente", back_populates="cliente_mensagem", lazy= True)
    mensagem_cliente_dados = db.relationship('Cliente_Dados', back_populates = 'cliente_dados_mensagem', lazy = True)


#TABELAS PARA O SISTEMA DO DR LYMARK
class Topico(db.Model, UserMixin):
    __tablename__ = "topico"    
    id = db.Column(db.Integer, primary_key = True)
    topico = db.Column(db.String(256), unique = False, nullable = False)

    #RELACIONAMENTO ENTRE AS TABELAS TOPICO E TEXTOS
    topico_texto = db.relationship("Textos", back_populates = "texto_topico", lazy = True)
    topico_cliente_dados = db.relationship('Cliente_Dados', back_populates = 'cliente_dados_topico', lazy = True)

    def __init__(self,topico):
        self.topico=topico

    def to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = str(getattr(self, key))
            else:
                result[key] = getattr(self, key)
        return result


class Textos(db.Model,UserMixin):
    __tablename__ = "textos"       
    id = db.Column(db.Integer, primary_key = True)
    texto = db.Column(db.Text, unique = False, nullable = False)
    topico_id = db.Column(db.Integer,db.ForeignKey("topico.id"))

    #RELACIONAMENTO ENTRE AS TABELAS TEXTOS E TOPICOS
    texto_topico = db.relationship("Topico", back_populates = "topico_texto", lazy = True)


