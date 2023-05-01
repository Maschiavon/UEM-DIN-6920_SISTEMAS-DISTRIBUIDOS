import PySimpleGUI as sg
import socket


def tela():
    sg.ChangeLookAndFeel("DarkBlue14")

    # Layout
    layout = [[sg.Text("Este é o PC SERVIDOR, Veja as informações:", font="Roboto")],
              [sg.Text("IP Origem:", font="Roboto"), sg.Input(default_text="", size=(15, 0), key="ip_origem"),
               sg.Text("Porta:", font="Roboto"), sg.Input(default_text="5001", size=(7, 0), key="porta")],
              [sg.Button("Executar", font="Roboto"), sg.Button("Get IP", font="Roboto"), sg.Text("Seu IP:", font="Roboto", key="txtMeuIP")],
              [sg.Output(size=(60, 12), key="output", font="Roboto")]]

    # Janela
    janela = sg.Window('Computador Servidor', layout, icon=r'./ic.ico')

    while True:
        # Extrair os dados da tela
        event, values = janela.Read()

        # Pegar Ip
        if event == "Get IP":
            hostname = socket.gethostname()
            IPAddr = socket.gethostbyname(hostname)
            janela['txtMeuIP'].update("Seu IP: " + str(IPAddr))
            janela['ip_origem'].update(IPAddr)

        # Executar
        elif event == "Executar":
            HOST = socket.gethostname()
            PORT = 5001
            s = setup(HOST, PORT)

            Continue = True
            while Continue:
                Continue = upper_rpc(s)

        # Fechar Janela
        else:
            break


def setup(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    return s


def upper_rpc(s):
    (conn, addr) = s.accept()
    data = conn.recv(1024)

    if data:
        conn.send(data.upper())
        print(f"'{data.decode()}' from {addr}")

        s_data = str(data.upper())
        condicao = s_data == "b'BREAK'"
        if condicao:
            return False
    return True


if __name__ == "__main__":
    tela()
