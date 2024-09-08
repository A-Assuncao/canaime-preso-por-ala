from playwright.sync_api import Page


class CanaimeLogin:
    def __init__(self, p, headless=True, login='', password=''):
        self.p = p
        self.headless = headless
        self.login = login
        self.password = password
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
            self.page.goto('https://canaime.com.br/sgp2rr/login/login_principal.php', timeout=0)
            self.page.locator("input[name=\"usuario\"]").click()
            self.page.locator("input[name=\"usuario\"]").fill(self.login)
            self.page.locator("input[name=\"senha\"]").fill(self.password)
            self.page.locator("input[name=\"senha\"]").press("Enter")
            return self.page, self.browser  # Retorna a página e o navegador

        except Exception as e:
            raise e

    def close_browser(self):
        """
        Fecha o navegador explicitamente quando não for mais necessário.
        """
        if self.browser:
            self.browser.close()
            self.browser = None
