import oracledb
import json

def abrir_conexao():
    try:
        conexao = oracledb.connect(
            user="rm97758",
            password="080305",
            dsn="oracle.fiap.com.br:1521/ORCL"          
        )
        print("Conexão aberta com sucesso!")
        return conexao
    except oracledb.Error as e:
        print("Erro ao conectar ao banco de dados:", e)
        return None

def encerrar_conexao(conexao, cursor=None):
    if cursor:
        cursor.close()
        print("Cursor fechado.")
    if conexao:
        conexao.close()
        print("Conexão encerrada.")
        

def listar_produtos(conexao):
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM PRODUTOS ORDER BY id")
        for row in cursor:
            print(row)
    
    finally:
        cursor.close()

def reordenar_ids(conexao):
    try:
        cursor = conexao.cursor()

        cursor.execute("SELECT id FROM PRODUTOS ORDER BY id")
        produtos = cursor.fetchall()

        novo_id = 1 
        for produto in produtos:
            id_atual = produto[0]
            cursor.execute("UPDATE PRODUTOS SET id = :1 WHERE id = :2", (novo_id, id_atual))
            novo_id += 1

        conexao.commit()
        print("IDs reordenados com sucesso.")
    finally:
        cursor.close()

def cadastro_produto(conexao):
    try:
        cursor = conexao.cursor()
        
        cursor.execute("SELECT MAX(id) FROM produtos")
        id_final = cursor.fetchone()[0] + 1
        nome = input("Digite o nome do produto: ")
        categoria = input("Digite a categoria do produto: ")
        preco = round(float(input("Digite o valor do produto: ")), 2)
        quantidade = int(input("Digite a quantidade de produtos em estoque: "))
        cursor.execute("INSERT INTO produtos (id, nome, categoria, preco, quantidade) VALUES (:1, :2, :3, :4, :5)", (id_final, nome, categoria, preco, quantidade))
        
        conexao.commit()
        print("Produto inserido com sucesso")
    finally:
        cursor.close()

def atualizar_produto(conexao):
    try:
        cursor = conexao.cursor()
        listar_produtos(conexao)
        id_produto = int(input("\nDigite o ID do produto que deseja atualizar (Ou 0 para cancelar a operação): "))
        
        while True:
            if id_produto == 0:
                break
            
            cursor.execute("SELECT * FROM PRODUTOS WHERE ID = :1", (id_produto,))
            produto = cursor.fetchone()
            
            print(f"Produto selecionado: {produto[1]} ({produto[2]}) - {produto[3]}. Quantidade: {produto[4]}\n")
            print(f"O que deseja alterar do produto de id: {produto[0]} \n1 - Nome \n2 - Categoria \n3 - Preço \n4 - Quantidade\n")
            opcao = int(input("Opção desejada: "))
            
            match opcao:
                case 1:
                    print("Atualização do nome\n")
                    nome_atual = produto[1]
                    novo_nome = input(f"Qual o novo nome para o produto {nome_atual}: ")
                    print("\n")
                    cursor.execute("UPDATE PRODUTOS SET nome = :1 WHERE id = :2", (novo_nome, produto[0]))
                    conexao.commit()
                case 2:
                    print("Atualização da categoria\n")
                    categoria_atual = produto[2]
                    nova_categoria = input(f"Qual a nova categoria para o produto {produto[1]} ({categoria_atual}): ")
                    print("\n")
                    cursor.execute("UPDATE PRODUTOS SET categoria = :1 WHERE id = :2", (nova_categoria, produto[0]))
                    conexao.commit()
                case 3:
                    print("Atualização do preço\n")
                    preco_atual = produto[3]
                    novo_preco = round(float(input(f"Digite o novo valor do produto {produto[1]} - Preço atual {preco_atual}: ")), 2)
                    print("/n")
                    cursor.execute("UPDATE PRODUTOS SET preco = :1 WHERE id = :2", (novo_preco, produto[0]))
                    conexao.commit()
                case 4:
                    print("Atualização da quantidade\n")
                    quantidade_atual = produto[4]
                    nova_quantidade = int(input(f"Digite a nova quantidade do produto: {produto[1]} - Quantidade atual: {quantidade_atual}:  "))
                    print("/n")
                    cursor.execute("UPDATE PRODUTOS SET quantidade = :1 WHERE id = :2", (nova_quantidade, produto[0]))
                    conexao.commit()
                case _:
                    print("Opção inválida")
    finally:
        cursor.close()
    

def deletar_produto(conexao):
    try:
        cursor = conexao.cursor()
        
        listar_produtos(conexao)
        
        id_desejado = int(input("Digite o ID do produto que deseja eliminar: "))
        cursor.execute("SELECT COUNT(*) FROM PRODUTOS WHERE id = :1", (id_desejado))
        existe = cursor.fetchone()[0]
        
        if existe:
            cursor.execute("DELETE FROM PRODUTOS WHERE id = :1", (id_desejado))
            conexao.commit()
            print("Produto excluído com sucesso.")
            reordenar_ids(conexao)
        else:
            print("Produto com o ID informado não encontrado.")
    finally:
        cursor.close()


def registrar_venda(conexao):
    try:
        cursor = conexao.cursor()
        produtos_vendas = {}
        total = 0

        while True:
            listar_produtos(conexao)
            id_produto = int(input("Digite o ID do produto (ou 0 para finalizar): "))

            if id_produto == 0:
                break
            
            quantidade = int(input("Digite a quantidade: "))
            cursor.execute("SELECT nome, preco, quantidade FROM produtos WHERE id = :1", (id_produto,))
            produto = cursor.fetchone()

            if produto and produto[2] >= quantidade:
                subtotal = quantidade * produto[1]
                produtos_vendas[id_produto] = {"Nome": produto[0], "Preco": produto[1], "Quantidade": quantidade} # Verificar para adicionar o total da venda
                total += subtotal
            else:
                print("Quantidade insuficiente ou produto inexistente.")

        if not produtos_vendas:
            print("Nenhum item foi adicionado à venda.")
            return

        cursor.execute("SELECT NVL(MAX(id_venda), 0) + 1 FROM tabela_vendas")
        id_final_venda = cursor.fetchone()[0]
        
        produtos_vendas_json = json.dumps(produtos_vendas)

        
        cursor.execute(
            "INSERT INTO tabela_vendas (id_venda, itens_venda, data_venda, total_venda) VALUES (:1, :2, SYSTIMESTAMP, :3)",
            (id_final_venda, produtos_vendas_json, total)
        )

        for id_produto, detalhes in produtos_vendas.items():
            cursor.execute( "UPDATE produtos SET quantidade = quantidade - :quantidade WHERE id = :id_produto", {"quantidade": detalhes["Quantidade"], "id_produto": id_produto})


        conexao.commit()
        print(f"Venda registrada com sucesso! Total: R${total:.2f}")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        conexao.rollback()
    finally:
        cursor.close()