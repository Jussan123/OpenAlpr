import cv2
import os
import sys
from openalpr import Alpr
import requests
from collections import Counter
import logging
import time

# Configuração do logging
logging.basicConfig(filename='alpr_errors.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(message)s')

# Adicione o diretório da DLL ao caminho de pesquisa
dll_path = r'C:\openalpr_64'
os.environ['PATH'] = dll_path + ';' + os.environ['PATH']

def initialize_alpr():
    alpr = Alpr("br", "openalpr.conf", "runtime_data")
    if not alpr.is_loaded():
        logging.error("Error loading OpenALPR")
        sys.exit(1)
    alpr.set_top_n(10)
    alpr.set_default_region("br")
    return alpr

def open_video_stream(video_path, max_attempts=5):
    attempts = 0
    cap = None
    while attempts < max_attempts:
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            return cap
        attempts += 1
        logging.error(f"Falha ao abrir o stream de vídeo, tentativa {attempts}")
        time.sleep(2)  # Espera 2 segundos antes de tentar novamente
    logging.error("Falha ao abrir o stream de vídeo após várias tentativas")
    sys.exit(1)

def save_image(plate, frame):
    output_dir = 'c:\\temp'
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Diretório '{output_dir}' criado com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao criar o diretório '{output_dir}': {e}")
            return
    
    if frame is None:
        logging.error(f"Erro: frame é None para a placa {plate}")
        return
    
    filename = os.path.join(output_dir, f'{plate}.jpg')
    result, img_encoded = cv2.imencode('.jpg', frame)
    if not result:
        logging.error(f"Erro ao codificar a imagem para a placa {plate}")
        return
    
    try:
        with open(filename, 'wb') as f:
            f.write(img_encoded.tobytes())
            print(f"Imagem salva com sucesso para a placa {plate} em {filename}")
    except Exception as e:
        logging.error(f"Erro ao salvar a imagem para a placa {plate}: {e}")

def draw_rectangle(frame, coordinates):
    cv2.rectangle(frame, (coordinates[0]['x'], coordinates[0]['y']),
                  (coordinates[2]['x'], coordinates[2]['y']), (0, 255, 0), 2)

def is_valid_plate(plate):
    if len(plate) != 7:
        return False
    if not (plate[:3].isalpha() and plate[3].isdigit() and
            (plate[4].isdigit() or plate[4].isalpha()) and plate[5:].isdigit()):
        return False
    return True

def send_to_api(plate, camera_id):
    email = "admin@email.com"
    password = "admin@123"
    try:
        loginApi = requests.post("https://apicondsecurity.azurewebsites.net/api/Usuario/LoginApp", json={"email": email, "senha": password})
        if loginApi.status_code != 200:
            logging.error(f"Erro ao fazer login na API: {loginApi.status_code} - {loginApi.text}")
            return

        login_data = loginApi.json()
        Token = login_data.get("token")
        if not Token:
            logging.error("Erro ao obter token de autorização")
            return
        
        url = "https://apicondsecurity.azurewebsites.net/api/VeiculoUsuario/GetPlaca"
        headers = {
            "Authorization": f"Bearer {Token}"
        }
        data = {
            "placa": plate,
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            print(f"Dados enviados com sucesso para a API: {response.json()}")
            abrePortao = requests.post("https://apicondsecurity.azurewebsites.net/api/AbrePortao/AberturaPortao", json={"placa": plate, "idPortao": camera_id}, headers=headers)
        else:
            abrePortaoTerceiro = requests.post("https://apicondsecurity.azurewebsites.net/api/AbrePortao/ReceberTerceiro", json={"placa": plate, "idPortao": camera_id}, headers=headers)
            logging.error(f"Erro ao enviar dados para a API: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Exceção ao enviar dados para a API: {e}")
        print(f"Erro ao enviar dados para a API: {e}")
    except ValueError as e:
        logging.error(f"Erro ao decodificar a resposta JSON: {e}")
        print(f"Erro ao decodificar a resposta JSON: {e}")

def main():
    alpr = initialize_alpr()
    video_path = r"imagens/ALPR_Test.mp4"
    #video_path = "http://192.168.1.13:80"  # Substitua pela URL correta da sua câmera IP
    cap = open_video_stream(video_path)

    plate_counter = Counter()
    last_processed_time = {}
    camera_id = "1"
    min_interval = 60

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            logging.error("Erro ao ler o frame do vídeo")
            break

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        result, img_encoded = cv2.imencode('.jpg', frame)
        if not result:
            logging.error("Erro ao codificar o frame em JPEG")
            continue
        
        img_str = img_encoded.tobytes()
        results = alpr.recognize_array(img_str)

        if results['results']:
            for plate in results['results']:
                for candidate in plate['candidates']:
                    plate_text = candidate['plate']
                    confidence = candidate['confidence']
                    if is_valid_plate(plate_text):
                        plate_counter[plate_text] += 1
                        print(f"Placa: {plate_text} Confiança: {confidence}")
                
                draw_rectangle(frame, plate['coordinates'])

            if plate_counter:
                most_common_plate = plate_counter.most_common(1)[0][0]
                current_time = time.time()
                if most_common_plate not in last_processed_time or current_time - last_processed_time[most_common_plate] > min_interval:
                    save_image(most_common_plate, frame)
                    print(f"Placa mais comum: {most_common_plate}")
                    send_to_api(most_common_plate, camera_id)
                    print(f"Placa {most_common_plate} enviada para a API")
                    last_processed_time[most_common_plate] = current_time
            else:
                logging.info("Nenhuma placa válida encontrada até agora.")

        cv2.imshow('frame', frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    alpr.unload()

if __name__ == "__main__":
    main()
