import cv2
import time
import os
import numpy as np
from flet import *
import flet as ft
import pytesseract
import sqlite3
import locale
import re
from selenium import webdriver
import webbrowser
import requests
from bs4 import BeautifulSoup



pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
tessdata_dir_config = '/usr/share/tesseract-ocr/4.00/tessdata'

def create_table_if_not_exists():
    conn = sqlite3.connect('notas_fiscais.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notas_fiscais
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, loja TEXT, endereco_loja TEXT, cnpj_loja TEXT, 
                 descricao_produto TEXT, valor_produto REAL)''')
    conn.commit()
    conn.close()

def insert_nota_fiscal(loja, endereco_loja, cnpj_loja, descricao_produto, valor_produto):
    try:
        conn = sqlite3.connect('notas_fiscais.db')
        c = conn.cursor()
        c.execute('''INSERT INTO notas_fiscais (loja, endereco_loja, cnpj_loja, descricao_produto, valor_produto)
                     VALUES (?, ?, ?, ?, ?)''', (loja, endereco_loja, cnpj_loja, descricao_produto, valor_produto))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Erro ao inserir dados no banco de dados:", e)
        return False
files = Column() 
def main(page: Page):
    create_table_if_not_exists()  

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

    def take_me_picture(e):
        remove_all_you_photo()
        cap = cv2.VideoCapture(0)
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

    locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')

    def extract_info_from_image(image_path):
        img = cv2.imread(image_path)
        if img is None:
            print("Failed to read image file:", image_path)
            return
        text = pytesseract.image_to_string(img, lang="por", config=tessdata_dir_config)
        info_dict = {
            'Loja': None,
            'Endereço da loja': None,
            'CNPJ da loja': None,
            'Descrição do produto': None,
            'Valor total do produto': None,
            'Quantidade total de itens': None,
            'Valor total da compra': None
        }

        lines = text.split('\n')

        for line in lines[:2]: 
            if line.strip(): 
                info_dict['Loja'] = line.strip()
                break

        for i, line in enumerate(lines):
            if 'Endereço' in line:
                info_dict['Endereço da loja'] = lines[i + 1].strip()
                break

        for line in lines:
            if 'CNPJ' in line:
                info_dict['CNPJ da loja'] = line.split(' ')[1]
                break

        for line in lines:
            if 'NCM' in line:
                info_dict['Descrição do produto'] = lines[lines.index(line) - 1].strip()
                break

        valor_pattern = r'(VALOR TOTAL R\$|TOTAL \(=\)|VALOR PAGO R\$|VALOR).*?([\d.,]+\d{2})'
        for line in lines:
            match = re.search(valor_pattern, line, re.IGNORECASE)
            if match:
                valor_str = match.group(2).replace('.', '').replace(',', '.')
                info_dict['Valor total da compra'] = float(valor_str)
                break

        confirm_dialog = AlertDialog(
            title=Text("Confirme os valores extraídos"),
            content=Column([
                Text(f"Loja: {info_dict['Loja']}"),
                Text(f"Endereço da loja: {info_dict['Endereço da loja']}"),
                Text(f"CNPJ da loja: {info_dict['CNPJ da loja']}"),
                Text(f"Descrição do produto: {info_dict['Descrição do produto']}"),
                Text(f"Valor total da compra: {info_dict['Valor total da compra']}")
            ]),
            actions=[
                TextButton("Confirmar", on_click=lambda e: confirm_values(info_dict)),
                TextButton("Editar", on_click=lambda e: edit_info(info_dict, page))
            ]
        )
        page.dialog = confirm_dialog
        confirm_dialog.open = True
        page.update()

    def confirm_values(info_dict):
        if insert_nota_fiscal(info_dict['Loja'], info_dict['Endereço da loja'], info_dict['CNPJ da loja'],
                            info_dict['Descrição do produto'], info_dict['Valor total da compra']):
            print("Valores confirmados e salvos com sucesso!")
            page.dialog.open = False
            page.update()
        else:
            print("Erro ao salvar os valores!")

    def edit_info(info_dict, page):
        edit_dialog = ft.AlertDialog(
            title=ft.Text("Editar valores extraídos"),
            content=ft.Column([
                ft.TextField(label="Loja", value=info_dict['Loja']),
                ft.TextField(label="Endereço da loja", value=info_dict['Endereço da loja']),
                ft.TextField(label="CNPJ da loja", value=info_dict['CNPJ da loja']),
                ft.TextField(label="Descrição do produto", value=info_dict['Descrição do produto']),
                ft.TextField(label="Valor total da compra", value=str(info_dict['Valor total da compra']))
            ]),
            actions=[
                ft.TextButton("Salvar", on_click=lambda e: save_edited_info(info_dict, edit_dialog, page)),
                ft.TextButton("Cancelar", on_click=lambda e: cancel_edit(edit_dialog))
            ]
        )
        page.dialog = edit_dialog
        edit_dialog.open = True
        page.update()

    def save_edited_info(info_dict, edit_dialog, page):
        info_dict['Loja'] = edit_dialog.content.controls[0].value
        info_dict['Endereço da loja'] = edit_dialog.content.controls[1].value
        info_dict['CNPJ da loja'] = edit_dialog.content.controls[2].value
        info_dict['Descrição do produto'] = edit_dialog.content.controls[3].value
        info_dict['Valor total da compra'] = float(edit_dialog.content.controls[4].value)
        print("Valores editados:", info_dict)
        # Salvar os valores atualizados no banco de dados
        if insert_nota_fiscal(info_dict['Loja'], info_dict['Endereço da loja'], info_dict['CNPJ da loja'],
                            info_dict['Descrição do produto'], info_dict['Valor total da compra']):
            print("Valores editados foram salvos com sucesso no banco de dados!")
            edit_dialog.open = False
            page.update()
        else:
            print("Erro ao salvar os valores editados no banco de dados!")
        edit_dialog.open = False
        page.update()

    def cancel_edit(dialog):
        dialog.open = False

    # def read_qr_code(e):
    #     cap = cv2.VideoCapture(0)
    #     while True:
    #         ret, frame = cap.read()
    #         if not ret:
    #             break
    #         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #         detector = cv2.QRCodeDetector()
    #         data, points, _ = detector.detectAndDecode(gray)
    #         if data:
    #             print(f"QR Code data: {data}")
    #             open_url(data)
    #             cap.release()
    #             cv2.destroyAllWindows()
    #             break
    #         cv2.imshow("QR CODE Detection", frame)
    #         if cv2.waitKey(1) & 0xFF == ord("q"):
    #             break
    #     if cap.isOpened():
    #         cap.release()
    #         cv2.destroyAllWindows()

    # def open_url(url):
    #     try:
    #         # Abrir o navegador padrão do sistema com a URL
    #         webbrowser.open(url)
    #     except Exception as ex:
    #         print(f"Erro ao abrir a URL: {ex}")

    # def print_nota_fiscal(content):
    #     print("Conteúdo da nota fiscal:")
    #     print(content)

    # def extract_info_from_nota_fiscal(content):
    #     # Extrair as informações da nota fiscal aqui
    #     # Atualize esta função de acordo com a estrutura do conteúdo da nota fiscal
    #     pass

    # def handle_nota_fiscal(content):
    #     print_nota_fiscal(content)
    #     extract_info_from_nota_fiscal(content)

    # def on_code_entered(code):
    #     print("Código da nota fiscal inserido:", code)
    #     # Acessar o conteúdo da nota fiscal usando o código inserido
    #     content = fetch_nota_fiscal_content(code)
    #     if content:
    #         handle_nota_fiscal(content)
    #     else:
    #         print("Erro ao obter o conteúdo da nota fiscal")

    # def fetch_nota_fiscal_content(code):
    #     # Simulando o acesso ao conteúdo da nota fiscal com o código inserido
    #     # Aqui você deve implementar a lógica para obter o conteúdo da nota fiscal usando o código
    #     # Neste exemplo, estamos apenas retornando uma string fixa
    #     return "Conteúdo da nota fiscal retornado com sucesso"

    # # Chamada de função para simular o código inserido manualmente
    # on_code_entered("123456")
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
                print(f"QR Code data: {data}")
                handle_nota_fiscal(data)
                cap.release()
                cv2.destroyAllWindows()
                break
            cv2.imshow("QR CODE Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        if cap.isOpened():
            cap.release()
            cv2.destroyAllWindows()

    def handle_nota_fiscal(url):
        # Fazer solicitação POST para obter a página com o código gerado
        response = requests.post(url)
        if response.status_code == 200:
            content = response.content
            # Extrair o código de segurança do conteúdo HTML
            codigo_seguranca = extrair_codigo_seguranca(content)
            if codigo_seguranca:
                print(f"Código de segurança extraído: {codigo_seguranca}")
                # Solicitar ao usuário para inserir o código de segurança
                input_codigo = input("Por favor, insira o código de segurança para acessar a nota fiscal: ")
                if input_codigo == codigo_seguranca:
                    print("Código de segurança válido. Acessando o conteúdo da nota fiscal...")
                    # Aqui você pode continuar o processamento da nota fiscal
                    # Exemplo: fazer outra solicitação HTTP para obter o conteúdo da nota fiscal
                    # e extrair as informações necessárias
                else:
                    print("Código de segurança inválido. Acesso negado.")
            else:
                print("Não foi possível extrair o código de segurança da página.")
        else:
            print(f"Erro ao acessar a página: {response.status_code}")

    def extrair_codigo_seguranca(content):
        # Parsear o conteúdo HTML usando BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        # Encontrar todos os elementos span na página
        spans = soup.find_all("span")
        # Iterar sobre os elementos span para encontrar o que contém o texto "Código Gerado:"
        for span in spans:
            if "Código Gerado:" in span.text:
                # Encontrar o próximo elemento irmão após o elemento span
                codigo_seguranca = span.find_next_sibling().text.strip()
                return codigo_seguranca
        return None
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
            files_to_upload = [f.path for f in file_picker.result.files]
            for file_path in files_to_upload:
                extract_info_from_image(file_path)
            file_picker.upload(files_to_upload)

    page.overlay.append(file_picker)

    page.add(
        Column([
            Text("Select an option:", size=30, weight="bold"),
            ElevatedButton("Take a Photo",
                           bgcolor="blue",
                           color="white",
                           on_click=take_me_picture),
            myimage,
            Divider(),
            Text("Read QR Code from Your Phone", size=30, weight="bold"),
            ElevatedButton("Read QR Code",
                           bgcolor="blue",
                           color="white",
                           on_click=read_qr_code),
            Text("Result QR Code", size=20, weight="bold"),
            Divider(),
            myresult
        ]),
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
    )

app(target=main)
