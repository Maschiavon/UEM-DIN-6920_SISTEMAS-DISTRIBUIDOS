import PySimpleGUI as sg
import socket


def tela():
    sg.ChangeLookAndFeel("DarkBlue14")

    # Layout
    layout = [[sg.Text("Selecione um dos métodos pré-definidos:", font="Roboto")],
              [sg.Text("Insira os IP's dos Servidores:", font="Roboto")],
              [sg.Text("1º IP:", font="Roboto"), sg.Input(default_text="", size=(20, 0), key="ip1"),
               sg.Text("2º IP:", font="Roboto"), sg.Input(default_text="", size=(20, 0), key="ip2"),
               sg.Text("3º IP:", font="Roboto"), sg.Input(default_text="", size=(20, 0), key="ip3")],
              [sg.Text("Mensgem:", font="Roboto"), sg.Input(default_text="", size=(75, 0), key="msg")],
              [sg.Button("Executar", font="Roboto"), sg.Button("Get IP", font="Roboto"),
               sg.Text("Seu IP:", font="Roboto", key="txtMeuIP")],
              [sg.Output(size=(60, 12), key="output", font="Roboto")]]

    # Janela
    janela = sg.Window('Computador Cliente', layout, icon=r'./ic.ico')

    while True:
        # Extrair os dados da tela
        event, values = janela.Read()

        # Get Pegar
        if event == "Get IP":
            hostname = socket.gethostname()
            IPAddr = socket.gethostbyname(hostname)
            janela['txtMeuIP'].update("Seu IP: " + str(IPAddr))
            janela['ip1'].update(IPAddr)

        # Executar
        elif event == "Executar":
            ip1 = values["ip1"]
            ip2 = values["ip2"]
            ip3 = values["ip3"]
            lista_ip = [x for x in [ip1, ip2, ip3] if x != '']
            print(lista_ip)
            try:
                # IP 1
                msg = values["msg"]  # msg = input("say> ")
                print("Enviando: " + msg)
                resp = upper_rcp(msg, lista_ip[0])
                print(f"echo> {resp}")
            except:
                try:
                    # IP 2
                    print("Deu Ruim na conexão com:" + str(lista_ip[0]))
                    print("Tentando com outro server:" + str(lista_ip[1]))
                    msg = values["msg"]  # msg = input("say> ")
                    print("Enviando novamente: " + msg)
                    resp = upper_rcp(msg, lista_ip[1])
                    print(f"echo> {resp}")
                except:
                    try:
                        # IP 3
                        print("Deu Ruim na conexão com:" + str(lista_ip[1]))
                        print("Tentando com ultimo server:" + str(lista_ip[2]))
                        msg = values["msg"]  # msg = input("say> ")
                        print("Enviando ultima vez: " + msg)
                        resp = upper_rcp(msg, lista_ip[2])
                        print(f"echo> {resp}")
                    except:
                        print("FERROU GERAL")

        # Fechar Janela
        else:
            break


HOST = "172.17.48.1"
PORT = 5001

def upper_rcp(msg, host):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, PORT))
    s.send(msg.encode())
    data = s.recv(1024)
    s.close()
    return data.decode()


if __name__ == "__main__":
    tela()
