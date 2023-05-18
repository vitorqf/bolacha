import json
import os
import random
from datetime import date, datetime

import pywhatkit
import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables
load_dotenv()

# Starts the scheduler
scheduler = BlockingScheduler()

# Twitter API credentials
api = tweepy.Client(
    consumer_key=f"{os.getenv('consumer_key')}",
    consumer_secret=f"{os.getenv('consumer_secret')}",
    access_token=f"{os.getenv('access_token')}",
    access_token_secret=f"{os.getenv('access_token_secret')}",
    bearer_token=f"{os.getenv('bearer_token')}",
)

# Constant variables
config = {
    "base_url": "https://twitter.com/merendaifrnpdf",
    "keywords": ["bolacha", "Bolacha", "BOLACHA", "Biscoito", "biscoito", "BISCOITO"],
}

# Random words
bad_words = [
    "Puxa vida",
    "Carambolas",
    "Caraca",
    "Cacetada",
    "Diacho",
    "Droga",
    "Argh",
    "Ah não omi",
    "Maizome",
]
good_words = [
    "Oooopa",
    "Aeee",
    "Vamoooo",
    "Aleluia",
    "Massaaa",
    "Dale",
    "Caneta azul, azul caneta",
    "Bom demaize",
]

# Selenium options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("window-size=1920x1080")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
# options.add_experimental_option("detach", True)

# Selenium driver
driver = webdriver.Chrome(service=Service("./driver/chromedriver.exe"), options=options)

print(driver)

f = open("log.txt", "w")

"""
    Steps:
    1. Inicia o driver do Selenium
    2. Acessa a página da merenda do Twitter
    3. Pega o último tweet e clica nele
    4. Então, espera 5 segundos para a página carregar
    5. Pega o texto do tweet
    6. Verifica se o tweet é de hoje:
    6.1 Se for, verifica se o tweet contém alguma das palavras-chave
    6.1.1 Se sim, retorna True
    6.1.2 Se não, retorna False
    6.2 Se não for, retorna None
    7. Se o tweet for True, cria uma mensagem com uma palavra boa aleatória
    8. Se o tweet for False, cria uma mensagem com uma palavra ruim aleatória
    9. Se o tweet for None, não faz nada
    10. Verifica se a última data do tweet é diferente da última data salva no JSON
    10.1 Se for, cria uma mensagem com o link do tweet e a mensagem criada anteriormente
    10.2 Se não for, não faz nada
    11. Envia a mensagem no WhatsApp
    12. Envia o tweet pela API do Twitter
    13. Salva a última data do tweet no JSON
"""


def shutdown_PC():
    os.system("shutdown /s /t 30")
    f.write(
        f"{datetime.now().strftime('[%H:%M:%S]')} - Desligando o PC em 10 segundos...\n"
    )
    print(
        f"{datetime.now().strftime('[%H:%M:%S]')} - Desligando o PC em 10 segundos..."
    )


def get_latest_tweet(base_url):
    f.write(f"{datetime.now().strftime('[%H:%M:%S]')} - Acessando o Twitter...\n")
    print(f"{datetime.now().strftime('[%H:%M:%S]')} - Acessando o Twitter...")

    # Access the Twitter page
    driver.get(base_url)

    # Wait for the page to load
    driver.implicitly_wait(5)

    try:
        notification_button = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]",
        )

        if notification_button:
            f.write(
                f"{datetime.now().strftime('[%H:%M:%S]')} - Fechei o pop-up de notificação...\n"
            )
            print(
                f"{datetime.now().strftime('[%H:%M:%S]')} - Fechei o pop-up de notificação..."
            )
            notification_button.click()

    except:
        pass

    driver.implicitly_wait(5)

    # Get the latest tweet
    latest_tweet = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/section/div/div/div[1]/div/div/article/div/div/div[2]/div[2]/div[2]/div/span",
    )

    if latest_tweet and datetime.now().strftime("%d/%m/%y") in latest_tweet.text:
        f.write(
            f"{datetime.now().strftime('[%H:%M:%S]')} - Encontrei o último Tweet...\n"
        )
        print(f"{datetime.now().strftime('[%H:%M:%S]')} - Encontrei o último Tweet...")

        # Enter the latest tweet
        latest_tweet.click()

        # Wait for the page to load
        driver.implicitly_wait(5)

        f.write(
            f"{datetime.now().strftime('[%H:%M:%S]')} - Acabei de entrar no último Tweet...\n"
        )
        print(
            f"{datetime.now().strftime('[%H:%M:%S]')} - Acabei de entrar no último Tweet..."
        )

        # Get the tweet text
        tweet_text = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[1]/div/div/span",
        ).text

        # Check if tweet_text is not empty
        if tweet_text:
            f.write(
                f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui encontrar o texto do Tweet acessado...\n"
            )
            print(
                f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui encontrar o texto do Tweet acessado..."
            )

            # Check if the tweet contains any of the keywords
            for keyword in config["keywords"]:
                if keyword in tweet_text:
                    f.write(
                        f"{datetime.now().strftime('[%H:%M:%S]')} - Encontrei a Palavra-chave...\n"
                    )
                    print(
                        f"{datetime.now().strftime('[%H:%M:%S]')} - Encontrei a Palavra-chave..."
                    )
                    return True

                else:
                    f.write(
                        f"{datetime.now().strftime('[%H:%M:%S]')} - Não encontrei a Palavra-chave...\n"
                    )
                    print(
                        f"{datetime.now().strftime('[%H:%M:%S]')} - Não encontrei a Palavra-chave..."
                    )
                    return False

        else:
            f.write(
                f"{datetime.now().strftime('[%H:%M:%S]')} - Não consegui encontrar o texto no tweet...\n"
            )
            print(
                f"{datetime.now().strftime('[%H:%M:%S]')} - Não consegui encontrar o texto no tweet..."
            )
            return None


def new_tweet(message):
    f.write(f"{datetime.now().strftime('[%H:%M:%S]')} - Criando novo tweet...\n")
    print(f"{datetime.now().strftime('[%H:%M:%S]')} - Criando novo tweet...")

    # Create the tweet
    api.create_tweet(text=message)

    # Saves the last tweet date
    write_last_tweet_date()

    f.write(f"{datetime.now().strftime('[%H:%M:%S]')} - Tweet criado com sucesso!\n")
    print(f"{datetime.now().strftime('[%H:%M:%S]')} - Tweet criado com sucesso!")


def new_whatsapp_message(message):
    f.write(
        f"{datetime.now().strftime('[%H:%M:%S]')} - Criando nova mensagem no WhatsApp...\n"
    )
    print(
        f"{datetime.now().strftime('[%H:%M:%S]')} - Criando nova mensagem no WhatsApp..."
    )

    phone = f"{os.getenv('phone')}"

    # Send the tweet + custom message on WhatsApp
    pywhatkit.sendwhatmsg_instantly(
        phone_no=phone,
        message=message,
        wait_time=30,
        tab_close=True,
        close_time=10,
    )

    f.write(
        f"{datetime.now().strftime('[%H:%M:%S]')} - Mensagem enviada com sucesso para {phone}!\n"
    )
    print(
        f"{datetime.now().strftime('[%H:%M:%S]')} - Mensagem enviada com sucesso para {phone}!"
    )


def create_message(url, is_good):
    message = ""
    wpp_message = ""

    # If the tweet is good (doesn't have cookie on text), we choose a random good word and build the message
    if is_good:
        word = random.choice(good_words)
        message = f"{word}!\nHoje NÃO tem bolacha! 😃\n\n{url}\n🍪🍪🍪"
        wpp_message = f"*A merenda de hoje do IFRN PDF é bolacha?* 🤖\n*@hojeehbolacha no Twitter*\n\n{word}!\nHoje NÃO tem bolacha! 😃\n\n{url}\n🍪🍪🍪"

    # If not, we choose a random bad word and build the message
    else:
        word = random.choice(bad_words)
        message = f"{word}!\nHoje tem bolacha. 😔\n\n{url}\n🍪🍪🍪"
        wpp_message = f"*A merenda de hoje do IFRN PDF é bolacha?* 🤖\n*@hojeehbolacha no Twitter*\n\n{word}!\nHoje tem bolacha. 😔\n\n{url}\n🍪🍪🍪"

    return message, wpp_message


def check_last_tweet_date():
    # Opens last_tweet_date.json and gets the last tweet date
    with open("last_tweet_date.json", "r") as file:
        last_tweet_date = json.load(file).get("last_tweet_date")

    # If the last tweet date is the same as today, we return True
    if last_tweet_date == date.today().strftime("%d/%m/%y"):
        return True


def write_last_tweet_date():
    # Saves the last tweet date
    last_tweet_date = date.today().strftime("%d/%m/%y")

    with open("last_tweet_date.json", "w") as file:
        json.dump({"last_tweet_date": last_tweet_date}, file)


# Scheduler to run the script every 30 minutes
@scheduler.scheduled_job("interval", minutes=2)
def checker():
    f.write(f"{datetime.now().strftime('[%H:%M:%S]')} - Iniciando o script...\n")
    print(f"{datetime.now().strftime('[%H:%M:%S]')} - Iniciando o script...")

    # Check if the tweet was already posted today
    if check_last_tweet_date():
        f.write(
            f"{datetime.now().strftime('[%H:%M:%S]')} [ ! ] Tweet já postado hoje!\n"
        )
        print(f"{datetime.now().strftime('[%H:%M:%S]')} [ ! ] Tweet já postado hoje!")

    else:
        try:
            # Get the latest tweet on page
            result = get_latest_tweet(config["base_url"])

            # Get the url of the latest tweet
            tweet_url = driver.current_url

            """
                If result is True, we create a new tweet and send a new WhatsApp message with a good message
                If result is False, we create a new tweet and send a new WhatsApp message with a bad message
                If result is None, we print a message saying that the date was not found
            """
            if result is True:
                f.write(
                    f"{datetime.now().strftime('[%H:%M:%S]')} - Verifiquei que hoje é bolacha, iniciando os posts...\n"
                )
                print(
                    f"{datetime.now().strftime('[%H:%M:%S]')} - Verifiquei que hoje é bolacha, iniciando os posts..."
                )

                message, wpp_message = create_message(tweet_url, is_good=False)
                f.write(
                    f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui criar a mensagem para o Twitter e WhatsApp...\n"
                )
                print(
                    f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui criar a mensagem para o Twitter e WhatsApp..."
                )

                # new_tweet(message)
                # f.write(
                #     f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui criar o tweet...\n"
                # )
                # print(
                #     f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui criar o tweet..."
                # )

                new_whatsapp_message(wpp_message)
                f.write(
                    f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui criar a mensagem no WhatsApp...\n"
                )
                print(
                    f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui criar a mensagem no WhatsApp..."
                )

                shutdown_PC()

            elif result is False:
                f.write(
                    f"{datetime.now().strftime('[%H:%M:%S]')} - Verifiquei que hoje NÃO é bolacha, iniciando os posts...\n"
                )
                print(
                    f"{datetime.now().strftime('[%H:%M:%S]')} - Verifiquei que hoje NÃO é bolacha, iniciando os posts..."
                )

                message, wpp_message = create_message(tweet_url, is_good=True)
                f.write(
                    f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui criar a mensagem para o Twitter e WhatsApp...\n"
                )
                print(
                    f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui criar a mensagem para o Twitter e WhatsApp..."
                )

                # new_tweet(message)
                # f.write(
                #     f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui criar o tweet...\n"
                # )
                # print(
                #     f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui criar o tweet..."
                # )

                new_whatsapp_message(wpp_message)
                f.write(
                    f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui criar a mensagem no WhatsApp...\n"
                )
                print(
                    f"{datetime.now().strftime('[%H:%M:%S]')} - Consegui criar a mensagem no WhatsApp..."
                )

                shutdown_PC()

            elif result is None:
                f.write(
                    f"{datetime.now().strftime('[%H:%M:%S]')} [ ! ] Vi que o último Tweet não é de hoje!\n"
                )
                print(
                    f"{datetime.now().strftime('[%H:%M:%S]')} [ ! ] Vi que o último Tweet não é de hoje!"
                )

        except Exception as e:
            f.write(f"{datetime.now().strftime('[%H:%M:%S]')} [ ! ] Erro: {e}")
            print(f"{datetime.now().strftime('[%H:%M:%S]')} [ ! ] Erro: {e}")

    f.flush()
    os.fsync(f.fileno())


f.write(f"{datetime.now().strftime('[%H:%M:%S]')} - Executando...\n")
print(f"{datetime.now().strftime('[%H:%M:%S]')} - Executando...")

scheduler.start()
f.close()
