import json
import os
import random
from datetime import date

import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()


# Twitter API credentials
api = tweepy.Client(
    consumer_key=f"{os.getenv('consumer_key')}",
    consumer_secret=f"{os.getenv('consumer_secret')}",
    access_token=f"{os.getenv('access_token')}",
    access_token_secret=f"{os.getenv('access_token_secret')}",
    bearer_token=f"{os.getenv('bearer_token')}",
)

config = {
    "base_url": "https://twitter.com/merendaifrnpdf",
    "browserless_token": f"{os.getenv('browserless_token')}",
    "browserless_endpoint": "https://chrome.browserless.io/webdriver",
    "keywords": ["bolacha", "Bolacha", "BOLACHA", "Biscoito", "biscoito", "BISCOITO"],
    "bad_word": [
        "Puxa vida",
        "Carambolas",
        "Caraca",
        "Cacetada",
        "Diacho",
        "Droga",
        "Argh",
        "Ah não omi",
        "Maizome",
    ],
    "good_word": [
        "Parabéns",
        "Viva",
        "Bravo",
        "Aleluia",
        "Uhu",
        "Eba",
        "Aplausos",
        "Que legal",
        "Excelente",
        "Sensacional",
        "Bom demaize",
    ],
}

options = Options()
options.add_argument("--headless")
options.add_argument("window-size=1920x1480")
options.add_argument("--no-sandbox")
options.add_argument("disable-dev-shm-usage")
# options.add_experimental_option("detach", True)

capabilities = DesiredCapabilities.CHROME.copy()
capabilities["browserless:token"] = config["browserless_token"]

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

scheduler = BlockingScheduler()


def get_latest_tweet(base_url):
    print("[ - ] Acessando o Twitter...")

    driver.get(base_url)

    driver.implicitly_wait(5)

    # Get the latest tweet
    latest_tweet = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/section/div/div/div[1]/div/div/article/div/div/div[2]/div[2]/div[2]/div/span",
    )

    # Check if there's a date in the tweet then checks if its today's date
    if (date.today().strftime("%d/%m/%y")) in latest_tweet.text:
        # Check if there's any of the keywords in the tweet
        if any(keyword in latest_tweet.text for keyword in config["keywords"]):
            return True

        else:
            return False

    else:
        return None


def new_tweet(message):
    print("[ - ] Criando novo tweet...")
    api.create_tweet(text=message)
    write_last_tweet_date()
    print("[ + ] Tweet criado com sucesso!")


def create_message(is_good):
    message = ""

    if is_good:
        word = random.choice(config["good_word"])
        message = f"{word}!\nHoje NÃO tem bolacha! 😃\n\n🍪🍪🍪"

    else:
        word = random.choice(config["bad_word"])
        message = f"{word}!\nHoje tem bolacha. 😔\n\n🍪🍪🍪"

    return message


def check_last_tweet_date():
    with open("last_tweet_date.json", "r") as file:
        last_tweet_date = json.load(file).get("last_tweet_date")

    if last_tweet_date == date.today().strftime("%d/%m/%y"):
        return True


def write_last_tweet_date():
    last_tweet_date = date.today().strftime("%d/%m/%y")

    with open("last_tweet_date.json", "w") as file:
        json.dump({"last_tweet_date": last_tweet_date}, file)


@scheduler.scheduled_job("interval", minutes=20)
def checker():
    # Check if the tweet was already posted today
    if check_last_tweet_date():
        print(f"[ ! ] Tweet já postado hoje!")

    else:
        try:
            result = get_latest_tweet(config["base_url"])

            if result:
                message = create_message(is_good=False)
                new_tweet(message)

            elif result is False:
                message = create_message(is_good=True)
                new_tweet(message)

            elif result is None:
                print("[ ! ] Data não encontrada")

        except Exception as e:
            print(e)


os.system("clear")
print("[ * ] Executando...")
scheduler.start()
