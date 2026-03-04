#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Senha Única - Alfatronic
Sistema de Licenciamento e Validação
"""

import tkinter as tk
from tkinter import messagebox
import platform
import subprocess
import re
import os
import json
import sys


def obter_serial_hd():
    """Obtém o número de série do HD do sistema"""
    sistema = platform.system()

    try:
        if sistema == "Windows":
            output = subprocess.check_output(
                "wmic diskdrive get serialnumber",
                shell=True,
                stderr=subprocess.DEVNULL
            ).decode('utf-8', errors='ignore')

            lines = output.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and line != "SerialNumber":
                    serial = re.sub(r'[^a-zA-Z0-9]', '', line)
                    if serial:
                        return serial

            output = subprocess.check_output(
                "vol C:",
                shell=True,
                stderr=subprocess.DEVNULL
            ).decode('utf-8', errors='ignore')

            match = re.search(r'([0-9A-F]{4}-[0-9A-F]{4})', output)
            if match:
                return match.group(1).replace('-', '')

        elif sistema == "Linux":
            try:
                output = subprocess.check_output(
                    "lsblk -o SERIAL | head -2 | tail -1",
                    shell=True
                ).decode().strip()
                if output:
                    return output
            except:
                pass

        elif sistema == "Darwin":
            output = subprocess.check_output(
                "system_profiler SPSerialATADataType | grep 'Serial Number'",
                shell=True
            ).decode().strip()
            if output:
                return output.split(':')[-1].strip()

    except Exception as e:
        pass

    return None


def gerar_senha_de_serial(serial_hd):
    """Gera senha de 6 dígitos a partir do serial do HD"""
    if not serial_hd:
        return None

    serial_bytes = serial_hd.encode('utf-8')

    cpu_id0 = 0
    cpu_id1 = 0
    cpu_id2 = 0

    for i, byte in enumerate(serial_bytes):
        if i % 3 == 0:
            cpu_id0 = (cpu_id0 << 8) | byte
            cpu_id0 = cpu_id0 & 0xFFFFFFFF
        elif i % 3 == 1:
            cpu_id1 = (cpu_id1 << 8) | byte
            cpu_id1 = cpu_id1 & 0xFFFFFFFF
        else:
            cpu_id2 = (cpu_id2 << 8) | byte
            cpu_id2 = cpu_id2 & 0xFFFFFFFF

    temp = cpu_id0
    temp ^= (cpu_id1 << 11) & 0xFFFFFFFFFFFFFFFF
    temp ^= (cpu_id2 << 22) & 0xFFFFFFFFFFFFFFFF
    temp = ((temp >> 32) ^ (temp & 0xFFFFFFFF)) & 0xFFFFFFFF
    temp = (temp * 2654435761) & 0xFFFFFFFF
    senha = temp % 1000000

    return senha


def gera_senha_4_digitos(senha_6_digitos):
    """Gera senha de 4 dígitos a partir de senha de 6 dígitos - Nível 2 (Técnico)"""
    parte1 = senha_6_digitos // 1000
    parte2 = senha_6_digitos % 1000
    temp = (parte1 * 17) ^ (parte2 * 23)
    temp = temp * 40503
    senha = temp % 10000
    return senha


def gera_senha_nivel_1(senha_6_digitos):
    """Gera senha de 4 dígitos - Nível 1 (Usuário básico)"""
    parte1 = senha_6_digitos // 1000
    parte2 = senha_6_digitos % 1000
    temp = (parte1 * 13) ^ (parte2 * 19)
    temp = temp * 31847
    senha = temp % 10000
    return senha


def gera_senha_nivel_2(senha_6_digitos):
    """Gera senha de 4 dígitos - Nível 2 (Técnico)"""
    return gera_senha_4_digitos(senha_6_digitos)


def gera_senha_nivel_3(senha_6_digitos):
    """Gera senha de 4 dígitos - Nível 3 (Administrador)"""
    parte1 = senha_6_digitos // 1000
    parte2 = senha_6_digitos % 1000
    temp = (parte1 * 29) ^ (parte2 * 37)
    temp = temp * 52711
    senha = temp % 10000
    return senha


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Licenciamento - Alfatronic")
        self.root.geometry("600x750")
        self.root.configure(bg="#2C3E50")

        self.arquivo_licenca = "alfatronic_license.json"
        self.serial_hd = None
        self.senha_6_dig = None
        self.licenciado = False

        # Verifica licença
        self.verificar_licenca()

    def verificar_licenca(self):
        """Verifica se já existe licença válida"""
        # Obtém serial do HD
        self.serial_hd = obter_serial_hd()

        if not self.serial_hd:
            messagebox.showerror(
                "Erro",
                "Não foi possível detectar o serial do HD.\n"
                "Execute como administrador se necessário."
            )
            self.root.destroy()
            return

        # Gera senha de 6 dígitos do HD
        self.senha_6_dig = gerar_senha_de_serial(self.serial_hd)

        # Verifica se existe arquivo de licença
        if os.path.exists(self.arquivo_licenca):
            try:
                with open(self.arquivo_licenca, 'r') as f:
                    dados = json.load(f)

                if dados.get('ativado'):
                    # Licença válida (não verifica mais o serial do HD)
                    self.licenciado = True
                    self.criar_interface_licenciado()
                    return
            except:
                pass

        # Não licenciado - mostra tela de ativação
        self.criar_interface_ativacao()

    def criar_interface_ativacao(self):
        """Cria interface para ativação do sistema"""
        # Limpa janela
        for widget in self.root.winfo_children():
            widget.destroy()

        # Título
        tk.Label(
            self.root,
            text="🔒 Sistema Não Licenciado",
            font=("Arial", 18, "bold"),
            bg="#2C3E50",
            fg="#E74C3C"
        ).pack(pady=20)

        tk.Label(
            self.root,
            text="Alfatronic - Controle Remoto",
            font=("Arial", 10),
            bg="#2C3E50",
            fg="#3498DB"
        ).pack(pady=(0, 20))

        # Frame informações
        frame_info = tk.Frame(self.root, bg="#34495E", relief=tk.RAISED, bd=2)
        frame_info.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            frame_info,
            text="⚠️ Ativação Necessária",
            font=("Arial", 12, "bold"),
            bg="#34495E",
            fg="white"
        ).pack(pady=(15, 10))

        tk.Label(
            frame_info,
            text="Código de Ativação:",
            font=("Arial", 10, "bold"),
            bg="#34495E",
            fg="white"
        ).pack(pady=(15, 5))

        senha_display = tk.Entry(
            frame_info,
            font=("Arial", 28, "bold"),
            width=10,
            justify="center",
            bg="white",
            fg="#E74C3C",
            state="normal"
        )
        senha_display.pack(pady=(0, 10), ipady=8)
        senha_display.insert(0, f"{self.senha_6_dig:06d}")
        senha_display.config(state="readonly")

        tk.Button(
            frame_info,
            text="COPIAR CÓDIGO",
            font=("Arial", 9, "bold"),
            bg="#F39C12",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.copiar_codigo(f"{self.senha_6_dig:06d}")
        ).pack(pady=(0, 15), padx=20, fill=tk.X)

        # Frame validação
        frame_val = tk.Frame(self.root, bg="#34495E", relief=tk.RAISED, bd=2)
        frame_val.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(
            frame_val,
            text="Digite a Contra-Senha (6 dígitos):",
            font=("Arial", 11, "bold"),
            bg="#34495E",
            fg="white"
        ).pack(pady=(15, 5))

        self.entry_contra = tk.Entry(
            frame_val,
            font=("Arial", 24, "bold"),
            width=10,
            justify="center",
            bg="white",
            fg="#2C3E50"
        )
        self.entry_contra.pack(pady=(0, 15), ipady=8)
        self.entry_contra.bind('<KeyRelease>', self.validar_entrada_contra)
        self.entry_contra.bind('<Return>', lambda e: self.ativar_licenca())

        tk.Button(
            self.root,
            text="ATIVAR LICENÇA",
            font=("Arial", 12, "bold"),
            bg="#27AE60",
            fg="white",
            activebackground="#229954",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.ativar_licenca,
            height=2
        ).pack(fill=tk.X, padx=20, pady=15)

        # Status
        self.status = tk.Label(
            self.root,
            text="Envie o Código de Ativação para o suporte\ne digite a mesma senha como Contra-Senha",
            font=("Arial", 9),
            bg="#2C3E50",
            fg="white",
            justify="center"
        )
        self.status.pack(pady=10)

        self.centralizar()
        self.entry_contra.focus()

    def validar_entrada_contra(self, event=None):
        """Valida entrada da contra-senha"""
        texto = self.entry_contra.get()
        limpo = ''.join(c for c in texto if c.isdigit())
        if len(limpo) > 6:
            limpo = limpo[:6]
        if texto != limpo:
            self.entry_contra.delete(0, tk.END)
            self.entry_contra.insert(0, limpo)

    def ativar_licenca(self):
        """Ativa a licença verificando a contra-senha"""
        contra_senha = self.entry_contra.get()

        if len(contra_senha) != 6 or not contra_senha.isdigit():
            messagebox.showerror("Erro", "Digite uma contra-senha de 6 dígitos!")
            return

        # Gera a senha de 4 dígitos a partir do código de ativação
        senha_4_dig = gera_senha_4_digitos(self.senha_6_dig)
        # Formata como 6 dígitos (com zeros à esquerda)
        senha_correta = f"{senha_4_dig:06d}"

        if contra_senha == senha_correta:
            # Salva licença (sem incluir o serial do HD)
            dados = {
                'ativado': True,
                'senha_validacao': contra_senha
            }

            try:
                with open(self.arquivo_licenca, 'w') as f:
                    json.dump(dados, f)

                messagebox.showinfo(
                    "Sucesso",
                    "✓ Licença ativada com sucesso!\n\nO sistema agora está liberado."
                )

                self.licenciado = True
                self.criar_interface_licenciado()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar licença: {e}")
        else:
            messagebox.showerror(
                "Erro",
                "✗ Contra-senha incorreta!\n\nVerifique com o suporte."
            )

    def criar_interface_licenciado(self):
        """Cria interface para sistema licenciado"""
        # Limpa janela
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("600x650")

        # Título
        tk.Label(
            self.root,
            text="🔓 Sistema Licenciado",
            font=("Arial", 16, "bold"),
            bg="#2C3E50",
            fg="#27AE60"
        ).pack(pady=10)

        tk.Label(
            self.root,
            text="Alfatronic - Gerador de Senhas",
            font=("Arial", 9),
            bg="#2C3E50",
            fg="#3498DB"
        ).pack(pady=(0, 10))

        # Frame entrada
        frame1 = tk.Frame(self.root, bg="#34495E", relief=tk.RAISED, bd=2)
        frame1.pack(fill=tk.X, padx=20, pady=6)

        tk.Label(
            frame1,
            text="Senha de 6 Dígitos:",
            font=("Arial", 11, "bold"),
            bg="#34495E",
            fg="white"
        ).pack(pady=(10, 5))

        self.entrada6 = tk.Entry(
            frame1,
            font=("Arial", 20, "bold"),
            width=12,
            justify="center",
            bg="white",
            fg="#2C3E50"
        )
        self.entrada6.pack(pady=(0, 10), ipady=6)
        self.entrada6.bind('<KeyRelease>', self.validar)
        self.entrada6.bind('<Return>', lambda e: self.gerar())

        # Botão
        tk.Button(
            self.root,
            text="GERAR SENHA",
            font=("Arial", 11, "bold"),
            bg="#3498DB",
            fg="white",
            activebackground="#2980B9",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.gerar,
            height=2
        ).pack(fill=tk.X, padx=20, pady=8)

        # Frame resultado
        frame2 = tk.Frame(self.root, bg="#34495E", relief=tk.RAISED, bd=2)
        frame2.pack(fill=tk.X, padx=20, pady=6)

        tk.Label(
            frame2,
            text="Senha de 4 Dígitos:",
            font=("Arial", 11, "bold"),
            bg="#34495E",
            fg="white"
        ).pack(pady=(10, 5))

        self.saida4 = tk.Entry(
            frame2,
            font=("Arial", 20, "bold"),
            width=12,
            justify="center",
            bg="white",
            fg="#27AE60",
            state="normal"
        )
        self.saida4.pack(pady=(0, 10), ipady=6)
        self.saida4.insert(0, "----")
        self.saida4.config(state="readonly")

        # Frame Nível Senha
        frame3 = tk.Frame(self.root, bg="#34495E", relief=tk.RAISED, bd=2)
        frame3.pack(fill=tk.X, padx=20, pady=6)

        tk.Label(
            frame3,
            text="Nível Senha (1, 2 ou 3):",
            font=("Arial", 11, "bold"),
            bg="#34495E",
            fg="white"
        ).pack(pady=(10, 3))

        tk.Label(
            frame3,
            text="1=Usuário | 2=Técnico | 3=Admin",
            font=("Arial", 8),
            bg="#34495E",
            fg="#ECF0F1"
        ).pack(pady=(0, 3))

        self.entrada_nivel = tk.Entry(
            frame3,
            font=("Arial", 20, "bold"),
            width=12,
            justify="center",
            bg="white",
            fg="#2C3E50"
        )
        self.entrada_nivel.pack(pady=(0, 10), ipady=6)
        self.entrada_nivel.insert(0, "1")  # Valor padrão: Nível 1
        self.entrada_nivel.bind('<KeyRelease>', self.validar_nivel)

        # Status
        self.status_lic = tk.Label(
            self.root,
            text="✓ Sistema Licenciado",
            font=("Arial", 8),
            bg="#2C3E50",
            fg="#27AE60"
        )
        self.status_lic.pack(pady=5)

        self.status = tk.Label(
            self.root,
            text="Digite uma senha de 6 dígitos",
            font=("Arial", 9),
            bg="#2C3E50",
            fg="white"
        )
        self.status.pack(pady=2)

        self.centralizar()
        self.entrada6.focus()

    def validar(self, event=None):
        texto = self.entrada6.get()
        limpo = ''.join(c for c in texto if c.isdigit())
        if len(limpo) > 6:
            limpo = limpo[:6]
        if texto != limpo:
            self.entrada6.delete(0, tk.END)
            self.entrada6.insert(0, limpo)

        if len(limpo) == 6:
            self.status.config(text="✓ Pronto para gerar", fg="#27AE60")
        else:
            self.status.config(text=f"Digite {6-len(limpo)} dígito(s)", fg="white")

    def validar_nivel(self, event=None):
        """Valida entrada do campo Nível Senha (aceita apenas 1, 2 ou 3)"""
        texto = self.entrada_nivel.get()
        limpo = ''.join(c for c in texto if c.isdigit())

        # Limita a 1 dígito
        if len(limpo) > 1:
            limpo = limpo[:1]

        # Se valor maior que 3, fica 3; se for 0, fica vazio
        if limpo:
            valor = int(limpo)
            if valor > 3:
                limpo = '3'
            elif valor == 0:
                limpo = ''

        if texto != limpo:
            self.entrada_nivel.delete(0, tk.END)
            self.entrada_nivel.insert(0, limpo)

    def gerar(self):
        senha6 = self.entrada6.get()

        if len(senha6) != 6 or not senha6.isdigit():
            messagebox.showerror("Erro", "Digite 6 dígitos!")
            return

        # Verifica o nível da senha (1, 2 ou 3)
        nivel_str = self.entrada_nivel.get()
        if nivel_str == "":
            nivel = 1  # Padrão: Nível 1 (Usuário)
        else:
            nivel = int(nivel_str) if nivel_str.isdigit() and int(nivel_str) in [1, 2, 3] else 1

        # Gera a senha de acordo com o nível
        senha6_int = int(senha6)
        if nivel == 1:
            senha4 = gera_senha_nivel_1(senha6_int)
        elif nivel == 3:
            senha4 = gera_senha_nivel_3(senha6_int)
        else:  # nivel == 2 ou padrão
            senha4 = gera_senha_nivel_2(senha6_int)

        self.saida4.config(state="normal")
        self.saida4.delete(0, tk.END)
        self.saida4.insert(0, f"{senha4:04d}")
        self.saida4.config(state="readonly")

        # Atualiza status com informação do nível
        nivel_texto = {1: "Nível 1 (Usuário)", 2: "Nível 2 (Técnico)", 3: "Nível 3 (Admin)"}
        self.status.config(
            text=f"✓ Senha gerada - {nivel_texto.get(nivel, 'Nível 2 (Técnico)')}",
            fg="#27AE60"
        )

    def copiar_codigo(self, codigo):
        """Copia código para área de transferência"""
        self.root.clipboard_clear()
        self.root.clipboard_append(codigo)
        self.status.config(
            text="✓ Código copiado! Cole no gerador de contra-senha.",
            fg="#27AE60"
        )

    def centralizar(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')


if __name__ == "__main__":
    # Configuração do ícone para Windows (barra de tarefas) - ANTES de criar Tk
    try:
        import ctypes
        myappid = 'Alfatronic.GeradorSenha.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass

    root = tk.Tk()
    root.withdraw()  # Esconde a janela durante o carregamento

    # Define tamanho inicial fixo
    root.geometry("600x650")
    root.minsize(600, 650)

    # Configura ícone da janela
    try:
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(base_path, 'senha.ico')
        if os.path.exists(icon_path):
            root.iconbitmap(default=icon_path)

            # Também define via Windows API para barra de tarefas
            try:
                import ctypes

                GWL_EXSTYLE = -20
                WS_EX_APPWINDOW = 0x00040000

                hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                style = style | WS_EX_APPWINDOW
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

                # Carrega e define o ícone
                IMAGE_ICON = 1
                LR_LOADFROMFILE = 0x00000010
                hicon = ctypes.windll.user32.LoadImageW(None, icon_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE)
                if hicon:
                    ICON_SMALL = 0
                    ICON_BIG = 1
                    ctypes.windll.user32.SendMessageW(hwnd, 0x0080, ICON_SMALL, hicon)  # WM_SETICON
                    ctypes.windll.user32.SendMessageW(hwnd, 0x0080, ICON_BIG, hicon)
            except:
                pass
    except:
        pass

    app = App(root)

    # Aguarda todos os elementos serem processados e centraliza
    root.update_idletasks()
    root.deiconify()  # Mostra a janela já pronta

    root.mainloop()
