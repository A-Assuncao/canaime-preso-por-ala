"""
Adaptador do Playwright.

Fornece uma interface para interagir com o navegador usando o Playwright.
"""
from playwright.sync_api import sync_playwright
from utils.logger import Logger

logger = Logger.get_logger()


class PlaywrightAdapter:
    """
    Adaptador para o Playwright, permitindo interação com navegadores web.
    
    Attributes
    ----------
    headless : bool
        Indica se o navegador deve ser executado em modo headless
    playwright : object
        Instância do Playwright
    browser : object
        Instância do navegador
    page : object
        Instância da página atual
    """
    
    def __init__(self, headless=True):
        """
        Inicializa o adaptador do Playwright.
        
        Parameters
        ----------
        headless : bool, optional
            Indica se o navegador deve ser executado em modo headless
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
    
    def __enter__(self):
        """
        Inicializa o Playwright e o navegador quando usado como contexto.
        
        Returns
        -------
        PlaywrightAdapter
            A própria instância do adaptador
        """
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Finaliza o Playwright e o navegador quando sai do contexto.
        
        Parameters
        ----------
        exc_type : type
            Tipo da exceção, se houver
        exc_val : Exception
            Valor da exceção, se houver
        exc_tb : traceback
            Traceback da exceção, se houver
        """
        self.close()
    
    def initialize(self):
        """
        Inicializa o Playwright e o navegador.
        
        Returns
        -------
        bool
            True se a inicialização foi bem-sucedida, False caso contrário
        """
        try:
            logger.info("Inicializando o Playwright")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.page = self.browser.new_page()
            logger.info("Playwright inicializado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao inicializar o Playwright: {str(e)}", exc_info=True)
            Logger.capture_error(e)
            return False
    
    def navigate(self, url):
        """
        Navega para uma URL.
        
        Parameters
        ----------
        url : str
            URL para navegar
            
        Returns
        -------
        bool
            True se a navegação foi bem-sucedida, False caso contrário
        """
        try:
            logger.info(f"Navegando para {url}")
            self.page.goto(url)
            return True
        except Exception as e:
            logger.error(f"Erro ao navegar para {url}: {str(e)}", exc_info=True)
            Logger.capture_error(e)
            return False
    
    def fill_form(self, selector, value):
        """
        Preenche um campo de formulário.
        
        Parameters
        ----------
        selector : str
            Seletor CSS do campo
        value : str
            Valor a ser preenchido
            
        Returns
        -------
        bool
            True se o preenchimento foi bem-sucedido, False caso contrário
        """
        try:
            logger.debug(f"Preenchendo campo {selector}")
            self.page.fill(selector, value)
            return True
        except Exception as e:
            logger.error(f"Erro ao preencher campo {selector}: {str(e)}", exc_info=True)
            Logger.capture_error(e)
            return False
    
    def click(self, selector):
        """
        Clica em um elemento.
        
        Parameters
        ----------
        selector : str
            Seletor CSS do elemento
            
        Returns
        -------
        bool
            True se o clique foi bem-sucedido, False caso contrário
        """
        try:
            logger.debug(f"Clicando em {selector}")
            self.page.click(selector)
            return True
        except Exception as e:
            logger.error(f"Erro ao clicar em {selector}: {str(e)}", exc_info=True)
            Logger.capture_error(e)
            return False
    
    def get_text(self, selector):
        """
        Obtém o texto de um elemento.
        
        Parameters
        ----------
        selector : str
            Seletor CSS do elemento
            
        Returns
        -------
        str
            Texto do elemento ou None se ocorrer um erro
        """
        try:
            return self.page.text_content(selector)
        except Exception as e:
            logger.error(f"Erro ao obter texto de {selector}: {str(e)}", exc_info=True)
            Logger.capture_error(e)
            return None
    
    def get_element_count(self, selector):
        """
        Obtém a quantidade de elementos que correspondem a um seletor.
        
        Parameters
        ----------
        selector : str
            Seletor CSS dos elementos
            
        Returns
        -------
        int
            Quantidade de elementos ou 0 se ocorrer um erro
        """
        try:
            return self.page.locator(selector).count()
        except Exception as e:
            logger.error(f"Erro ao contar elementos {selector}: {str(e)}", exc_info=True)
            Logger.capture_error(e)
            return 0
    
    def close(self):
        """Fecha o navegador e finaliza o Playwright."""
        try:
            if self.browser:
                logger.info("Fechando o navegador")
                self.browser.close()
                
            if self.playwright:
                logger.info("Finalizando o Playwright")
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Erro ao fechar o Playwright: {str(e)}", exc_info=True)
            Logger.capture_error(e) 