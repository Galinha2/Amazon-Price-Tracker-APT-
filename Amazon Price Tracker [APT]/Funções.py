import requests
from bs4 import BeautifulSoup
from time import sleep
import xlsxwriter
import sys
import smtplib
from email.message import EmailMessage
import json

# Define um titulo
def titulo(nome):
    print('\033[36;4m_\033[m' * 63)
    print(f'\033[4;3;43m                   {nome}                    \033[m')

def ui_ES():  # UI Espanhola

    try:
        while True:  # REPETE O UI enquanto o programa continua ativo
            print('\033[7;3m [1]Add new Product - [2]View Price History - [3]Close Program \033[m')
            resposta = str(input('Type Your Option: '))

            if resposta.isalpha():  # Se a resposta for em letras.
                while resposta.isalpha():
                    resposta = str(input('That Option Does Not Exist. Type Your Option:'))

            numero_inteiro = int(resposta)

            if numero_inteiro != 1 and numero_inteiro != 2 and numero_inteiro != 3:
                resposta = str(input('That Option Does Not Exist. Type Your Option:'))
                numero_inteiro = int(resposta)

            if numero_inteiro == 3:
                titulo('    Closing The Program ')
                break

            if numero_inteiro == 1:
                titulo('     Add New Product    ')
                url = str(input('Type Your Product URL: '))
                timer = str(input('How many seconds would you like to update the page?: '))

                while timer.isalpha():
                    timer = int(input('How many seconds would you like to update the page?: '))

                segundos = int(timer)
                loja_ES(url, segundos)

            elif numero_inteiro == 2:

                available_files()

                load_data_file = str(input(f'Type the name of the file: '))

                loading_user_data(load_data_file)


    except (NameError, ValueError):
        print('\033[31mERRO NO PROGRAMA, POR FAVOR RENICIE!!!\033[m')

    except KeyboardInterrupt:
        print('\033[31mEntrada de dados interrompida pelo usuário.\033[m')

def loja_ES(site, segundos):
    url1 = site
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
                AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15'}

    data = {'produtos': [], 'precos': []}

    mail_alert_notify = str(
        input('Do you whant to recive an e-mail notifiction when the price Updates?[Y/N]: ')).upper().strip()

    if mail_alert_notify == 'Y':
        print()
        print(
            '\033[7;3mPLEASE NOTE:\033[m \033[36mOnce the program starts running we will send you a testing e-mail '
            'notification.\n'
            'Please check if you are receving any e-mail or is it going to any spam folder.\n'
            'Thank you!\033[m')

        user_mail = str(input('Type your e-mail adress: '))

    else:
        user_mail = None

    ask_for_Save = str(input('Would you like to save this entries?[Y/N]: ')).upper().strip()

    if ask_for_Save == 'Y':
        save_name = str(input('Type the save name: ')).lower().strip()
        name_previous_saved_programs(save_name)
        load_data(save_name, url1, mail_alert_notify, user_mail, segundos)

    while True:
        pagina = requests.get(url1, headers=headers)
        pagina.raise_for_status()
        soup1 = BeautifulSoup(pagina.content, 'html.parser')
        produto = soup1.findAll('span', class_='a-size-large product-title-word-break')
        preco = soup1.findAll('span', class_='a-offscreen')

        pensando()

        for games, prices in zip(produto, preco):
            print(f'The product: \033[32m{games.text.strip():<40}\033[m')
            print(f'With the price: \033[32m{prices.text.strip()}\033[m')

            if len(data['precos']) == 0 or prices.text.strip() != data['precos'][-1]:
                data['produtos'].append(games.text.strip())

                data['precos'].append(prices.text.strip())

                print('\033[3;42mPRICE CHANGE IMPORTED TO THE SYSTEM\033[m')

                if mail_alert_notify == 'Y':  # Endereço eletrónico enviado
                    print(f'\033[3;46mE-MAIL SENT TO: {user_mail}\033[m')
                    mail_msg = (f'Your product, {games.text.strip()}.\nGot a price change to {prices.text.strip()}\n'
                                f'\nClick the link of the product here: {url1}')
                    email_alert('Price Change', mail_msg, user_mail)

            write_to_excel(data)

        for ponto in range(segundos, -1, -1):  # Contagem regressiva de update.
            print(f'Time left to UPDATE: \033[34m{ponto}\033[m Seconds.', end='', flush=True)
            sleep(1)
            sys.stdout.write('\r')
            sys.stdout.flush()

        print()
        print('-' * 100)


def write_to_excel(data): #Cria ficheiro de excel com os dados do produto selecionado.
    excel = xlsxwriter.Workbook('AmazonPriceTracker.xlsx')
    sheet = excel.add_worksheet('Sheet1')  # Create the worksheet outside the loop

    sheet.write(0, 0, '#')
    sheet.write(0, 1, 'Produto')
    sheet.write(0, 2, 'Preço')

    for i, (prod, price) in enumerate(zip(data['produtos'], data['precos']), 1):
        sheet.write(i, 0, str(i))
        sheet.write(i, 1, prod)
        sheet.write(i, 2, price)

    excel.close()


def pensando():  # Contador de loading
    sleep(0.3)
    print('                  \033[36mLOADING THE INFORMATION', end=''), sleep(0.3)
    print('.', end=''), sleep(0.3)
    print('.', end=''), sleep(0.3)
    print('.\033[m'), sleep(0.3)


def email_alert(subject, body, to):  # Mensagem de alerta com alteração de preço

    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = 'amazonpricedropapt@gmail.com'
    msg['from'] = user
    password = 'vdxn zeyw sojh rlfo'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()

def name_previous_saved_programs(nome_ficheiro):
    with open('ALLfiles', 'a') as file:
        file.write(f'{nome_ficheiro} | ')

def available_files():
    ficheiro = 'ALLfiles'
    with open(ficheiro, 'r') as file:
        conteudoficheiro = file.read()
        print(f'\033[45m{conteudoficheiro}\033[m')

def load_data(nome_ficheiro, url, mail, user_mail, segundos):
    user_datas = {'url': url, 'mail': mail, 'user_mail': user_mail, 'segundos': segundos}

    with open(f'{nome_ficheiro}.json', 'w') as file:
        json.dump(user_datas, file)


def load_user_data(url, mail, my_user_mail, segundos):  # pré-carregamento de data do utilizador anteriormete processada

    global user_mail
    url1 = url
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
                AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15'}

    data = {'produtos': [], 'precos': []}

    mail_alert_notify = mail

    if mail_alert_notify == 'Y':
        print()
        print('\033[7;3mPLEASE NOTE:\033[m \033[36mOnce the program starts running we will send you a testing e-mail '
              'notification.\n'
              'Please check if you are receving any e-mail or is it going to any spam folder.\n'
              'Thank you!\033[m')

        user_mail = my_user_mail

    while True:
        pagina = requests.get(url1, headers=headers)
        pagina.raise_for_status()
        soup1 = BeautifulSoup(pagina.content, 'html.parser')
        produto = soup1.findAll('span', class_='a-size-large product-title-word-break')
        preco = soup1.findAll('span', class_='a-offscreen')

        pensando()

        for games, prices in zip(produto, preco):
            print(f'The product: \033[32m{games.text.strip():<40}\033[m')
            print(f'With the price: \033[32m{prices.text.strip()}\033[m')

            if len(data['precos']) == 0 or prices.text.strip() != data['precos'][-1]:
                data['produtos'].append(games.text.strip())

                data['precos'].append(prices.text.strip())

                print('\033[3;42mPRICE CHANGE IMPORTED TO THE SYSTEM\033[m')

                if mail_alert_notify == 'Y':  # Endereço eletrónico enviado
                    print(f'\033[3;46mE-MAIL SENT TO: {user_mail}\033[m')
                    mail_msg = (f'Your product, {games.text.strip()}.\nGot a price change to {prices.text.strip()}\n'
                                f'\nClick the link of the product here: {url1}')
                    email_alert('Price Change', mail_msg, user_mail)

                else:
                    continue

            write_to_excel(data)

        for ponto in range(segundos, -1, -1):  # Contagem regressiva de update.
            print(f'Time left to UPDATE: \033[34m{ponto}\033[m Seconds.', end='', flush=True)
            sleep(1)
            sys.stdout.write('\r')
            sys.stdout.flush()

        print()
        print('-' * 100)

def loading_user_data(load_data_file): #Carrega todos os dados guardados anteriormente em perfis.
    try:
        with open(f'{load_data_file}.json', 'r') as file:
            loaded_data = json.load(file)
            url = loaded_data['url']
            mail_alert_notify = loaded_data['mail']
            user_mail = loaded_data['user_mail']
            segundos = loaded_data['segundos']
            load_user_data(url, mail_alert_notify, user_mail, segundos)

    except FileNotFoundError:
        print(f'The file {load_data_file}.json was not found.')

    else:
        print('Continuing with new data...')
