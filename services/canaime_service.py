from playwright.sync_api import Page, TimeoutError
from utils.logger import Logger

logger = Logger.get_logger()

class CanaimeLogin:
    def __init__(self, p, headless=True, login='', password='', use_https=True):
        self.p = p
        self.headless = headless
        self.login = login
        self.password = password
        self.use_https = use_https
        self.browser = None
        self.page = None

    def perform_login(self) -> (Page, object):
        try:
            self.browser = self.p.chromium.launch(headless=self.headless)
            context = self.browser.new_context(java_script_enabled=False)
            context.set_extra_http_headers(
                {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})
            context.route("**/*",
                          lambda route: route.abort() if route.request.resource_type == "image" else route.continue_())

            self.page = context.new_page()
            protocol = 'https' if self.use_https else 'http'
            url = f'{protocol}://canaime.com.br/sgp2rr/login/login_principal.php'
            
            try:
                logger.info(f"Tentando acessar {url}")
                self.page.goto(url, timeout=30000)  # 30 segundos de timeout
            except TimeoutError:
                logger.error(f"Timeout ao tentar acessar {url}")
                raise Exception(f"O site demorou muito para responder. Verifique sua conexão ou tente novamente mais tarde.")
            except Exception as e:
                logger.error(f"Erro ao acessar {url}: {str(e)}", exc_info=True)
                raise Exception(f"Não foi possível acessar o site. Verifique sua conexão ou tente usar HTTP se o certificado estiver expirado.")

            try:
                self.page.locator("input[name=\"usuario\"]").click()
                self.page.locator("input[name=\"usuario\"]").fill(self.login)
                self.page.locator("input[name=\"senha\"]").fill(self.password)
                self.page.locator("input[name=\"senha\"]").press("Enter")
            except Exception as e:
                logger.error(f"Erro ao preencher formulário de login: {str(e)}", exc_info=True)
                raise Exception("Não foi possível preencher o formulário de login. O site pode estar com problemas.")

            return self.page, self.browser  # Retorna a página e o navegador

        except Exception as e:
            if self.browser:
                self.browser.close()
            raise e

    def close_browser(self):
        """
        Fecha o navegador explicitamente quando não for mais necessário.
        """
        if self.browser:
            self.browser.close()
            self.browser = None
