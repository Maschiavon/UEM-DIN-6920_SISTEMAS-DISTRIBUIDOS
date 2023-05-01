import socket
import tqdm
import os
import math
import time
import re
import PySimpleGUI as sg


def tela():
    sg.ChangeLookAndFeel("DarkGrey3")

    # Layout
    layout = [[sg.Text("Selecione um dos métodos pré-definidos:", font="Roboto")],
              [sg.Radio("1) Round Robin padrão", "group1", key="RRpadrao", font="Roboto",
                        default=True)],
              [sg.Radio("2)  S1 - TCP, S2 e S3 - UDP com Round Robin", "group1", key="S2S3UDP", font="Roboto")],
              [sg.Radio("3) Teste UDP", "group1", key="UDP", font="Roboto")],
              [sg.Text("\nInsira os IP's dos Servidores:", font="Roboto")],
              [sg.Text("1º IP:", font="Roboto"), sg.Input(default_text="", size=(15, 0), key="ip1"),
               sg.Text("2º IP:", font="Roboto"), sg.Input(default_text="", size=(15, 0), key="ip2"),
               sg.Text("3º IP:", font="Roboto"), sg.Input(default_text="", size=(15, 0), key="ip3")],
              [sg.Button("Executar", font="Roboto"), sg.Button("Get IP", font="Roboto"),
               sg.Text("Seu IP:", font="Roboto", key="txtMeuIP")],
              [sg.Output(size=(60, 12), key="output", font="Roboto")]]

    # Janela
    janela = sg.Window('Computador Cliente', layout, icon=r'./ic.ico')

    while True:
        # Extrair os dados da tela
        event, values = janela.Read()

        # Get Ip
        if event == "Get IP":
            hostname = socket.gethostbyname(socket.gethostname())
            janela['txtMeuIP'].update("Seu IP: " + str(hostname))
            janela['ip1'].update(hostname)

        # Executar
        elif event == "Executar":
            # Pega as opções
            janela.FindElement("output").Update("")
            op1 = values["RRpadrao"]
            op2 = values["S2S3UDP"]
            op3 = values["UDP"]

            # Pega IP's adicionais
            ip1 = values["ip1"]
            ip2 = values["ip2"]
            ip3 = values["ip3"]
            ip_list = [x for x in [ip1, ip2, ip3] if x != '']

            if op1:
                RRpadrao(ip_list, 1) # Round robin padrão
            elif op2:
                RRpadrao(ip_list, 2) # TCP, UDP, UDP
            elif op3:
                RRpadrao(ip_list, 3) # UDP TESTE
            else:
                print("Erro nas operações ?")

        # Fechar Janela
        else:
            break


def modo2cliente(UDP_IP, UDP_PORT):
    Buffer_Size = 1024
    MESSAGE = "Hello, World!\n"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(bytes(MESSAGE, "utf-8"), (UDP_IP, UDP_PORT))

    while True:
        bytesAP = sock.recvfrom(Buffer_Size)
        message = bytesAP[0]
        adress = bytesAP[1]
        clientMsg = "Messagem do Servidor:{}".format(message.decode())
        clientIP = "Ip do Servidor:{}".format(adress)

        print(clientMsg)
        print(clientIP)

        if (message.decode() != None):
            break


def RRpadrao(ip_list, modo):
    print("Round Robin Padrão")
    print("Lista IP's:\n", ip_list)

    # Info adicional
    tam_iplist = len(ip_list)
    directory = 'Problemas Matematicos'
    tempo_total = time.time()
    portas = [5000, 5001, 5002]

    file_list = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)

        if os.path.isfile(f):
            f_abs = os.path.abspath(f)
            print("Arquivo: ", filename)
            file_list.append(f_abs)

    # Tamanho dos problemas
    tamanho = len(file_list)
    Impar = (True if tamanho % 2 == 1 else False)

    # Exemplo de distribuição: 7 prob / 2 ip = 4 prob pra cada pc
    calc = math.ceil(tamanho / tam_iplist)  # 4
    ip_pos = 0

    # Escolhendo modo de envio
    SEPARATOR = "<SEPARATOR>"

    if modo == 2:
        tam_iplist = 1  # só o primeiro é TCP
        calc = tamanho  # 6
    if modo == 3:
        tam_iplist = 0

    # Envia o número de problemas para cada computador
    for i in range(0, tam_iplist):
        # Se for impar o ultimo pc processa - 1
        num_calc = (calc - 1 if Impar & i == tam_iplist else calc)

        # Faz o envio do número de problemas e metodo de envio com tcp
        s = socket.socket()  # TCP é o padrão
        print(f"[+] Conectando à {ip_list[i]}:{portas[i]}")
        s.connect((ip_list[i], portas[i]))
        print("[+] Conectado.")
        s.send(f"{str(num_calc)}{SEPARATOR}{modo}".encode())
        s.close()

    # Envia todos os arquivos sequencialmente na forma de Round Robin padrão
    if modo != 3:
        for i in range(0, tamanho):
            time.sleep(0.05)
            envia_arquivo(ip_list[ip_pos], portas[ip_pos], file_list[i])
            ip_pos += 1
            if ip_pos == tam_iplist:
                ip_pos = 0

    ip_pos = 0
    # Receber a Resposta de forma Sequencial
    for i in range(0, tam_iplist):
        num_calc = (calc - 1 if Impar & i == tam_iplist else calc)
        recebe_arquivo_sequencial(ip_list[i], num_calc, portas[i])
        ip_pos += 1
        if ip_pos == tam_iplist:
            ip_pos = 0

    if modo == 2:
        for ip in ip_list[1:]:
            modo2cliente(ip, 5000)
    elif modo == 3:
        modo2cliente(ip_list[0], 5000)

    duracao_total = time.time() - tempo_total
    print("Tempo Total: ", duracao_total)
    return 0


def envia_arquivo(host, port, filename):
    SEPARATOR = "<SEPARATOR>"
    BUFFER_SIZE = 4096 # envia 4096 bytes a cada passo de tempo

    filesize = os.path.getsize(filename)

    #  criar o soquete do servidor de acordo com o tcp
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
                # a transmissão do arquivo está feita
                break
            # usamos sendall para garantir a transmissão em
            # redes ocupadas
            s.sendall(bytes_read)
            # atualizar a barra de progresso
            progress.update(len(bytes_read))
    # feche o socket
    s.close()


def recebe_arquivo_sequencial(ip, num_files, porta):
    savepath_resp = 'Respostas'
    # Verifique se o caminho especificado existe ou não
    isExist = os.path.exists(savepath_resp)
    if not isExist:
        # Crie um novo diretório porque ele não existe
        os.makedirs(savepath_resp)

    count = 0
    while True:
        # Printa o IP do servidor
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((ip, 80))
        print("\nIP Server: ", s.getsockname()[0])
        SERVER_HOST = s.getsockname()[0]
        s.close()

        SERVER_PORT = porta
        # receber 4096 bytes de cada vez
        BUFFER_SIZE = 4096
        SEPARATOR = "<SEPARATOR>"

        #  criar o soquete do servidor de acordo com o tcp
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # vincular o soquete ao nosso endereço local
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

        # receber as informações do arquivo
        # usando o soquete do cliente, não o soquete do servidor
        received = client_socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)

        # remova o caminho absoluto se houver
        filename = os.path.basename(filename)

        # converter para inteiro
        filesize = re.search(r'\d+', filename).group()
        filesize = int(filesize)
        filename = os.path.join(savepath_resp, filename)

        # comece a receber o arquivo do soquete
        # e grave no fluxo de arquivo
        progress = tqdm.tqdm(range(filesize), f"\nRecebendo {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                # ler 1024 bytes do soquete (receber)
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    # nada é recebido
                    # a transmissão do arquivo é concluída
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
        if count == num_files:
            break
    print("\nFULL BREAK")


if __name__ == '__main__':
    tela()
