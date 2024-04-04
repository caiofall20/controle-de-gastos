import pytesseract
from PIL import Image

def solve_captcha(image_path):
    captcha_image = Image.open(image_path)
    captcha_text = pytesseract.image_to_string(captcha_image)
    print(captcha_text)
    print(f"Captcha text: {captcha_text}")
    return captcha_text