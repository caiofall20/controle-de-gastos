from PIL import Image
import pytesseract

# Abre a imagem do captcha
image = Image.open("screenshot.png")



# Extrai o texto da imagem segmentada
captcha_text = pytesseract.image_to_string(image)

# Imprime o texto do captcha
print(captcha_text)