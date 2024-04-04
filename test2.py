from selenium import webdriver
from selenium.webdriver.common.by import by
from pil import image
import pytesseract
from captcha_solver import solve_captcha
import time

def main():
    driver = webdriver.chrome()
    driver.get("http://nfce.set.rn.gov.br/portaldfe/nfce/mdadosnfcev2.aspx?chnfce=24240408030363003369652180002760151004422582&token=f5a2f030fe25bf8b7aa0a744da1032b1")

    captcha_image = driver.find_element(by.id, "img_captcha")
    captcha_image.screenshot("captcha.png")

    time.sleep(5)  # aguarda 5 segundos

    captcha_solution = solve_captcha("captcha.png")

    captcha_input = driver.find_element(by.id, "txt_cod_antirobo")  # verifique se o id está correto
    captcha_input.send_keys(captcha_solution)

    submit_button = driver.find_element(by.id, "btnconsultar")
    submit_button.click()

    driver.quit()  # mantenha essa linha para visualizar mensagens ou alertas

if __name__ == "__main__":
    main()