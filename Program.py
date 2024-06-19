#import connectionAPI
import cv2 # Importa a biblioteca OpenCV
import os # Importa a biblioteca os
import sys # Importa a biblioteca sys
from openalpr import Alpr # Importa a classe Alpr da biblioteca openalpr
import requests # Importa a biblioteca requests
from collections import Counter # Importa a classe Counter da biblioteca collections
import logging # Importa a biblioteca logging
import time # Importa a biblioteca time

# Configuração do logging
logging.basicConfig(filename='alpr_errors.log', level=logging.ERROR, # Cria um arquivo de log chamado 'alpr_errors.log' e define o nível de log como ERROR
                    format='%(asctime)s %(levelname)s %(message)s') # Define o formato do log com data, nível de log e mensagem

# Adicione o diretório da DLL ao caminho de pesquisa
dll_path = r'C:\openalpr_64' # Define o caminho da DLL do OpenALPR como 'C:\openalpr_64'
os.environ['PATH'] = dll_path + ';' + os.environ['PATH'] # Adiciona o caminho da DLL ao PATH do sistema operacional (Windows) para que o OpenALPR possa ser carregado corretamente

def initialize_alpr(): # Define a função initialize_alpr que inicializa o objeto Alpr com as configurações necessárias
    alpr = Alpr("BR", "openalpr.conf", "runtime_data") # Cria um objeto Alpr para o Brasil com o arquivo de configuração 'openalpr.conf' e os dados em tempo de execução 'runtime_data'
    if not alpr.is_loaded(): # Verifica se o objeto Alpr foi carregado corretamente (se não houver erros) 
        logging.error("Error loading OpenALPR") # Registra um erro no log se houver um problema ao carregar o OpenALPR 
        sys.exit(1) # Encerra o programa com código de erro 1 em caso de falha ao carregar o OpenALPR
    alpr.set_top_n(10) # Define o número máximo de placas a serem retornadas como 20 (top 20) para aumentar a precisão da detecção de placas 
    alpr.set_default_region("br") # Define a região padrão como "br" (Brasil) para melhorar o reconhecimento de placas brasileiras 
    return alpr # Retorna o objeto Alpr inicializado com as configurações adequadas 

def open_video_stream(video_path): # Define a função open_video_stream que abre o stream de vídeo a partir de um arquivo ou URL
    cap = cv2.VideoCapture(video_path) # Cria um objeto de captura de vídeo usando o caminho do arquivo de vídeo ou URL fornecido
    if not cap.isOpened(): # Verifica se o objeto de captura de vídeo foi aberto corretamente
        logging.error("Erro ao abrir o stream de vídeo") # Registra um erro no log se houver um problema ao abrir o stream de vídeo
        sys.exit(1) # Encerra o programa com código de erro 1 em caso de falha ao abrir o stream de vídeo
    return cap # Retorna o objeto de captura de vídeo para ser usado posteriormente

def save_image(plate, frame): # Define a função save_image que salva a imagem do frame associada a uma placa específica
    output_dir = 'c:\\temp' # Define o diretório de saída como 'c:\\temp' para salvar as imagens das placas detectadas
    if not os.path.exists(output_dir): # Verifica se o diretório de saída existe
        try: 
            os.makedirs(output_dir) # Cria o diretório de saída 'c:\\temp' se ele não existir
            print(f"Diretório '{output_dir}' criado com sucesso.") # Exibe uma mensagem informando que o diretório foi criado com sucesso
        except Exception as e: 
            logging.error(f"Erro ao criar o diretório '{output_dir}': {e}") # Registra um erro no log se houver um problema ao criar o diretório de saída 
            return
    
    if frame is None: # Verifica se o frame é None (nulo) 
        logging.error(f"Erro: frame é None para a placa {plate}") # Registra um erro no log se o frame for nulo
        return 
    
    filename = os.path.join(output_dir, f'{plate}.jpg') # Define o nome do arquivo de saída com base na placa detectada e a extensão .jpg
    
    result, img_encoded = cv2.imencode('.jpg', frame) # Codifica o frame em formato JPEG para salvar como imagem 
    if not result: # Verifica se houve um erro ao codificar a imagem 
        logging.error(f"Erro ao codificar a imagem para a placa {plate}") # Registra um erro no log se houver um problema ao codificar a imagem
        return
    
    try:
        with open(filename, 'wb') as f: # Abre o arquivo de saída no modo de gravação binária ('wb') para salvar a imagem codificada
            f.write(img_encoded.tobytes()) # Escreve os bytes da imagem codificada no arquivo de saída 
            print(f"Imagem salva com sucesso para a placa {plate} em {filename}") # Exibe uma mensagem informando que a imagem foi salva com sucesso
    except Exception as e:
        logging.error(f"Erro ao salvar a imagem para a placa {plate}: {e}") # Registra um erro no log se houver um problema ao salvar a imagem

def draw_rectangle(frame, coordinates): # Define a função draw_rectangle que desenha um retângulo ao redor da placa detectada no frame 
    cv2.rectangle(frame, (coordinates[0]['x'], coordinates[0]['y']),  # Desenha um retângulo com base nas coordenadas da placa detectada 
                  (coordinates[2]['x'], coordinates[2]['y']), (0, 255, 0), 2) # As coordenadas são usadas para definir os cantos do retângulo e a cor da borda (verde) e a espessura (2 pixels)

def is_valid_plate(plate): # Define a função is_valid_plate que verifica se a placa detectada é válida (formato ABC1234) 
    if len(plate) < 7: # Verifica se a placa tem menos de 7 caracteres (formato mínimo ABC1234)
        return False
# Verifica se os primeiros 3 caracteres são letras e os últimos 2 são dígitos e o 4º é um digito (formato ABC1234 ou ABC1A23)
    return plate[:3].isalpha() and plate[3].isdigit() and plate[4:].isdigit()  # placa de 7 digitos com 4 letras e 3 numeros ou 3 letras e 4 numeros sendo o 4 digito um numero os 2 ultimos digitos sao numeros e os 3 primeiros sao letras

def send_to_api(plate, camera_id): # Define a função send_to_api que envia os dados da placa para uma API REST 
    email = "admin@email.com" # Define o email do usuário para fazer login na API REST
    password = "admin@123" # Define a senha do usuário para fazer login na API REST
    try:
        loginApi = requests.post("https://apicondsecurity.azurewebsites.net/api/Usuario/LoginApp", json={"email": email, "senha": password}) # Envia uma solicitação POST para fazer login na API REST com o email e senha fornecidos
        Token = loginApi.json()["token"] # Obtém o token de autorização da resposta da API REST para acessar os endpoints protegidos
        url = "https://apicondsecurity.azurewebsites.net/api/VeiculoUsuario/Get" # Define a URL da API REST para enviar os dados da placa 
        data = { # Define os dados a serem enviados para a API REST
            "authorization": Token, # Token de autorização para acessar a API
            "placa": plate, # Dados da placa detectada
        }
        data = requests.post(url, json=data) # Envia uma solicitação POST para a URL da API com os dados da placa em formato JSON
        if data.status_code == 200: # Verifica se a solicitação foi bem-sucedida (código de status 200)
            print(f"Dados enviados com sucesso para a API: {data.json()}") # Exibe uma mensagem informando que os dados foram enviados com sucesso
            abrePortao = requests.post("https://apicondsecurity.azurewebsites.net/api/AbrePortao/AberturaPortao", json={"placa": plate, "idPortao": camera_id}) # Envia uma solicitação POST para a URL da API com os dados da placa em formato JSON
        else:
            abrePortaoTerceiro = requests.post("https://apicondsecurity.azurewebsites.net/api/AbrePortao/ReceberTerceiro", json={"placa": plate, "idPortao": camera_id}) # Envia uma solicitação POST para a URL da API com os dados da placa em formato JSON
       
            logging.error(f"Erro ao enviar dados para a API: {data.status_code} - {data.text}") # Registra um erro no log se houver um problema ao enviar os dados para a API
    except Exception as e:
        logging.error(f"Exceção ao enviar dados para a API: {e}") # Registra um erro no log se houver uma exceção ao enviar os dados para a API
        print(f"Erro ao enviar dados para a API: {e}") # Exibe uma mensagem de erro se houver uma exceção ao enviar os dados para a API

def main():
    alpr = initialize_alpr() # Inicializa o objeto Alpr com as configurações adequadas
    video_path = r"imagens/ALPR_Test.mp4" # Define o caminho do arquivo de vídeo para teste
    # pass video stream link here
    # video_path = "http://localhost:81/stream"
    cap = open_video_stream(video_path) # Abre o stream de vídeo a partir do arquivo de vídeo ou URL fornecido


    plate_counter = Counter()
    last_processed_time = {}  # 
    camera_id = "1" # Define o ID da câmera como "camera_01" para identificar a câmera que detectou a placa
    min_interval =  60  # Define o intervalo mínimo entre processamentos da mesma placa (em segundos) para evitar processamento repetido

    while True:
        ret, frame = cap.read() # Lê um frame do stream de vídeo 
        if not ret or frame is None: # Verifica se o frame foi lido corretamente e não é nulo
            logging.error("Erro ao ler o frame do vídeo") # Registra um erro no log se houver um problema ao ler o frame do vídeo 
            continue 
        
        result, img_encoded = cv2.imencode('.jpg', frame) # Codifica o frame em formato JPEG para processamento 
        if not result:
            logging.error("Erro ao codificar o frame em JPEG") # Registra um erro no log se houver um problema ao codificar o frame 
            continue
        
        img_str = img_encoded.tobytes() # Converte a imagem codificada em bytes para uma string para ser processada pelo OpenALPR 
        results = alpr.recognize_array(img_str) # Processa a imagem para detectar placas de veículos  

        if results['results']: # Verifica se foram encontradas placas de veículos na imagem
            for plate in results['results']: # Itera sobre as placas detectadas na imagem
                for candidate in plate['candidates']: # Itera sobre os candidatos de placa para cada placa detectada
                    plate_text = candidate['plate'] # Obtém o texto da placa do candidato 
                    confidence = candidate['confidence'] # Obtém a confiança do candidato (probabilidade de acerto)
                    if is_valid_plate(plate_text): # Verifica se a placa detectada é válida (formato ABC1234)
                        plate_counter[plate_text] += 1 # Incrementa o contador da placa detectada  
                        print(f"Placa: {plate_text} Confiança: {confidence}") # Exibe a placa detectada e a confiança do candidato
                
                draw_rectangle(frame, plate['coordinates']) # Desenha um retângulo ao redor da placa detectada no frame

            # Process the most common plate if it hasn't been processed yet or was processed more than 5 minutes ago
            if plate_counter: # Verifica se há placas detectadas válidas 
                most_common_plate = plate_counter.most_common(1)[0][0] # Obtém a placa mais comum (com maior contagem)  
                current_time = time.time() # Obtém o tempo atual em segundos  
                if (most_common_plate not in last_processed_time or  # Verifica se a placa mais comum ainda não foi processada ou foi processada há mais de 5 minutos
                        current_time - last_processed_time[most_common_plate] > min_interval): # Verifica se o intervalo de tempo desde o último processamento é maior que 5 minutos
                    save_image(most_common_plate, frame) # Salva a imagem associada à placa mais comum
                    print(f"Placa mais comum: {most_common_plate}") # Exibe a placa mais comum no log
                    send_to_api(most_common_plate, camera_id) # Envia os dados da placa mais comum para a API REST
                    print(f"Placa {most_common_plate} enviada para a API") # Exibe uma mensagem informando que a placa foi enviada para a API
                    last_processed_time[most_common_plate] = current_time # Atualiza o tempo de processamento da placa mais comum
            else:
                logging.info("Nenhuma placa válida encontrada até agora.") # Registra uma mensagem de informação no log se nenhuma placa válida for encontrada

        cv2.imshow('frame', frame) # Exibe o frame com as placas detectadas e o retângulo desenhado 

        if cv2.waitKey(1) == 27: # Verifica se a tecla ESC foi pressionada para sair do loop
            break

    cap.release()
    cv2.destroyAllWindows()
    alpr.unload()

if __name__ == "__main__":
    main()
