import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json

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
    janela_cadastro.geometry("400x300")

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