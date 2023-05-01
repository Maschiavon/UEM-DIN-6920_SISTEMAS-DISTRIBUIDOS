import socket
import tqdm
import os
import time
import re
import math
import PySimpleGUI as sg


def tela():
    sg.ChangeLookAndFeel("DarkGrey3")

    # Layout
    layout = [[sg.Text("Este é o PC SERVIDOR, Veja as informações:", font="Roboto")],
              [sg.Text("IP Origem:", font="Roboto"), sg.Input(default_text="", size=(15, 0), key="ip_origem"),
               sg.Text("Porta:", font="Roboto"), sg.Input(default_text="5000", size=(7, 0), key="porta")],
              [[sg.Text("Selecione um dos métodos pré-definidos:", font="Roboto")],
              [sg.Radio("1) TCP", "group1", key="TCP", font="Roboto", default=True), sg.Radio("2) UDP", "group1", key="UDP", font="Roboto")]],
              [sg.Button("Executar", font="Roboto"), sg.Button("Get IP", font="Roboto"), sg.Text("Seu IP:", font="Roboto", key="txtMeuIP")],
              [sg.Output(size=(60, 12), key="output", font="Roboto")]]

    # Janela
    janela = sg.Window('Computador Servidor', layout, icon=r'./ic.ico')

    while True:
        # Extrair os dados da tela
        event, values = janela.Read()

        # Pegar Ip
        if event == "Get IP":
            hostname = socket.gethostbyname(socket.gethostname())
            janela['txtMeuIP'].update("Seu IP: " + str(hostname))
            janela['ip_origem'].update(hostname)

        # Executar
        elif event == "Executar":
            ip_origem = values["ip_origem"]

            tcp = values["TCP"]
            udp = values["UDP"]
            porta = int(values["porta"])
            janela.FindElement("output").Update("")

            if tcp:
                # Pega o número de problemas
                num_files, modo = getNumberOfFiles(ip_origem, porta)

                # Por padrão o número de problemas é 6
                recebe_arquivo_sequencial(ip_origem, num_files, porta)
            elif udp:
                modo2servidor(ip_origem, porta)
            else:
                print("Erro")

        # Fechar Janela
        else:
            break


def modo2servidor(UDP_IP, UDP_PORT):
    Buffer_Size = 1024
    MESSAGE = "Mensagem recebida!\n"

    bytesToSend = str.encode(MESSAGE)
    socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socketUDP.bind((UDP_IP, UDP_PORT))

    print("Ouvindo ...")
    while True:
        bytesAP = socketUDP.recvfrom(Buffer_Size)
        message = bytesAP[0]
        adress = bytesAP[1]
        clientMsg = "Messagem do Cliente:{}".format(message.decode())
        clientIP = "Ip do Cliente:{}".format(adress)

        print(clientMsg)
        print(clientIP)

        socketUDP.sendto(bytesToSend, adress)
        break

def getNumberOfFiles(ip_origem, porta):
    # Printar endereço IP do dispositivo
    s = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM) # UDP
    s.connect((ip_origem, 80))
    print("IP Origem: ", s.getsockname()[0])
    SERVER_HOST = s.getsockname()[0]
    s.close()

    SERVER_PORT = porta
    # receber 4096 bytes de cada vez
    BUFFER_SIZE = 4096
    SEPARATOR = "<SEPARATOR>"

    # usando tcp (SOCK_STREAM) ao inves de udp (socket.SOCK_DGRAM)
    # para pegar informações
    s = socket.socket()

    # liga o socket ao nosso endereço local
    s.bind((SERVER_HOST, SERVER_PORT))

    # permite que nosso servidor aceite conexões
    # 5 aqui é o número de conexões não aceitas que
    # o sistema permitirá antes de recusar novas conexões
    s.listen(5)
    print(f"[*] Ouvindo á {SERVER_HOST}:{SERVER_PORT}")

    # aceitar conexão se houver alguma
    client_socket, address = s.accept()
    # se o código abaixo for executado, isso significa que o remetente está conectado
    print(f"[+] {address} está conectad.")

    # recebendo as informações do arquivo
    # receba usando o soquete do cliente, não o soquete do servidor
    received = client_socket.recv(BUFFER_SIZE).decode()
    number_of_files, modo = received.split(SEPARATOR)
    print("Numero de arquivos:", number_of_files)

    # feche o soquete do cliente
    client_socket.close()
    # feche o soquete do servidor
    s.close()

    return int(number_of_files), modo


def envia_arquivo(host, port, filename):
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096 # envia 4096 bytes a cada passo de tempo

    filesize = os.path.getsize(filename)

    # criar o soquete do cliente
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"[+] Conectando à {host}:{port}")
    s.connect((host, port))
    print("[+] Conectado.")

    # envie o nome do arquivo e o tamanho do arquivo
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    # comece a enviar o arquivo
    progress = tqdm.tqdm(range(filesize), f"\nEnviando {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            # leia os bytes do arquivo
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # a transmissão do arquivo é finalizada
                break
            # usamos sendall para garantir a transmissão em
            # redes ocupadas
            s.sendall(bytes_read)
            # atualizar a barra de progresso
            progress.update(len(bytes_read))
    # feche o socket
    s.close()


def envia_arquivo_sequencial(ip_origem, porta):
    print("Enviando arquivo...\n")

    # Informações adicionais adicional
    directory = 'Respostas'
    tempo_total = time.time()

    file_list = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)

        if os.path.isfile(f):
            f_abs = os.path.abspath(f)
            print("Arquivo: ", filename)
            # print("Abs: ", f_abs)
            file_list.append(f_abs)

    for i in range(0, len(file_list)):
        time.sleep(0.01)
        envia_arquivo(ip_origem, porta, file_list[i])

    return 0


def processa_Problemas_sequencial():
    print("Processando Problemas...")

    count = 1
    directory = 'Problemas Matematicos'
    savepath_resp = 'Respostas'
    # Verifique se o caminho especificado existe ou não
    isExist = os.path.exists(savepath_resp)
    if not isExist:
        # Crie um novo diretório se ele não existe
        os.makedirs(savepath_resp)

    # itera sobre os arquivos
    # daquele diretorio
    duracao_acumulativa = 0
    tempo_total = time.time()
    for filename in os.listdir(directory):
        start = time.time()
        f = os.path.join(directory, filename)
        # verifica se é arquivo
        if os.path.isfile(f):
            # Abre o arquivo e armazena linha por linha em
            # um vetor de strings sem o \n no final
            print("Arquivo: ", filename)
            with open(f) as arquivo:
                linhas = [linha.rstrip() for linha in arquivo]

            resp_nome = os.path.join(savepath_resp, "r" + str(count) + ".txt")
            r = open(resp_nome, "w")
            for linha in linhas:
                resp = eval(linha)
                duration = time.time() - start
                duracao_acumulativa += duration
                # print("Resposta: ", res)
                print("Duração: ", duration)
                print("T Acumulado: ", duracao_acumulativa)
                r.write(str(duration))
            r.close()
            count += 1
    duracao_total = time.time() - tempo_total
    print("Tempo Total: ", duracao_total)


def recebe_arquivo_sequencial(ip_origem, num_files, porta):
    savepath = 'Problemas Matematicos'
    # Verifique se o caminho especificado existe ou não
    isExist = os.path.exists(savepath)
    if not isExist:
        # Crie um novo diretório se ele não existe
        os.makedirs(savepath)

    count = 0
    while True:
        # Printar endereço IP do dispositivo
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
        s.connect((ip_origem, 80))
        print("\nIP Origem: ", s.getsockname()[0])
        SERVER_HOST = s.getsockname()[0]
        s.close()

        SERVER_PORT = porta
        # receber 4096 bytes de cada vez
        BUFFER_SIZE = 4096
        SEPARATOR = "<SEPARATOR>"

        # criar o soquete tcp do servidor
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind the socket to our local address
        s.bind((SERVER_HOST, SERVER_PORT))

        # permitindo que nosso servidor aceite conexões
        # 5 aqui é o número de conexões não aceitas que
        # o sistema permitirá antes de recusar novas conexões
        s.listen(5)
        print(f"[*] Ouvindo como {SERVER_HOST}:{SERVER_PORT}")

        # aceita conexão se houver alguma
        client_socket, address = s.accept()
        # se o código abaixo for executado, isso significa que o remetente está conectado
        print(f"[+] {address} está conectado.")

        # recebendo as informações do arquivo
        # receba usando o soquete do cliente, não o soquete do servidor
        received = client_socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)

        # remova o caminho absoluto se houver
        filename = os.path.basename(filename)

        # converter para inteiro
        filesize = re.search(r'\d+', filename).group()  # Bug Bizarro
        filesize = int(filesize)
        filename = os.path.join(savepath, filename)

        # comece a receber o arquivo do soquete
        # e grave no fluxo de arquivo
        progress = tqdm.tqdm(range(filesize), f"\nRecebendo {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                # lê 1024 bytes do socket (receive)
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    # se nada é recebido
                    # a transmissão do arquivo é concluída
                    f.close()
                    count += 1
                    break
                # escreva no arquivo os bytes que acabamos de receber
                f.write(bytes_read)
                # atualizar a barra de progresso
                progress.update(len(bytes_read))

        # feche o soquete do cliente
        client_socket.close()
        # feche o soquete do servidor
        s.close()

        # Se bater no numero de arquivos saia
        if count == num_files:
            break

    print("\nFULL BREAK")
    processa_Problemas_sequencial()
    envia_arquivo_sequencial(ip_origem, porta)


if __name__ == '__main__':
    tela()
