import json
import os
import random
from datetime import date

import pywhatkit
import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
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
    "browserless_token": f"{os.getenv('browserless_token')}",
    "browserless_endpoint": "https://chrome.browserless.io/webdriver",
    "keywords": ["bolacha", "Bolacha", "BOLACHA", "Biscoito", "biscoito", "BISCOITO"],
}

# Random words
bad_words = ["Puxa vida", "Carambolas", "Caraca", "Cacetada", "Diacho", "Droga", "Argh", "Ah não omi", "Maizome"]
good_words = ["Oooopa", "Aeee", "Vamoooo", "Aleluia", "Massaaa", "Dale", "Caneta azul, azul caneta", "Bom demaize"]

# Selenium options
options = Options()
options.add_argument("--headless")
options.add_argument("window-size=1920x1480")
options.add_argument("--no-sandbox")
options.add_argument("disable-dev-shm-usage")
# options.add_experimental_option("detach", True)

# Selenium driver
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

def get_latest_tweet(base_url):
    print("[ - ] Acessando o Twitter...")

    # Access the Twitter page
    driver.get(base_url)

    # Wait for the page to load
    driver.implicitly_wait(5)

    # Get the latest tweet
    latest_tweet = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/section/div/div/div[1]/div/div/article/div/div/div[2]/div[2]/div[2]/div/span",
    )

    # Enter the latest tweet
    latest_tweet.click()

    # Wait for the page to load
    driver.implicitly_wait(5)

    # Get the tweet text
    tweet_text = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[2]/div/div[1]/span[1]",
    ).text

    # We check if the tweet is from today, if not we return None
    if (date.today().strftime("%d/%m/%y")) in tweet_text:
        
        # If the tweet is from today, we check if it contains any of the keywords
        if any(keyword in tweet_text for keyword in config["keywords"]):
            return True

        else:
            return False

    else:
        return None

def new_tweet(message):
    print("[ - ] Criando novo tweet...")

    # Create the tweet
    api.create_tweet(text=message)

    # Saves the last tweet date
    write_last_tweet_date()

    print("[ + ] Tweet criado com sucesso!")

def new_whatsapp_message(message):
    print("[ - ] Criando nova mensagem no WhatsApp...")

    # Send the tweet + custom message on WhatsApp
    pywhatkit.sendwhatmsg_instantly(
        phone_no=f"{os.getenv('phone')}",
        message=message,
        wait_time=30,
        tab_close=True,
        close_time=10,
    )

    print("[ + ] Mensagem enviada com sucesso!")

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
@scheduler.scheduled_job("interval", minutes=30)
def checker():
    # Check if the tweet was already posted today
    if check_last_tweet_date():
        print(f"[ ! ] Tweet já postado hoje!")

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
            if result:
                message, wpp_message = create_message(tweet_url, is_good=False)
                new_tweet(message)
                new_whatsapp_message(wpp_message)

            elif result is False:
                message, wpp_message = create_message(tweet_url, is_good=True)
                new_tweet(message)
                new_whatsapp_message(wpp_message)

            elif result is None:
                print("[ ! ] Data não encontrada")

        except Exception as e:
            print(e)


os.system("clear")
print("[ * ] Executando...")
scheduler.start()
