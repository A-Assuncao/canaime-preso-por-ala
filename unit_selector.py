import tkinter as tk
from tkinter import messagebox

units = ('PAMC', 'CPBV', 'CPFBV', 'CPP', 'UPRRO')


def center_window(window, width, height):
    """
    Centers the window on the screen.

    Parameters
    ----------
    window : tk.Tk or tk.Toplevel
        The window to center.
    width : int
        The width of the window.
    height : int
        The height of the window.
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (width / 2))
    y_coordinate = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")


def select_units_and_login() -> tuple:
    """
    Creates a GUI for selecting units and entering login credentials.

    Returns
    -------
    tuple
        A tuple containing the login credentials and the list of selected unit codes.
    """

    def on_submit(event=None):
        login = login_entry.get()
        password = password_entry.get()
        selected_units = [unit_var.get() for unit_var in unit_vars if unit_var.get()]

        if not login or not password:
            messagebox.showwarning("Campos obrigatórios", "Por favor, preencha o login e a senha.")
            return
        if not selected_units:
            messagebox.showwarning("Seleção de Unidades", "Por favor, selecione pelo menos uma unidade.")
            return

        root.login = login
        root.password = password
        root.selected_units = selected_units
        root.quit()  # Close the window and end the mainloop

    root = tk.Tk()
    root.title("Presos por Ala")

    # Adjust the size of the window to fit the title
    width = 500
    height = 350
    center_window(root, width, height)

    # Login and Password Input
    tk.Label(root, text="Digite seu login (Canaimé):").pack(pady=5)
    login_entry = tk.Entry(root, width=40)
    login_entry.pack(pady=5)
    login_entry.focus()  # Set focus to login entry

    tk.Label(root, text="Digite sua senha:").pack(pady=5)
    password_entry = tk.Entry(root, show="*", width=40)
    password_entry.pack(pady=5)

    # Checkbox for Unit Selection
    frame = tk.Frame(root)
    frame.pack(pady=10, anchor=tk.W, padx=20)
    tk.Label(frame, text="Selecione uma ou mais unidades:").pack(anchor=tk.W)

    unit_vars = []
    for unit in units:
        var = tk.StringVar(value="")
        checkbox = tk.Checkbutton(frame, text=unit, variable=var, onvalue=unit, offvalue="")
        checkbox.pack(anchor=tk.W)
        unit_vars.append(var)

    # Button to submit and continue
    submit_button = tk.Button(root, text="Confirmar", command=on_submit)
    submit_button.pack(pady=20)  # Ensure there is space around the button

    root.bind('<Return>', on_submit)  # Allow pressing Enter to submit

    root.mainloop()
    return getattr(root, 'login', ''), getattr(root, 'password', ''), getattr(root, 'selected_units', [])
