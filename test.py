import cv2

# Caminho da imagem
print("testee")
#image_path = "/l/disk0/caios/Downloads/casa-hidrometro.jpg"
image_path = "/l/disk0/caios/Downloads/COMPROVANTE_CUPOM_FISCAL_215001202311116105607_page-0001.jpg"

# Tentar ler a imagem
img = cv2.imread(image_path)

# Verificar se a imagem foi carregada corretamente
if img is None:
    print("Erro ao abrir a imagem.")
else:
    # Mostrar a imagem em uma janela separada
    cv2.imshow("Imagem", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()