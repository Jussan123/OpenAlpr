import os # Importa o modulo os para manipulacao de arquivos e diretorios
import sys  # Importa o modulo sys para manipulacao de variaveis do sistema
from openalpr import Alpr # Importa a Alpr class do modulo openalpr 

# Adicione o diretório da DLL ao caminho de pesquisa
dll_path = r'C:\openalpr_64'  # Substitua pelo caminho correto
os.environ['PATH'] = dll_path + ';' + os.environ['PATH']


alpr = Alpr("BR", "openalpr.conf", "runtime_data") # Cria uma instancia da classe Alpr, passando o pais, o arquivo de configuracao e o diretorio de dados em tempo de execucao
if not alpr.is_loaded(): # Verifica se o modulo foi carregado corretamente
    print("Error loading OpenALPR") # Se nao foi carregado, imprime uma mensagem de erro
    sys.exit(1) # Encerra o programa

alpr.set_top_n(20) # Define o numero de placas que serao retornadas
alpr.set_default_region("br") # Define a regiao padrao'BR' para o Brasil

image_path = r"imagens/image5.png"
if not os.path.exists(image_path):
    print(f"Erro: O caminho da imagem {image_path} não existe.")
    sys.exit(1)
    #results = alpr.recognize_file("imagens/image.png") # Chama o metodo recognize_file passando o caminho da imagem a ser reconhecida
results = alpr.recognize_file(image_path) # Chama o metodo recognize_file passando o caminho da imagem a ser reconhecida
print(results) # Imprime os resultados


i=0
for plate in results['results']: # Itera sobre as placas reconhecidas
    i += 1
    print("Plate #%d" % i) # Imprime o numero da placa
    print("   %12s %12s" % ("Plate", "Confidence")) # Imprime o cabecalho da tabela
    for candidate in plate['candidates']: # Itera sobre os candidatos
        prefix = "-" # Inicializa o prefixo com '-'
        if candidate['matches_template']: # Verifica se o candidato corresponde ao template
            prefix = "*" # Se corresponder, atribui '*' ao prefixo

        print("  %s %12s%12f" % (prefix, candidate['plate'], candidate['confidence'])) # Imprime o prefixo, a placa e a confianca

# Call when completely done to release memory
alpr.unload() # Libera a memoria alocada pelo modulo