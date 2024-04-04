from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


def find_element(driver):
    try:
        element = driver.find_element(By.ID, "img_captcha")
        return element if element else False
    except NoSuchElementException:
        return False

def extrair_codigo_seguranca(url):
    """
    Extrai o código de segurança da página web informada.

    Args:
        url: A URL da página web que contém o código de segurança.

    Returns:
        O código de segurança extraído da página web.
    """

    # Criar opções do Chrome
    options = Options()
    # Adicionar opções desejadas, como modo headless
    # options.add_argument('--headless')

    # Criar um driver do Chrome usando as opções
    driver = webdriver.Chrome()

    try:
        # Acessar a página web
        driver.get(url)

        # Criar um WebDriverWait com tempo limite de 20 segundos
        wait = WebDriverWait(driver, 100)
        imagem_captcha = wait.until(find_element)

        if not imagem_captcha:
            print(f"Elemento com o ID 'img_captcha' não encontrado na página '{url}'.")
            return None

        # Acessar o atributo "src" da imagem
        url_imagem = imagem_captcha.get_attribute("src")
        print(url_imagem)
        codigo_gerado_element = wait.until(find_element)
        codigo_gerado = codigo_gerado_element.text
        print(codigo_gerado_element)
        print(f"Código gerado: '{codigo_gerado}'")
        # Retornar o código de segurança e a URL da imagem
        return codigo_gerado, url_imagem

    except TimeoutException:
        print(f"Tempo limite excedido ao tentar encontrar o elemento na página '{url}'.")
        return None, None

    finally:
        # Fechar o navegador
        driver.quit()

# Exemplo de uso
url = "http://nfce.set.rn.gov.br/portalDFE/NFCe/mDadosNFCe.aspx?p=24240408030363003369652180002760151004422582%7C2%7C1%7C1%7C0D21EEA6C5C78EEFF9A9B98ED95E74669804F19F"
codigo_seguranca, url_imagem = extrair_codigo_seguranca(url)

if codigo_seguranca:
    print(f"Código de segurança: {codigo_seguranca}")
    print(f"URL da imagem: {url_imagem}")
else:
    print("Falha ao extrair o código de segurança.")
