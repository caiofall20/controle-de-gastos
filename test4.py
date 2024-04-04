from selenium import webdriver
from PIL import Image

def main():
    driver = webdriver.Chrome()
    driver.get("http://nfce.set.rn.gov.br/portalDFE/NFCe/mDadosNFCeV2.aspx?chNFCe=24240408030363003369652180002760151004422582&Token=F5A2F030FE25BF8B7AA0A744DA1032B1")

    # Captura a tela
    screenshot = driver.get_screenshot_as_png()

    # Salva a imagem
    with open("screenshot.png", "wb") as f:
        f.write(screenshot)

    # Abra a imagem capturada para verificar as coordenadas

    driver.quit()

if __name__ == "__main__":
    main()