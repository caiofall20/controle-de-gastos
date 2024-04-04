from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image, ImageChops, ImageGrab
import pytesseract
from captcha_solver import solve_captcha
import time

def segment_captcha(image_path):
    # Abre a imagem do captcha
    captcha_image = Image.open(image_path)

    # Localiza a área do captcha (atualizado com suas coordenadas)
    captcha_area = (
        int(2170),  # Coordenada X do canto superior esquerdo (substitua se necessário)
        int(1026),  # Coordenada Y do canto superior esquerdo (substitua se necessário)
        int(2170 + 100),  # Coordenada X do canto inferior direito
        int(1026 + 50),  # Coordenada Y do canto inferior direito
    )

    # Recorta a imagem do captcha
    segmented_captcha = captcha_image.crop(captcha_area)

    # Salva a imagem do captcha segmentada
    segmented_captcha.save("segmented_captcha.png")

    return segmented_captcha

def main():
    driver = webdriver.Chrome()
    driver.get("http://nfce.set.rn.gov.br/portalDFE/NFCe/mDadosNFCeV2.aspx?chNFCe=24240408030363003369652180002760151004422582&Token=F5A2F030FE25BF8B7AA0A744DA1032B1")

    # Captura a tela toda
    screenshot = driver.get_screenshot_as_png()

    # Salva a tela toda como imagem
    with open("screenshot.png", "wb") as f:
        f.write(screenshot)

    # Busca a localização do elemento captcha na tela capturada
    captcha_image_element = driver.find_element(By.ID, "img_captcha")
    captcha_image_location = captcha_image_element.location
    captcha_image_size = captcha_image_element.size

    # Recorta a área da imagem do captcha a partir da imagem capturada
    captcha_screenshot = Image.open("screenshot.png")
    captcha_screenshot = captcha_screenshot.crop((
        int(captcha_image_location['x']),
        int(captcha_image_location['y']),
        int(captcha_image_location['x'] + captcha_image_size['width']),
        int(captcha_image_location['y'] + captcha_image_size['height'])))
    captcha_screenshot.save("captcha.png")

    # Continuação do seu código original a partir daqui
    print("Captcha image saved successfully!")  # Confirma a captura

    # Aguarda 5 segundos
    time.sleep(5)

    # Segmenta o captcha
    segmented_captcha = segment_captcha("captcha.png")

    # Envia a imagem segmentada para o captcha_solver
    captcha_solution = solve_captcha("segmented_captcha.png")

    captcha_input = driver.find_element(By.ID, "txt_cod_antirobo")
    captcha_input.send_keys(captcha_solution)

    # Localiza e clica no botão "btnVerDanfe"
    submit_button = driver.find_element(By.ID, "btnVerDanfe")
    submit_button.click()

    driver.quit()  # Mantenha essa linha para visualizar mensagens ou alertas

if __name__ == "__main__":
    main()