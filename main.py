import datetime
import os
import random
from datetime import date, datetime

import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
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

options = Options()
options.add_argument("--headless")
options.add_argument("window-size=1920x1480")
options.add_argument("--no-sandbox")
options.add_argument("disable-dev-shm-usage")
# options.add_experimental_option("detach", True)

capabilities = DesiredCapabilities.CHROME.copy()
capabilities["browserless:token"] = "b64d611d-e4e2-418d-8157-43d91809ca13"


driver = webdriver.Remote(
    command_executor="https://chrome.browserless.io/webdriver",
    options=options,
    desired_capabilities=capabilities,
)

base_url = "https://twitter.com/merendaifrnpdf"

keywords = ["bolacha", "Bolacha", "BOLACHA", "Biscoito", "biscoito", "BISCOITO"]
bad_word = [
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
good_word = [
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
]

scheduler = BlockingScheduler()


def get_latest_tweet(base_url):
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
        if any(keyword in latest_tweet.text for keyword in keywords):
            return True

        else:
            return False

    else:
        return None


def new_tweet(message):
    api.create_tweet(text=message)


def create_message(is_good):
    message = ""

    if is_good:
        word = random.choice(good_word)
        message = f"{word}!\nHoje NÃO tem bolacha! 😃\n\n🍪🍪🍪"

    else:
        word = random.choice(bad_word)
        message = f"{word}!\nHoje tem bolacha. 😔\n\n🍪🍪🍪"

    return message


tweeted_at = None


@scheduler.scheduled_job("interval", hours=1)
def checker():
    global tweeted_at

    # Check if the tweet was already posted today
    if tweeted_at == date.today().strftime("%d/%m/%y"):
        print(f"{datetime.now()} - Tweet já postado hoje!")

    else:
        try:
            if get_latest_tweet(base_url):
                # Case there's a tweet with the date and the keywords, it means there's no cookies, then create a bad message
                message = create_message(is_good=False)
                new_tweet(message)
                print(f"{date.today().strftime('%d/%m/%y')} - {message}")
                tweeted_at = date.today().strftime("%d/%m/%y")

            elif get_latest_tweet(base_url) is False:
                message = create_message(is_good=True)
                new_tweet(message)
                print(f"{date.today().strftime('%d/%m/%y')} - {message}")
                tweeted_at = date.today().strftime("%d/%m/%y")

            elif get_latest_tweet(base_url) is None:
                print("Data não encontrada")

        except Exception as e:
            print(e)


scheduler.start()
