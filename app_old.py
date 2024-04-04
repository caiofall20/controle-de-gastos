import cv2
import time
import os
import numpy as np
from flet import *
import pytesseract
import sqlite3

# Configurações do pytesseract (caminho para o executável e língua)
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
tessdata_dir_config = '/usr/share/tesseract-ocr/4.00/tessdata'

# Função para criar a tabela no banco de dados se ela não existir
def create_table_if_not_exists():
    conn = sqlite3.connect('notas_fiscais.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notas_fiscais
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, loja TEXT, endereco_loja TEXT, cnpj_loja TEXT, 
                 descricao_produto TEXT, valor_produto REAL)''')
    conn.commit()
    conn.close()

# Função para inserir uma nova nota fiscal no banco de dados
def insert_nota_fiscal(loja, endereco_loja, cnpj_loja, descricao_produto, valor_produto):
    conn = sqlite3.connect('notas_fiscais.db')
    c = conn.cursor()
    c.execute('''INSERT INTO notas_fiscais (loja, endereco_loja, cnpj_loja, descricao_produto, valor_produto)
                 VALUES (?, ?, ?, ?, ?)''', (loja, endereco_loja, cnpj_loja, descricao_produto, valor_produto))
    conn.commit()
    conn.close()


def main(page: Page):
    myimage = Image(
        src=False,
        width=300,
        height=300,
        fit="cover"
    )

    myresult = Column()

    def remove_all_you_photo():
        folder_path = "/l/disk0/caios/Imagens/"
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"File successfully removed: {file_path}")

    def take_me_picture(e):
        remove_all_you_photo()
        cap = cv2.VideoCapture(0)
        cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Webcam", 400, 600)
        timestamp = str(int(time.time()))
        myfileface = f"myCumFaceFile_{timestamp}.jpg"
        try:
            while True:
                ret, frame = cap.read()
                cv2.imshow("Webcam", frame)
                myimage.src = ""
                page.update()
                key = cv2.waitKey(1)
                if key == ord("q"):
                    break
                elif key == ord("s"):
                    cv2.imwrite(f"/l/disk0/caios/Imagens/{myfileface}", frame)
                    cv2.putText(frame, "YOU SUCCESSFULLY CAPTURED!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow("Webcam", frame)
                    cv2.waitKey(3000)
                    folder_path = "/l/disk0/caios/Imagens/"
                    myimage.src = folder_path + myfileface
                    page.update()
                    extract_info_from_image(folder_path + myfileface)
                    break
            cap.release()
            cv2.destroyAllWindows()
            page.update()
        except Exception as e:
            print(e)
            print("Failed to capture image!")

    def extract_info_from_image(image_path):
        img = cv2.imread(image_path)
        text = pytesseract.image_to_string(img, lang="por", config=tessdata_dir_config)
        info_dict = {}

        # Extrair informações relevantes da nota fiscal
        lines = text.split('\n')
        for line in lines:
            if 'Loja:' in line:
                info_dict['Loja'] = line.split(': ')[1]
            elif 'Endereço da loja:' in line:
                info_dict['Endereço da loja'] = line.split(': ')[1]
            elif 'CNPJ da loja:' in line:
                info_dict['CNPJ da loja'] = line.split(': ')[1]
            elif 'Descrição do produto:' in line:
                info_dict['Descrição do produto'] = line.split(': ')[1]
            elif 'Valor total do produto:' in line:
                info_dict['Valor total do produto'] = float(line.split(': ')[1].replace('R$', '').replace(',', '.'))

        # Inserir as informações no banco de dados
        if 'Loja' in info_dict and 'Endereço da loja' in info_dict and 'CNPJ da loja' in info_dict \
                and 'Descrição do produto' in info_dict and 'Valor total do produto' in info_dict:
            insert_nota_fiscal(info_dict['Loja'], info_dict['Endereço da loja'], info_dict['CNPJ da loja'],
                               info_dict['Descrição do produto'], info_dict['Valor total do produto'])

        # Adicionar informações extraídas à interface do usuário
        for key, value in info_dict.items():
            myresult.controls.append(Text(f"{key}: {value}", size=25, weight="bold"))
        page.update()

    def read_qr_code(e):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detector = cv2.QRCodeDetector()
            data, points, _ = detector.detectAndDecode(gray)
            if data:
                cv2.polylines(frame, [np.int32(points)], True, (255, 0, 0), 2, cv2.LINE_AA)
                print(f"QR Code data: {data}")
                myresult.controls.append(Text(data, size=25, weight="bold"))
                page.update()
                cap.release()
                cv2.destroyAllWindows()
                break
            cv2.imshow("QR CODE Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        if cap.isOpened():
            cap.release()
            cv2.destroyAllWindows()

    # def upload_image(e):
    #     file_path_input = TextEntry(placeholder="Enter the file path", width=300)
    #     submit_button = ElevatedButton("Submit", on_click=lambda e: submit_file_path(file_path_input))
    #     page.add(Column([file_path_input, submit_button]))

    # def submit_file_path(file_path_input):
    #     file_path = file_path_input.value
    #     if file_path and os.path.isfile(file_path):
    #         extract_info_from_image(file_path)
    #         myimage.src = file_path
    #         page.remove()  # Remover os campos de entrada após o envio
    #         page.update()
    #     else:
    #         page.alert("Invalid file path. Please try again.")

    prog_bars = {}
    files = Ref[Column]()
    upload_button = Ref[ElevatedButton]()

    def file_picker_result(e: FilePickerResultEvent):
        upload_button.current.disabled = True if e.files is None else False
        prog_bars.clear()
        files.current.controls.clear()
        if e.files is not None:
            for f in e.files:
                prog = ProgressRing(value=0, bgcolor="#eeeeee", width=20, height=20)
                prog_bars[f.name] = prog
                files.current.controls.append(Row([prog, Text(f.name)]))
        page.update()

    def on_upload_progress(e: FilePickerUploadEvent):
        prog_bars[e.file_name].value = e.progress
        prog_bars[e.file_name].update()

    file_picker = FilePicker(on_result=file_picker_result, on_upload=on_upload_progress)

    def upload_files(e):
        if file_picker.result is not None and file_picker.result.files is not None:
            for f in file_picker.result.files:
                # Processar a imagem aqui
                extract_info_from_image(f.path)
            file_picker.upload()

    # Oculta o diálogo em uma sobreposição
    page.overlay.append(file_picker)

    page.add(
        # Column([
        #     Text("Select an option:", size=30, weight="bold"),
        #     ElevatedButton("Take a Photo",
        #                    bgcolor="blue",
        #                    color="white",
        #                    on_click=take_me_picture),
        #     myimage,
        #     Divider(),
        #     Text("Read QR Code from Your Phone", size=30, weight="bold"),
        #     ElevatedButton("Read QR Code",
        #                    bgcolor="blue",
        #                    color="white",
        #                    on_click=read_qr_code),
        #     Text("Result QR Code", size=20, weight="bold"),
        #     Divider(),
        #     myresult
        # ]),
        ElevatedButton(
            "Select files...",
            icon=icons.FOLDER_OPEN,
            on_click=lambda _: file_picker.pick_files(allow_multiple=True),
        ),
        Column(ref=files),
        ElevatedButton(
            
            "Upload",
            ref=upload_button,
            icon=icons.UPLOAD,
            on_click=upload_files,
            disabled=True,
        ),
        myresult
    )

app(target=main, assets_dir="youphoto")
