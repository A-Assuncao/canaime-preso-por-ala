import requests
from bs4 import BeautifulSoup
import logging
import os
import sys
from dotenv import load_dotenv
from pathlib import Path
import urllib3

# Configurar paths do projeto
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils'))
from logger import Logger

logger = Logger.get_logger()

# Carrega variáveis de ambiente
load_dotenv()
load_dotenv(Path(__file__).parents[2] / ".env")

class CanaimeLogin:
    def __init__(self, headless=True, login='', password=''):
        self.login = login or os.getenv("CANAIME_USER", "")
        self.password = password or os.getenv("CANAIME_PASSWORD", "")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Desabilitar verificação SSL para permitir certificados expirados
        self.session.verify = False
        
        # Suprimir avisos de requests sobre verificação SSL desabilitada
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self._logged_in = False

    def perform_login(self):
        """
        Realiza o login no sistema Canaimé usando requests
        
        Returns:
            tuple: (session, None) - Mantém a mesma interface do código anterior
        """
        try:
            base_url = os.getenv("CANAIME_BASE_URL", "https://canaime.com.br")
            login_url = f"{base_url}/sgp2rr/login/login_principal.php"
            logger.info(f"Tentando acessar {login_url} (verificação SSL desabilitada)")
            
            logger.info("Iniciando o login...")
            
            # Primeiro, obtém os cookies iniciais
            response = self.session.get(login_url, verify=False)
            response.raise_for_status()
            logger.info(f"Obteve resposta inicial com status: {response.status_code}")
            
            # Prepara os dados de login
            login_data = {
                'usuario': self.login,
                'senha': self.password
            }
            
            # Realiza o login
            logger.info(f"Realizando login com usuário: {self.login}")
            login_response = self.session.post(login_url, data=login_data, allow_redirects=True, verify=False)
            login_response.raise_for_status()
            logger.info(f"Resposta do login: status={login_response.status_code}, url={login_response.url}")
            
            # Verifica se o login foi bem-sucedido
            # Login bem-sucedido deve redirecionar para index_areas.php
            # Login mal-sucedido permanece em login_principal.php ou redireciona para index.php
            success_url = f"{base_url}/sgp2rr/areas/index_areas.php"
            if "login_principal.php" in login_response.url:
                logger.error("Falha no login: ainda na página de login")
                raise Exception("Falha no login. Verifique suas credenciais.")
            elif "index.php" in login_response.url and "areas" not in login_response.url:
                logger.error("Falha no login: redirecionado para página incorreta")
                raise Exception("Falha no login. Verifique suas credenciais.")
            elif success_url not in login_response.url:
                logger.error(f"Falha no login: URL inesperada - {login_response.url}")
                raise Exception("Falha no login. Verifique suas credenciais.")
            
            # Verifica também o conteúdo da página para confirmar o login
            if "Usuário ou senha inválidos" in login_response.text or "login_principal.php" in login_response.text:
                logger.error("Falha no login: mensagem de erro encontrada no conteúdo")
                raise Exception("Falha no login. Verifique suas credenciais.")
            
            # Se chegamos aqui, o login foi bem-sucedido
            self._logged_in = True
            logger.info("Login realizado com sucesso")
            
            # Retorna a sessão e None para manter compatibilidade com a interface anterior
            return self.session, None

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao realizar login: {e}")
            raise Exception(f"Erro ao acessar o sistema: {str(e)}")
        except Exception as e:
            logger.error(f"Erro durante o login: {e}")
            raise

    def close_browser(self):
        """
        Método mantido para compatibilidade com a interface anterior.
        Não é necessário fechar nada quando usando requests.
        """
        pass

    def get_page_content(self, url):
        """
        Obtém o conteúdo de uma página usando a sessão autenticada
        
        Args:
            url: URL da página a ser acessada
            
        Returns:
            str: Conteúdo HTML da página
        """
        if not self._logged_in:
            raise Exception("É necessário fazer login antes de acessar páginas")
            
        try:
            response = self.session.get(url, verify=False)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao acessar página {url}: {e}")
            raise Exception(f"Erro ao acessar página: {str(e)}")

    def get_soup(self, url):
        """
        Obtém um objeto BeautifulSoup da página
        
        Args:
            url: URL da página a ser acessada
            
        Returns:
            BeautifulSoup: Objeto BeautifulSoup da página
        """
        content = self.get_page_content(url)
        return BeautifulSoup(content, 'html.parser')
