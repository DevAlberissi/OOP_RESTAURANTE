import os
from datetime import datetime
import time

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.exc import IntegrityError 

Base = declarative_base()
engine = create_engine('sqlite:///restaurante.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

#====== TABELA ASSOCIATIVA ENTRE PEDIDO E PRODUTO ======
pedido_produto = Table(
    'pedido_produto', Base.metadata,
    Column('pedido_id', ForeignKey('pedidos.id'), primary_key=True),
    Column('produto_id', ForeignKey('produtos.id'), primary_key=True)
)

#====== CLASSES COM SQLALCHEMY ======

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    _nome = Column('nome', String)
    _cpf = Column('cpf', String, unique=True)
    _idade = Column('idade', Integer)
    _data_nascimento = Column('data_nascimento', Date)

    pedidos = relationship("Pedido", back_populates="cliente")
    pagamentos = relationship("Pagamento", back_populates="cliente")

    def __init__(self, nome, cpf, idade, data_nascimento):
        self._nome = nome
        self._cpf = cpf
        self._idade = idade
        self._data_nascimento = data_nascimento

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = value

    @property
    def cpf(self):
        return self._cpf

    @property
    def idade(self):
        return self._idade

    @idade.setter
    def idade(self, value):
        self._idade = value

    @property
    def data_nascimento(self):
        return self._data_nascimento

    @data_nascimento.setter
    def data_nascimento(self, value):
        self._data_nascimento = value

class Funcionario(Base):
    __tablename__ = 'funcionarios'
    id = Column(Integer, primary_key=True)
    _nome = Column('nome', String)
    _cpf = Column('cpf', String, unique=True)
    _idade = Column('idade', Integer)
    _data_nascimento = Column('data_nascimento', Date)
    _cargo = Column('cargo', String)
    _salario = Column('salario', Float)

    def __init__(self, nome, cpf, idade, data_nascimento, cargo, salario):
        self._nome = nome
        self._cpf = cpf
        self._idade = idade
        self._data_nascimento = data_nascimento
        self._cargo = cargo
        self._salario = salario

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = value

    @property
    def cpf(self):
        return self._cpf

    @property
    def idade(self):
        return self._idade

    @idade.setter
    def idade(self, value):
        self._idade = value

    @property
    def data_nascimento(self):
        return self._data_nascimento

    @data_nascimento.setter
    def data_nascimento(self, value):
        self._data_nascimento = value

    @property
    def cargo(self):
        return self._cargo

    @cargo.setter
    def cargo(self, value):
        self._cargo = value

    @property
    def salario(self):
        return self._salario

    @salario.setter
    def salario(self, value):
        self._salario = value

class Produto(Base):
    __tablename__ = 'produtos'
    id = Column(Integer, primary_key=True)
    _nome = Column('nome', String)
    _valor = Column('valor', Float)
    _quantidade = Column('quantidade', Integer)

    def __init__(self, nome, valor, quantidade=1):
        self._nome = nome
        self._valor = valor
        self._quantidade = quantidade

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = value

    @property
    def valor(self):
        return self._valor

    @valor.setter
    def valor(self, value):
        self._valor = value

    @property
    def quantidade(self):
        return self._quantidade

    @quantidade.setter
    def quantidade(self, value):
        self._quantidade = value

class Pagamento(Base):
    __tablename__ = 'pagamentos'
    id = Column(Integer, primary_key=True)
    _tipo = Column('tipo', String)
    _valor = Column('valor', Float)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))

    cliente = relationship("Cliente", back_populates="pagamentos")

    def __init__(self, tipo, valor, cliente):
        self._tipo = tipo
        self._valor = valor
        self.cliente = cliente

    @property
    def tipo(self):
        return self._tipo

    @property
    def valor(self):
        return self._valor

class EstoqueItem(Base):
    __tablename__ = 'estoque'
    id = Column(Integer, primary_key=True)
    _nome = Column('nome', String)
    _quantidade = Column('quantidade', Integer)
    _valor = Column('valor', Float)

    def __init__(self, nome, quantidade, valor):
        self._nome = nome
        self._quantidade = quantidade
        self._valor = valor

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = value

    @property
    def quantidade(self):
        return self._quantidade

    @quantidade.setter
    def quantidade(self, value):
        self._quantidade = value

    @property
    def valor(self):
        return self._valor

    @valor.setter
    def valor(self, value):
        self._valor = value

class Pedido(Base):
    __tablename__ = 'pedidos'
    id = Column(Integer, primary_key=True)
    _comanda = Column('comanda', String)
    _valor = Column('valor', Float)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))

    cliente = relationship("Cliente", back_populates="pedidos")
    produtos = relationship("Produto", secondary=pedido_produto)

    def __init__(self, cliente, produtos):
        self.cliente = cliente
        self._produtos = []
        self._valor = 0.0

        for p in produtos:
            estoque = session.query(EstoqueItem).filter_by(_nome=p._nome).first()
            if estoque and estoque._quantidade > 0:
                self._produtos.append(p)
                estoque._quantidade -= 1
                self._valor += p._valor
            else:
                raise ValueError(f"Produto '{p._nome}' fora de estoque.")

        self._comanda = f"CPF: {cliente._cpf[-3:]}\nPedidos: {len(cliente.pedidos) + 1}"

    @property
    def comanda(self):
        return self._comanda

    @property
    def valor(self):
        return self._valor

    @property
    def produtos(self):
        return self._produtos

class CardapioItem(Base):
    __tablename__ = 'cardapio'
    id = Column(Integer, primary_key=True)
    _nome = Column('nome', String)
    _valor = Column('valor', Float)

    def __init__(self, nome, valor):
        self._nome = nome
        self._valor = valor

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, value):
        self._nome = value

    @property
    def valor(self):
        return self._valor

    @valor.setter
    def valor(self, value):
        self._valor = value

# ====== FUNÇÕES UTILITÁRIAS ======
def exibir_nome_programa():
    print("""
    
████████╗░█████╗░░██████╗████████╗██╗░░░██╗  ██╗░░██╗██╗░░░██╗██████╗░
╚══██╔══╝██╔══██╗██╔════╝╚══██╔══╝╚██╗░██╔╝  ██║░░██║██║░░░██║██╔══██╗
░░░██║░░░███████║╚█████╗░░░░██║░░░░╚████╔╝░  ███████║██║░░░██║██████╦╝
░░░██║░░░██╔══██║░╚═══██╗░░░██║░░░░░╚██╔╝░░  ██╔══██║██║░░░██║██╔══██╗
░░░██║░░░██║░░██║██████╔╝░░░██║░░░░░░██║░░░  ██║░░██║╚██████╔╝██████╦╝
░░░╚═╝░░░╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░░░░╚═╝░░░  ╚═╝░░╚═╝░╚═════╝░╚═════╝░
╚══════╝╚═╝░░╚═╝╚═╝░░░░░╚═╝░░╚═╝╚══════╝╚═════╝░╚═════╝░
      """)

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear') #Para compatibilidade universal

def volta_menu():
    menu_gerenciamento()

def exibir_titulo(titulo):
    limpar_tela()
    print('*' * len(titulo))
    print(titulo)
    print('*' * len(titulo))

def obter_data_formatada(mensagem='Data de Nascimento (DD/MM/AAAA): '):
    while True:
        entrada = input(mensagem)
        try:
            return datetime.strptime(entrada, '%d/%m/%Y').date()
        except ValueError:
            print('Formato inválido! Use DD/MM/AAAA.')

# ====== LOGIN ======
def sistema_login():
    limpar_tela()
    exibir_nome_programa()
    print("******************")
    print("LOGIN DO SISTEMA")
    print("******************\n")

    usuario = input('Login: ').strip()
    senha = input('Senha: ').strip()

    try:
        if usuario.upper() == "ADMIN" and senha.upper() == "ADMIN":
            menu_gerenciamento()
        else:
            print('\nLogin inválido. Tente novamente.\n')
            input('Pressione Enter para continuar...')
            sistema_login()
    except ValueError:
            sistema_login()

# ====== MENU GERAL ======
def menu_gerenciamento():
    limpar_tela()
    exibir_nome_programa()

    while True:
        print("****************")
        print("GERENCIAMENTO")
        print("****************\n")

        print('1. FUNCIONÁRIO')
        print('2. CLIENTE')
        print('3. CARDÁPIO')
        print('4. ESTOQUE_PRODUTO')
        print('5. PAGAMENTO')
        print('6. SAIR')

        try:
            opcao = int(input('Escolha uma opção: '))
            if opcao == 1:
                menu_funcionario()
            elif opcao == 2:
                menu_cliente()
            elif opcao == 3:
                menu_cardapio()
            elif opcao == 4:           
                menu_estoque()
            elif opcao == 5:
                visualizar_pagamentos()
            elif opcao == 6:
                sair()
            else:
                limpar_tela()
                print('Opção inválida! Digite um número de 1 a 6.')
                volta_menu()
        except ValueError:
            limpar_tela()
            print('Entrada inválida! Digite um número inteiro.')
            volta_menu()

# ====== MENU FUNCIONÁRIO ======
def menu_funcionario():
    while True:
        exibir_titulo("OPÇÕES FUNCIONÁRIO")
        print("1. Adicionar Funcionário")
        print("2. Alterar Funcionário")
        print("3. Remover Funcionário")
        print("4. Visualizar Funcionários")
        print("5. Voltar")
        opcao = input("Escolha uma opção: ")
        if opcao == "1":
            nome = input("Nome: ")
            cpf = input("CPF: ")
            idade = int(input("Idade: "))
            data = obter_data_formatada()
            cargo = input("Cargo: ")
            salario = float(input("Salário: "))
            funcionario = Funcionario(nome, cpf, idade, data, cargo, salario)
            try:
                session.add(funcionario)
                session.commit()
                print("Funcionário adicionado com sucesso!")
            except IntegrityError:
                session.rollback()
                print("Erro: Já existe um funcionário com esse CPF.")
        elif opcao == "2":
            cpf = input("Digite o CPF do funcionário: ")
            funcionario = session.query(Funcionario).filter_by(cpf=cpf).first()
            if funcionario:
                funcionario.nome = input(f"Novo nome ({funcionario.nome}): ") or funcionario.nome
                funcionario.cargo = input(f"Novo cargo ({funcionario.cargo}): ") or funcionario.cargo
                salario_input = input(f"Novo salário ({funcionario.salario}): ")
                if salario_input:
                    funcionario.salario = float(salario_input)
                session.commit()
                print("Funcionário alterado com sucesso!")
            else:
                print("Funcionário não encontrado.")
        elif opcao == "3":
            cpf = input("CPF do funcionário a remover: ")
            funcionario = session.query(Funcionario).filter_by(_cpf=cpf).first()
            if funcionario:
                session.delete(funcionario)
                session.commit()
                print("Funcionário removido com sucesso!")
            else:
                print("Funcionário não encontrado.")
        elif opcao == "4":
            limpar_tela()
            funcionarios = session.query(Funcionario).all()
            if not funcionarios:
                print("\nNenhum funcionário cadastrado.\n")
            else:
                print("\n--- LISTA DE FUNCIONÁRIOS ---\n")
                print(f"{'Nome':<25} {'CPF':<15} {'Idade':<7} {'Data Nasc.':<15} {'Cargo':<20} {'Salário':<10}")
                print("-" * 95)
                for f in funcionarios:
                    print(f"{f.nome:<25} {f.cpf:<15} {f.idade:<7} {f.data_nascimento.strftime('%d/%m/%Y'):<15} {f.cargo:<20} R${f.salario:<9.2f}")
                print("-" * 95)
            input("\nPressione Enter para continuar...")
        elif opcao == "5":
            volta_menu()
        else:
            print("Opção inválida.")
            input("\nPressione Enter para continuar...")
            menu_funcionario()

# ====== MENU CLIENTE ======
def menu_cliente():
    while True:
        exibir_titulo('OPÇÕES CLIENTE')
        print('1. Adicionar Cliente')
        print('2. Alterar Cliente')
        print('3. Remover Cliente')
        print('4. Visualizar Clientes')
        print('5. Registrar Pagamento')
        print('6. Voltar')
        opcao = input('Escolha uma opção: ')
        if opcao == '1':
            nome = input('Nome: ')
            cpf = input('CPF: ')
            idade = int(input('Idade: '))
            data = obter_data_formatada()
            cliente = Cliente(nome, cpf, idade, data)
            try:
                session.add(cliente)
                session.commit()
                print('Cliente adicionado com sucesso!')
            except IntegrityError:
                session.rollback()
                print("Erro: Já existe um cliente com esse CPF.")
        elif opcao == '2':
            cpf = input('CPF do cliente: ')
            cliente = session.query(Cliente).filter_by(cpf=cpf).first()
            if cliente:
                cliente.nome = input(f'Novo nome ({cliente.nome}): ') or cliente.nome
                idade_input = input(f'Nova idade ({cliente.idade}): ')
                if idade_input:
                    cliente.idade = int(idade_input)
                cliente.data_nascimento = input(f'Nova data de nascimento ({cliente.data_nascimento}): ') or cliente.data_nascimento
                session.commit()
                print('Cliente alterado com sucesso!')
            else:
                print('Cliente não encontrado.')
        elif opcao == '3':
            cpf = input('CPF do cliente a remover: ')
            cliente = session.query(Cliente).filter_by(cpf=cpf).first()
            if cliente:
                session.delete(cliente)
                session.commit()
                print('Cliente removido com sucesso!')
            else:
                print('Cliente não encontrado.')
        elif opcao == '4':
            limpar_tela()
            clientes = session.query(Cliente).all()
            if not clientes:
                print('\nNenhum cliente cadastrado.\n')
            else:
                print("\n--- LISTA DE CLIENTES ---\n")
                print(f"{'Nome':<25} {'CPF':<15} {'Idade':<7} {'Data Nasc.':<15}")
                print("-" * 65)
                for c in clientes:
                    print(f"{c.nome:<25} {c.cpf:<15} {c.idade:<7} {c.data_nascimento.strftime('%d/%m/%Y'):<15}")
                print("-" * 65)
            input("\nPressione Enter para continuar...")
        elif opcao == "5":
            registrar_pagamento()
        elif opcao == '6':
            volta_menu()
        else:
            print('Opção inválida.')
            input("\nPressione Enter para continuar...")
            menu_cliente()

# ====== MENU CARDÁPIO ======
def menu_cardapio():
    while True:
        exibir_titulo('OPÇÕES DO CARDÁPIO')
        print('1. Adicionar Produto')
        print('2. Alterar Produto')
        print('3. Remover Produto')
        print('4. Visualizar Cardápio')
        print('5. Voltar')
        opcao = input('Escolha uma opção: ')
        
        if opcao == '1':
            nome = input('Nome do Produto: ').strip()
            if not nome:
                print("Nome não pode ser vazio.")
                continue
            try:
                valor = float(input('Valor: '))
                if valor <= 0:
                    print("O valor deve ser maior que zero.")
                    continue
                produto_existente = session.query(CardapioItem).filter_by(nome=nome).first()
                if produto_existente:
                    print("Já existe um produto com esse nome.")
                    continue
                novo_item = CardapioItem(nome=nome, valor=valor)
                session.add(novo_item)
                session.commit()
                print("Produto adicionado com sucesso!")
            except ValueError:
                print("Valor inválido. Digite um número válido.")
        elif opcao == '2':
            nome = input('Nome do Produto a alterar: ').strip()
            produto = session.query(CardapioItem).filter_by(nome=nome).first()
            if produto:
                novo_nome = input(f'Novo nome ({produto.nome}): ').strip()
                if novo_nome:
                    produto.nome = novo_nome
                novo_valor = input(f'Novo valor (R${produto.valor:.2f}): ').strip()
                if novo_valor:
                    try:
                        produto.valor = float(novo_valor)
                    except ValueError:
                        print("Valor inválido. Alteração de valor ignorada.")
                session.commit()
                print("Produto alterado com sucesso!")
            else:
                print("Produto não encontrado.")
        elif opcao == '3':
            nome = input('Nome do Produto a remover: ').strip()
            produto = session.query(CardapioItem).filter_by(_nome=nome).first()
            if produto:
                session.delete(produto)
                session.commit()
                print("Produto removido com sucesso!")
            else:
                print("Produto não encontrado.")
        elif opcao == '4':
            limpar_tela()
            itens = session.query(CardapioItem).all()
            if not itens:
                print("\nNenhum produto no cardápio.\n")
            else:
                print("\n--- CARDÁPIO ---\n")
                print(f"{'Nome do Produto':<30} {'Valor':<10}")
                print("-" * 40)
                for item in itens:
                    print(f'{item.nome:<30} R${item.valor:<9.2f}')
                print("-" * 40)
            input("\nPressione Enter para continuar...")
        elif opcao == '5':
            volta_menu()
        else:
            print("Opção inválida.")
            input("\nPressione Enter para continuar...")
            menu_cardapio()

# ====== ESTOQUE PRODUTO ======
def menu_estoque():
    while True:
        exibir_titulo('ESTOQUE DE PRODUTOS')
        print('1. Adicionar Item')
        print('2. Alterar Item')
        print('3. Remover Item')
        print('4. Visualizar Estoque')
        print('5. Voltar')
        opcao = input('Escolha uma opção: ')
        
        if opcao == '1':
            nome = input('Nome: ').strip()
            try:
                quantidade = int(input('Quantidade: '))
                valor = float(input('Valor: '))
                if quantidade < 0 or valor < 0:
                    print("Quantidade e valor devem ser positivos.")
                    continue
                if session.query(EstoqueItem).filter_by(nome=nome).first():
                    print("Já existe um item com esse nome.")
                    continue
                item = EstoqueItem(nome=nome, quantidade=quantidade, valor=valor)
                session.add(item)
                session.commit()
                print("Item adicionado com sucesso!")
            except ValueError:
                print("Erro: Digite valores válidos para quantidade e valor.")
            except IntegrityError:
                session.rollback()
                print("Erro: Não foi possível adicionar o item.")

        elif opcao == '2':
            nome = input('Nome do item a alterar: ').strip()
            item = session.query(EstoqueItem).filter_by(_nome=nome).first()
            if item:
                novo_nome = input(f'Novo nome ({item.nome}): ').strip()
                nova_quantidade = input(f'Nova quantidade ({item.quantidade}): ').strip()
                novo_valor = input(f'Novo valor (R${item.valor:.2f}): ').strip()
                
                if novo_nome:
                    item.nome = novo_nome
                if nova_quantidade:
                    try:
                        item.quantidade = int(nova_quantidade)
                    except ValueError:
                        print("Quantidade inválida. Alteração ignorada.")
                if novo_valor:
                    try:
                        item.valor = float(novo_valor)
                    except ValueError:
                        print("Valor inválido. Alteração ignorada.")

                session.commit()
                print("Item alterado com sucesso!")
            else:
                print("Item não encontrado.")

        elif opcao == '3':
            nome = input('Nome do item a remover: ').strip()
            item = session.query(EstoqueItem).filter_by(_nome=nome).first()
            if item:
                session.delete(item)
                session.commit()
                print("Item removido com sucesso!")
            else:
                print("Item não encontrado.")

        elif opcao == '4':
            limpar_tela()
            itens = session.query(EstoqueItem).all()
            if not itens:
                print("\nNenhum produto no estoque.\n")
            else:
                print("\n--- ESTOQUE ---\n")
                print(f"{'Nome do Produto':<20} {'Quantidade':<15} {'Valor':<15}")
                print("-" * 60)
                for item in itens:
                    print(f'{item.nome:<25} {item.quantidade:<10} R${item.valor:<9.2f}')
                print("-" * 60)
            input("\nPressione Enter para continuar...")
        elif opcao == '5':
            volta_menu()
        else:
            print('Opção inválida.')
            input("\nPressione Enter para continuar...")
            volta_menu()

# ====== PAGAMENTO ======
def visualizar_pagamentos():
    limpar_tela()
    exibir_titulo('PAGAMENTOS REGISTRADOS')

    pagamentos_encontrados = False
    clientes = session.query(Cliente).all()

    for cliente in clientes:
        if cliente.pagamentos:
            pagamentos_encontrados = True
            for pagamento in cliente.pagamentos:
                print(f'{cliente.nome} - {pagamento.tipo} - R${pagamento.valor:.2f}')

    if not pagamentos_encontrados:
        print("Nenhum pagamento registrado.")

    input("\nPressione Enter para continuar...")
    volta_menu()


def registrar_pagamento():
    limpar_tela()
    exibir_titulo('REGISTRAR PAGAMENTO')

    clientes = session.query(Cliente).all()

    if not clientes:
        print("Nenhum cliente cadastrado.")
        input("\nPressione Enter para voltar...")
        return volta_menu()

    print("Clientes disponíveis:")
    for cliente in clientes:
        print(f'{cliente.id} - {cliente.nome}')

    try:
        cliente_id = int(input("\nDigite o ID do cliente para o pagamento: "))
        cliente = session.query(Cliente).filter_by(id=cliente_id).first()

        if not cliente:
            print("Cliente não encontrado.")
            input("\nPressione Enter para voltar...")
            return volta_menu()

        tipo = input("Digite o tipo de pagamento (Dinheiro, Cartão, etc.): ")
        valor = float(input("Digite o valor do pagamento: R$ "))

        pagamento = Pagamento(tipo=tipo, valor=valor, cliente=cliente)
        session.add(pagamento)
        session.commit()

        print("\nPagamento registrado com sucesso!")

    except Exception as e:
        print(f"\n Erro ao registrar pagamento: {e}")
        session.rollback()

    input("\nPressione Enter para continuar...")
    volta_menu()

# ====== FUNÇÃO DE SAÍDA =====
def sair():
    limpar_tela()
    print('Saindo do sistema...')
    for i in range(3, 0, -1):
        print(f"Encerrando em {i} segundos...", end='\r')
        time.sleep(1)
    limpar_tela()
    exit(0)

# ====== CRIAÇÃO DAS TABELAS NO BANCO DE DADOS ======
Base.metadata.create_all(engine)

if __name__ == '__main__':
    sistema_login()
