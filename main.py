from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import time
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv
import os

# Função para enviar email avisando de falha de conexão ao site
def Send_Email(site, nome):

    print("Iniciando envio de email avisando falha de acesso a ", site, " ( ", datetime.now().strftime('%d/%m/%Y %H:%M'), " )")
    msg = MIMEMultipart()
    message = "Tentativa de acesso ao site " + site + " não foi realizada com sucesso"
    password = os.getenv("PASSWORD")
    msg['From'] = os.getenv("EMAIL_FROM")
    msg['To'] = os.getenv("EMAIL_TO")
    msg['Subject'] = "Alerta de queda de acesso ao site : " + nome
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    print("Envio de email avisando falha de acesso a ", site, " enviado! ( ", datetime.now().strftime('%d/%m/%Y %H:%M'), " )")

# Função para calcular a diferença em minutos entre dois datetimes
def Diff_Minutes(dt1, dt2):
    diff = dt2-dt1 
    return diff.total_seconds() / 60

# Procura variaveis de ambiente no arquivo .env
load_dotenv()

# Faz o download do driver do chrome caso não exista
s=Service(ChromeDriverManager().install())  

# Cria variavel para configurações do driver
options = webdriver.ChromeOptions()

# Modo oculto do chrome
options.add_argument("--headless")

# Cria o driver do chrome
driver = webdriver.Chrome(service=s, options=options)

# Aguarda ate 10 segundos para o driver ser criado
driver.implicitly_wait(10)

# Paginas de verificação
page1 = os.getenv("PAGE1")
page2 = os.getenv("PAGE2")

# Abre outra aba do chrome
driver.execute_script("window.open('');")

# Tempo de re-verificação
refresh_time = 60

print("")
print("Iniciando bot de verificação dos sites... ( ", datetime.now().strftime('%d/%m/%Y %H:%M'), " )")

dthr_ultimo_envio_email_page1 = datetime.now() - timedelta(days=1)
dthr_ultimo_envio_email_page2 = datetime.now() - timedelta(days=1)

# Verificação periodica dos sites
while True:

    print("")
    dthr_agora = datetime.now()

    try:
        driver.get(page1)
        div = driver.find_element(By.ID, "folder0")
        print("Pagina ", page1, " carregou ( ", datetime.now().strftime('%d/%m/%Y %H:%M'), " )")
        time.sleep(2)
    except:
        print("Pagina ", page1, " não carregou ( ", datetime.now().strftime('%d/%m/%Y %H:%M'), " )")
        
        # Se passou meia hora desde o ultimo envio de email, envia email avisando
        if(Diff_Minutes(dthr_ultimo_envio_email_page1, dthr_agora) > 30):
            print("Passou mais de meia hora desde que o ultimo email de aviso foi enviado, enviando novamente....")
            Send_Email(page1, 'IntegracaoND')
            dthr_ultimo_envio_email_page1 = datetime.now()
        else:
            print("Ainda não passou meia hora desde o ultimo envio de email...")

    driver.switch_to.window(driver.window_handles[1])
    time.sleep(2)

    try:
        driver.get(page2)
        div = driver.find_element(By.ID, "content")
        print("Pagina ", page2, " carregou ( ", datetime.now().strftime('%d/%m/%Y %H:%M'), " )")
        time.sleep(2)
    except:
        print("Pagina ", page2, " não carregou ( ", datetime.now().strftime('%d/%m/%Y %H:%M'), " )")

        if(Diff_Minutes(dthr_ultimo_envio_email_page2, dthr_agora) > 30):
            print("Passou mais de meia hora desde que o ultimo email de aviso foi enviado, enviando novamente....")
            Send_Email(page2, 'IntegracaoHRG')
            dthr_ultimo_envio_email_page2 = datetime.now()
        else:
            print("Ainda não passou meia hora desde o ultimo envio de email...")
   

    driver.switch_to.window(driver.window_handles[0])

    print("Aguardando ", refresh_time, " segundos para executar novamente a verificação... ( ", datetime.now().strftime('%d/%m/%Y %H:%M'), " )")
    time.sleep(refresh_time)

