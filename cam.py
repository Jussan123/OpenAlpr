import cv2
import os
import sys
from openalpr import Alpr

# Adicione o diretório da DLL ao caminho de pesquisa
dll_path = r'C:\openalpr_64'
os.environ['PATH'] = dll_path + ';' + os.environ['PATH']

def initialize_alpr():
    alpr = Alpr("BR", "openalpr.conf", "runtime_data")
    if not alpr.is_loaded():
        print("Error loading OpenALPR")
        sys.exit(1)
    alpr.set_top_n(20)
    alpr.set_default_region("br")
    return alpr

def open_video_stream(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Erro ao abrir o stream de vídeo")
        sys.exit(1)
    return cap

def save_image(plate, frame):
    output_dir = 'c:\\temp'
    # Garantir que o diretório 'prints' seja criado corretamente
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Diretório '{output_dir}' criado com sucesso.")
        except Exception as e:
            print(f"Erro ao criar o diretório '{output_dir}': {e}")
            return
    
    if frame is None:
        print(f"Erro: frame é None para a placa {plate}")
        return
    
    filename = os.path.join(output_dir, f'{plate}.jpg')
    
    result, img_encoded = cv2.imencode('.jpg', frame)
    if not result:
        print(f"Erro ao codificar a imagem para a placa {plate}")
        return
    
    try:
        with open(filename, 'wb') as f:
            f.write(img_encoded.tobytes())
            print(f"Imagem salva com sucesso para a placa {plate} em {filename}")
    except Exception as e:
        print(f"Erro ao salvar a imagem para a placa {plate}: {e}")

def draw_rectangle(frame, coordinates):
    cv2.rectangle(frame, (coordinates[0]['x'], coordinates[0]['y']), 
                  (coordinates[2]['x'], coordinates[2]['y']), (0, 255, 0), 2)

def main():
    alpr = initialize_alpr()
    video_path = r"imagens/ALPR_Test.mp4"
    cap = open_video_stream(video_path)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Erro ao ler o frame do vídeo")
            break
        
        result, img_encoded = cv2.imencode('.jpg', frame)
        if not result:
            print("Erro ao codificar o frame em JPEG")
            continue
        
        img_str = img_encoded.tobytes()
        results = alpr.recognize_array(img_str)

        for plate in results['results']:
            for candidate in plate['candidates']:
                print("  %12s %12f" % (candidate['plate'], candidate['confidence']))
            
            save_image(plate['plate'], frame)
            draw_rectangle(frame, plate['coordinates'])

        cv2.imshow('frame', frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    alpr.unload()

if __name__ == "__main__":
    main()
