import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import functions
import Functions_Interface


def janela_principal(conexao):
    root = tk.Tk()
    root.title("Sistema de Gerenciamento de Produtos")
    root.geometry("500x400")

    label_titulo = tk.Label(root, text="Bem-vindo ao Sistema de Gerenciamento", font=("Arial", 16))
    label_titulo.pack(pady=20)
    
    botao_listar = tk.Button(root, text="Listar Produtos", font=("Arial", 12), width=20, command=lambda: Functions_Interface.listar_produtos_interface(conexao))
    botao_listar.pack(pady=10)
    
    botao_listar = tk.Button(root, text="Cadastrar Produto", font=("Arial", 12), width=20, command=lambda: Functions_Interface.cadastro_produto_interface(conexao))
    botao_listar.pack(pady=10)
    
    '''
    Fazer depois, com dificuldade
    botao_listar = tk.Button(root, text="Atualizar Produto", font=("Arial", 12), width=20, command=lambda: Functions_Interface.atualizar_produto_interface(conexao))
    botao_listar.pack(pady=10)
    '''
    
    botao_deletar = tk.Button(root, text="Deletar Produto", font=("Arial", 12), width=20, command=lambda: Functions_Interface.deletar_produto_interface(conexao))
    botao_deletar.pack(pady=10)
    
    '''
    Fazer depois, com dificuldade
    botao_deletar = tk.Button(root, text="Registrar Venda", font=("Arial", 12), width=20, command=lambda: Functions_Interface.registrar_venda_interface(conexao))
    botao_deletar.pack(pady=10)
    '''
    
    botao_sair = tk.Button(root, text="Sair", font=("Arial", 12), width=20, command=root.destroy)
    botao_sair.pack(pady=10)

    root.mainloop()

abrir_conexao = functions.abrir_conexao()
janela_principal(abrir_conexao)
functions.encerrar_conexao(abrir_conexao)