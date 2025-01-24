import oracledb
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
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

def listar_produtos_interface(conexao):
    
    janela_listar = tk.Toplevel()
    janela_listar.title("Lista de Produtos")
    janela_listar.geometry("500x400")

    label_titulo = tk.Label(janela_listar, text="Produtos Cadastrados", font=("Arial", 14))
    label_titulo.pack(pady=10)

    frame_treeview = tk.Frame(janela_listar)
    frame_treeview.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(frame_treeview, columns=("ID", "Nome", "Preço", "Quantidade"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Nome", text="Nome")
    tree.heading("Preço", text="Preço")
    tree.heading("Quantidade", text="Quantidade")
    tree.column("ID", width=50, anchor="center")
    tree.column("Nome", width=200, anchor="w")
    tree.column("Preço", width=100, anchor="center")
    tree.column("Quantidade", width=100, anchor="center")
    tree.pack(fill="both", expand=True)

    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, preco, quantidade FROM PRODUTOS ORDER BY id")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
    finally:
        cursor.close()

    botao_fechar = tk.Button(janela_listar, text="Fechar", font=("Arial", 12), command=janela_listar.destroy)
    botao_fechar.pack(pady=10)

def cadastro_produto_interface(conexao):
    
    janela_cadastro = tk.Toplevel()
    janela_cadastro.title("Cadastro de Produto")
    janela_cadastro.geometry("500x400")

    label_titulo = tk.Label(janela_cadastro, text="Cadastrar Novo Produto", font=("Arial", 14))
    label_titulo.pack(pady=10)

    frame_campos = tk.Frame(janela_cadastro)
    frame_campos.pack(pady=10, padx=10, fill="x")

    tk.Label(frame_campos, text="Nome do Produto:", anchor="w").pack(fill="x")
    entry_nome = tk.Entry(frame_campos)
    entry_nome.pack(fill="x", pady=5)

    tk.Label(frame_campos, text="Categoria do Produto:", anchor="w").pack(fill="x")
    entry_categoria = tk.Entry(frame_campos)
    entry_categoria.pack(fill="x", pady=5)

    tk.Label(frame_campos, text="Preço do Produto:", anchor="w").pack(fill="x")
    entry_preco = tk.Entry(frame_campos)
    entry_preco.pack(fill="x", pady=5)

    tk.Label(frame_campos, text="Quantidade em Estoque:", anchor="w").pack(fill="x")
    entry_quantidade = tk.Entry(frame_campos)
    entry_quantidade.pack(fill="x", pady=5)

    def salvar_produto():
        try:
            cursor = conexao.cursor()

            cursor.execute("SELECT MAX(id) FROM produtos")
            max_id = cursor.fetchone()[0]
            id_final = (max_id + 1) if max_id else 1

            nome = entry_nome.get().strip()
            categoria = entry_categoria.get().strip()
            try:
                preco = round(float(entry_preco.get()), 2)
                quantidade = int(entry_quantidade.get())
            except ValueError:
                messagebox.showerror("Erro", "Preço e quantidade devem ser numéricos.")
                return

            if not nome or not categoria:
                messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
                return

            cursor.execute(
                "INSERT INTO produtos (id, nome, categoria, preco, quantidade) VALUES (:1, :2, :3, :4, :5)",
                (id_final, nome, categoria, preco, quantidade),
            )
            conexao.commit()
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso.")
            janela_cadastro.destroy()
        finally:
            cursor.close()

    botao_salvar = tk.Button(janela_cadastro, text="Salvar", font=("Arial", 12), width=15, command=salvar_produto)
    botao_salvar.pack(pady=(10, 5), padx=20)

    botao_fechar = tk.Button(janela_cadastro, text="Fechar", font=("Arial", 12), width=15, command=janela_cadastro.destroy)
    botao_fechar.pack(pady=(5, 10), padx=20)



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


def deletar_produto_interface(conexao):
    janela_deletar = tk.Toplevel()
    janela_deletar.title("Deletar Produtos")
    janela_deletar.geometry("400x500")

    label_titulo = tk.Label(janela_deletar, text="Selecione os Produtos para Deletar", font=("Arial", 14))
    label_titulo.pack(pady=10)

    frame_produtos = tk.Frame(janela_deletar)
    frame_produtos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    canvas = tk.Canvas(frame_produtos)
    scrollbar = tk.Scrollbar(frame_produtos, orient="vertical", command=canvas.yview)
    produtos_frame = tk.Frame(canvas)

    produtos_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=produtos_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    checkboxes = {}

    def carregar_produtos():
        for widget in produtos_frame.winfo_children():
            widget.destroy()

        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome FROM PRODUTOS ORDER BY id")
        produtos = cursor.fetchall()
        cursor.close()

        for produto in produtos:
            id_produto = produto[0]
            nome_produto = produto[1]
            var = tk.BooleanVar()
            check = tk.Checkbutton(produtos_frame, text=f"{id_produto} - {nome_produto}", variable=var, anchor="w", padx=10)
            check.pack(fill="x", pady=2, anchor="w")
            checkboxes[id_produto] = var

    carregar_produtos()

    def deletar_selecionados():
        ids_para_deletar = [id_produto for id_produto, var in checkboxes.items() if var.get()]

        if not ids_para_deletar:
            messagebox.showwarning("Aviso", "Nenhum produto foi selecionado para deletar.")
            return

        cursor = conexao.cursor()
        for id_produto in ids_para_deletar:
            cursor.execute("DELETE FROM PRODUTOS WHERE id = :1", (id_produto,))
        conexao.commit()
        cursor.close()

        reordenar_ids(conexao)

        messagebox.showinfo("Sucesso", "Produtos deletados com sucesso.")
        janela_deletar.destroy()

    botao_deletar = tk.Button(janela_deletar, text="Deletar Selecionados", font=("Arial", 12), command=deletar_selecionados)
    botao_deletar.pack(pady=10)


def atualizar_produto_interface(conexao):
    def listar_produtos():
        """Popula a Treeview com os produtos cadastrados no banco."""
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM produtos ORDER BY id")
        produtos = cursor.fetchall()
        cursor.close()

        for row in tree.get_children():
            tree.delete(row)

        for produto in produtos:
            tree.insert("", "end", values=produto)

    def selecionar_produto(event):
        """Carrega os dados do produto selecionado nos campos."""
        selected_item = tree.focus()
        if not selected_item:
            return

        valores = tree.item(selected_item, "values")
        id_produto.set(valores[0])
        nome_var.set(valores[1])
        categoria_var.set(valores[2])
        preco_var.set(valores[3])
        quantidade_var.set(valores[4])

    def atualizar_dados():
        """Atualiza o produto no banco com os dados informados."""
        try:
            cursor = conexao.cursor()
            id_atualizar = id_produto.get()

            if not id_atualizar:
                messagebox.showwarning("Aviso", "Selecione um produto para atualizar.")
                return

            novo_nome = nome_var.get()
            nova_categoria = categoria_var.get()
            novo_preco = float(preco_var.get())
            nova_quantidade = int(quantidade_var.get())

            cursor.execute(
                "UPDATE produtos SET nome = :1, categoria = :2, preco = :3, quantidade = :4 WHERE id = :5",
                (novo_nome, nova_categoria, novo_preco, nova_quantidade, id_atualizar),
            )
            conexao.commit()

            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            listar_produtos()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao atualizar o produto: {e}")
            conexao.rollback()
        finally:
            cursor.close()

    # Janela principal
    janela = tk.Toplevel()
    janela.title("Atualizar Produto")
    janela.geometry("800x600")

    # Widgets para listar produtos
    frame_lista = tk.Frame(janela)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("ID", "Nome", "Categoria", "Preço", "Quantidade")
    tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=10)

    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    tree.bind("<ButtonRelease-1>", selecionar_produto)

    # Frame para atualizar dados
    frame_dados = tk.Frame(janela)
    frame_dados.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_dados, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    id_produto = tk.StringVar()
    id_entry = tk.Entry(frame_dados, textvariable=id_produto, state="readonly")
    id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame_dados, text="Nome:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    nome_var = tk.StringVar()
    nome_entry = tk.Entry(frame_dados, textvariable=nome_var)
    nome_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame_dados, text="Categoria:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    categoria_var = tk.StringVar()
    categoria_entry = tk.Entry(frame_dados, textvariable=categoria_var)
    categoria_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame_dados, text="Preço:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    preco_var = tk.StringVar()
    preco_entry = tk.Entry(frame_dados, textvariable=preco_var)
    preco_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame_dados, text="Quantidade:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
    quantidade_var = tk.StringVar()
    quantidade_entry = tk.Entry(frame_dados, textvariable=quantidade_var)
    quantidade_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

    # Botões
    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(fill="x", padx=10, pady=10)

    atualizar_btn = tk.Button(frame_botoes, text="Atualizar Produto", command=atualizar_dados)
    atualizar_btn.pack(side="left", padx=5)

    fechar_btn = tk.Button(frame_botoes, text="Fechar", command=janela.destroy)
    fechar_btn.pack(side="right", padx=5)

    listar_produtos()

    janela.mainloop()

def registrar_venda_interface(conexao):
    def listar_produtos():
        """Popula a Treeview com os produtos cadastrados no banco."""
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, preco, quantidade FROM produtos ORDER BY id")
        produtos = cursor.fetchall()
        cursor.close()

        for row in tree.get_children():
            tree.delete(row)

        for produto in produtos:
            tree.insert("", "end", values=produto)

    def adicionar_produto():
        """Adiciona um produto à lista de vendas com a quantidade desejada."""
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um produto para adicionar.")
            return

        valores = tree.item(selected_item, "values")
        id_produto, nome, preco, estoque = valores

        try:
            quantidade = int(quantidade_var.get())
            if quantidade <= 0 or quantidade > int(estoque):
                raise ValueError("Quantidade inválida ou maior que o estoque disponível.")

            if id_produto in produtos_vendas:
                messagebox.showwarning("Aviso", "Este produto já foi adicionado.")
                return

            subtotal = quantidade * float(preco)
            produtos_vendas[id_produto] = {
                "Nome": nome,
                "Preco": float(preco),
                "Quantidade": quantidade,
                "Subtotal": subtotal,
            }

            atualizar_lista_vendas()
            atualizar_total()

        except ValueError:
            messagebox.showerror("Erro", "Insira uma quantidade válida.")

    def atualizar_lista_vendas():
        """Atualiza a Treeview de produtos na venda."""
        for row in tree_vendas.get_children():
            tree_vendas.delete(row)

        for id_produto, detalhes in produtos_vendas.items():
            tree_vendas.insert(
                "", "end", values=(id_produto, detalhes["Nome"], detalhes["Quantidade"], detalhes["Preco"], detalhes["Subtotal"])
            )

    def atualizar_total():
        """Atualiza o valor total da venda."""
        total = sum(detalhes["Subtotal"] for detalhes in produtos_vendas.values())
        total_var.set(f"Total: R${total:.2f}")

    def registrar_venda():
        """Registra a venda no banco de dados."""
        if not produtos_vendas:
            messagebox.showwarning("Aviso", "Nenhum produto foi adicionado à venda.")
            return

        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT NVL(MAX(id_venda), 0) + 1 FROM tabela_vendas")
            id_final_venda = cursor.fetchone()[0]

            produtos_vendas_json = json.dumps(produtos_vendas)
            total_venda = sum(detalhes["Subtotal"] for detalhes in produtos_vendas.values())

            cursor.execute(
                "INSERT INTO tabela_vendas (id_venda, itens_venda, data_venda, total_venda) VALUES (:1, :2, SYSTIMESTAMP, :3)",
                (id_final_venda, produtos_vendas_json, total_venda),
            )

            for id_produto, detalhes in produtos_vendas.items():
                cursor.execute(
                    "UPDATE produtos SET quantidade = quantidade - :quantidade WHERE id = :id_produto",
                    {"quantidade": detalhes["Quantidade"], "id_produto": id_produto},
                )

            conexao.commit()
            messagebox.showinfo("Sucesso", f"Venda registrada com sucesso! Total: R${total_venda:.2f}")
            produtos_vendas.clear()
            atualizar_lista_vendas()
            atualizar_total()
            listar_produtos()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar a venda: {e}")
            conexao.rollback()
        finally:
            cursor.close()

    # Janela principal
    janela = tk.Toplevel()
    janela.title("Registrar Venda")
    janela.geometry("1000x700")

    # Produtos disponíveis
    frame_lista = tk.Frame(janela)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

    tk.Label(frame_lista, text="Produtos Disponíveis").pack(anchor="w")

    colunas = ("ID", "Nome", "Preço", "Estoque")
    tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=10)

    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Frame para adicionar produtos
    frame_adicionar = tk.Frame(janela)
    frame_adicionar.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_adicionar, text="Quantidade:").pack(side="left", padx=5)
    quantidade_var = tk.StringVar()
    quantidade_entry = tk.Entry(frame_adicionar, textvariable=quantidade_var, width=10)
    quantidade_entry.pack(side="left", padx=5)

    adicionar_btn = tk.Button(frame_adicionar, text="Adicionar Produto", command=adicionar_produto)
    adicionar_btn.pack(side="left", padx=5)

    # Produtos na venda
    frame_venda = tk.Frame(janela)
    frame_venda.pack(fill="both", expand=True, padx=10, pady=10)

    tk.Label(frame_venda, text="Produtos na Venda").pack(anchor="w")

    colunas_venda = ("ID", "Nome", "Quantidade", "Preço Unitário", "Subtotal")
    tree_vendas = ttk.Treeview(frame_venda, columns=colunas_venda, show="headings", height=10)

    for col in colunas_venda:
        tree_vendas.heading(col, text=col)
        tree_vendas.column(col, width=150)

    tree_vendas.pack(side="left", fill="both", expand=True)
    scrollbar_venda = ttk.Scrollbar(frame_venda, orient="vertical", command=tree_vendas.yview)
    tree_vendas.configure(yscroll=scrollbar_venda.set)
    scrollbar_venda.pack(side="right", fill="y")

    # Total e botão registrar
    frame_total = tk.Frame(janela)
    frame_total.pack(fill="x", padx=10, pady=10)

    total_var = tk.StringVar(value="Total: R$0.00")
    tk.Label(frame_total, textvariable=total_var, font=("Arial", 14)).pack(side="left")

    registrar_btn = tk.Button(frame_total, text="Registrar Venda", command=registrar_venda)
    registrar_btn.pack(side="right", padx=5)

    fechar_btn = tk.Button(frame_total, text="Fechar", command=janela.destroy)
    fechar_btn.pack(side="right", padx=5)

    # Carregar produtos na Treeview
    produtos_vendas = {}
    listar_produtos()

    janela.mainloop()
