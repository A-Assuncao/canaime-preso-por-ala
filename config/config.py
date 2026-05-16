
# Identidade do produto (nome comercial exibido ao usuário)
APP_DISPLAY_NAME = "Plantão Helper - PAMC"
APP_TAGLINE = "Planilhas, chamada e contagem por ala — integrado ao Canaimé"

# Identificador técnico (repositório, releases GitHub, nome do .exe baixado)
APP_NAME = "canaime-preso-por-ala"
APP_VERSION = "v1.4.0"
GITHUB_REPO = "A-Assuncao/canaime-preso-por-ala"  # Formato: "dono/repositório"


def app_window_title(*, with_version: bool = True) -> str:
    """Título da janela principal do aplicativo."""
    if with_version:
        return f"{APP_DISPLAY_NAME} {APP_VERSION}"
    return APP_DISPLAY_NAME
