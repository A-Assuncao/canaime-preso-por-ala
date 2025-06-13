def __init__(self):
    """Inicializa a view de login."""
    self.logger = LoggerAdapter().get_logger()
    self.root = None
    self.username_var = None
    self.password_var = None
    self.use_https_var = None  # Nova variável para controlar o uso de HTTPS
    self.credentials = None

def show_dialog(self):
    """
    Exibe o diálogo de login e retorna as credenciais inseridas.
    
    Returns:
        tuple: Uma tupla (username, password) ou None se cancelado.
    """
    try:
        self.logger.info("Exibindo diálogo de login")
        
        # Criar janela de diálogo
        self.root = tk.Toplevel()
        self.root.title("Login - Canaime")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.transient()  # Tornar modal
        self.root.grab_set()  # Bloquear outras janelas
        
        # Inicializar as variáveis de texto depois de criar a janela
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.use_https_var = tk.BooleanVar(value=True)  # Por padrão, usar HTTPS
        
        # Configurar o ícone (se disponível)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            self.logger.warning("Ícone não encontrado")
        
        # Centralizar na tela
        self.center_window()
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Login - Canaime", 
            font=("Helvetica", 12, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Campo de usuário
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=5)
        
        username_label = ttk.Label(username_frame, text="Usuário:")
        username_label.pack(side=tk.LEFT, padx=(0, 5))
        
        username_entry = ttk.Entry(username_frame, textvariable=self.username_var)
        username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Campo de senha
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=5)
        
        password_label = ttk.Label(password_frame, text="Senha:")
        password_label.pack(side=tk.LEFT, padx=(0, 5))
        
        password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="*")
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Caixa de seleção para HTTP/HTTPS
        https_frame = ttk.Frame(main_frame)
        https_frame.pack(fill=tk.X, pady=5)
        
        https_check = ttk.Checkbutton(
            https_frame, 
            text="Usar HTTPS (desmarque se o site estiver com certificado expirado)", 
            variable=self.use_https_var
        )
        https_check.pack(side=tk.LEFT)
        
        # Explicação sobre a opção HTTP/HTTPS
        explanation_label = ttk.Label(
            main_frame, 
            text="Às vezes o site pode estar com certificado SSL/TLS expirado.\nNesse caso, desmarque esta opção para usar HTTP.",
            font=("Helvetica", 8),
            foreground="gray"
        )
        explanation_label.pack(pady=(0, 10))
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        login_button = ttk.Button(
            button_frame, 
            text="Login", 
            command=self.fazer_login
        )
        login_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancelar", 
            command=self.root.destroy
        )
        cancel_button.pack(side=tk.RIGHT)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.pack(pady=(10, 0))
        
        # Configurar eventos
        self.root.bind("<Return>", lambda event: self.fazer_login())
        self.root.bind("<Escape>", lambda event: self.root.destroy())
        
        # Focar no campo de usuário
        username_entry.focus()
        
        # Iniciar o loop de eventos
        self.root.mainloop()
        
        # Retornar as credenciais após o fechamento da janela
        return self.credentials
        
    except Exception as e:
        self.logger.error(f"Erro ao exibir diálogo de login: {str(e)}")
        return None

def get_credentials(self):
    """
    Retorna as credenciais inseridas pelo usuário.
    
    Returns:
        tuple: Uma tupla (username, password, use_https) ou None se cancelado.
    """
    if self.credentials:
        username, password = self.credentials
        return (username, password, self.use_https_var.get())
    return None 