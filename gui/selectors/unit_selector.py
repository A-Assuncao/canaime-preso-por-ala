import tkinter as tk
import sys

# Lista de unidades disponíveis
units = ('PAMC', 'CPBV', 'CPFBV', 'CPP', 'UPRRO')

# Lista de unidades ativas (modifique conforme necessário)
active_units = ['PAMC']  # Exemplo: adicione outras unidades ativas como 'CPBV', etc.


def center_window(window, width, height):
    """
    Centraliza a janela na tela.

    Parameters
    ----------
    window : tk.Tk or tk.Toplevel
        A janela a ser centralizada.
    width : int
        A largura da janela.
    height : int
        A altura da janela.
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (width / 2))
    y_coordinate = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")


def create_unit_checkbox(frame, unit, var, is_active):
    """
    Cria um checkbox para uma unidade, habilitado ou desabilitado conforme necessário.

    Parameters
    ----------
    frame : tk.Frame
        Frame onde o checkbox será inserido.
    unit : str
        Nome da unidade.
    var : tk.StringVar
        Variável associada ao valor do checkbox.
    is_active : bool
        Define se o checkbox deve estar habilitado ou desabilitado.
    """
    state = "normal" if is_active else "disabled"
    checkbox = tk.Checkbutton(frame, text=unit, variable=var, onvalue=unit, offvalue="", state=state)
    checkbox.pack(anchor=tk.W)
    return checkbox


def select_units() -> list:
    """
    Cria uma GUI para seleção de unidades.

    Returns
    -------
    list
        Uma lista com os códigos das unidades selecionadas.
    """
    window = tk.Tk()
    window.title("Seleção de Unidades")

    largura_janela, altura_janela = 300, 300
    center_window(window, largura_janela, altura_janela)
    window.attributes('-topmost', True)
    window.focus_force()

    def on_close():
        print("Fechando o programa...")
        window.quit()
        sys.exit(0)

    window.protocol("WM_DELETE_WINDOW", on_close)

    selected_units = []

    frame = tk.Frame(window)
    frame.pack(pady=10, padx=20, anchor=tk.W)

    tk.Label(frame, text="Selecione uma unidade:").pack(anchor=tk.W)

    unit_vars = []
    pre_select_unit = len(active_units) == 1  # Pré-seleciona a única unidade ativa, se for o caso

    # Exibe as unidades ativas com checkboxes habilitados
    for unit in units:
        if unit in active_units:
            var = tk.StringVar(value="")
            checkbox = create_unit_checkbox(frame, unit, var, is_active=True)
            if pre_select_unit and unit == active_units[0]:
                checkbox.select()  # Pré-seleciona a unidade se for a única ativa
            unit_vars.append(var)

    # Seção de unidades inativas
    tk.Label(frame, text="Breve para outras Unidades:", fg="gray").pack(anchor=tk.W, pady=(10, 0))

    # Exibe checkboxes desabilitados para as unidades inativas
    for unit in units:
        if unit not in active_units:
            var = tk.StringVar(value="")
            create_unit_checkbox(frame, unit, var, is_active=False)

    def submit_units():
        nonlocal selected_units
        selected_units = [var.get() for var in unit_vars if var.get()]  # Captura unidades selecionadas
        window.quit()  # Fecha o loop principal
        window.destroy()  # Fecha a janela

    btn = tk.Button(window, text="Confirmar", command=submit_units)
    btn.pack(pady=20)

    window.mainloop()  # Inicia o loop principal da janela

    return selected_units


if __name__ == '__main__':
    print(select_units())
