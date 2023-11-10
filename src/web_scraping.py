import bs4
import requests
import re
import configparser
import utils

config = configparser.ConfigParser()
config.read("settings.yaml")
config.read(".secrets.yaml")


def web_scraping_hofpark():
    # Download page and setup BeatifulSoup
    url = config["default"]["url_2"]
    getPage = requests.get(url)
    getPage.raise_for_status()  # if error it will stop the program
    soup = bs4.BeautifulSoup(getPage.text, "html.parser")
    links = soup.find_all("p", attrs={"class": "u-body-normal"})

    # select latest article and define the old article for comparing
    last_article = str(links[0])
    old_article = config["default"]["old_article"]
    last_article = re.findall(r"\>(.*)\<", last_article, flags=0)
    old_article = re.findall(r"\>(.*)\<", old_article, flags=0)

    # define settings for each user and chatbot ids
    usernames = [
        config["default"]["user_1"],
        config["default"]["user_2"],
        config["default"]["user_3"],
    ]

    chatbot_id2 = config["default"]["chatbot_id2"]
    chatbot_key2 = config["default"]["chatbot_key2"]

    # run for-loop for each user
    for user in usernames:
        resulttext = []

        # check if new article exists and return, else return old article
        if last_article == old_article:
            # if so, sent message with no new information
            uitkomst_true = "Helaas er is (nog) geen update op de website...."
            artikel_true = f"""Het laatste artikel bevat
              de volgende tekst: {last_article}"""
            resulttext.append(uitkomst_true)
            resulttext.append(artikel_true)
            resulttext.append(url)
            if user == "nelleke":
                utils.request_sender(
                    chatbot_id2,
                    chatbot_key2,
                    config["nelleke"]["telegram_id"],
                    resulttext,
                )

        else:
            # if not, sent message with new information
            uitkomst_false = (
                "Yes, er is nieuws! Check the website voor het nieuws."  # noqa: E501
            )
            artikel_false = f"""Het laatste artikel bevat
            de volgende tekst: {last_article}"""
            resulttext.append(uitkomst_false)
            resulttext.append(artikel_false)
            resulttext.append(url)
            utils.request_sender(
                chatbot_id2,
                chatbot_key2,
                config[user]["telegram_id"],
                resulttext,  # noqa: E501
            )


if __name__ == "__main__":
    web_scraping_hofpark()
