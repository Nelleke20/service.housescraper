from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from pathlib import Path
import logging
import configparser
import utils


def sign_in_new_phase(config, phase_output, housenumbers,
                      chatbot_id, chatbot_key, user):

    # send output to telegram bot
    resulttext = []
    resulttext.append(set(phase_output))
    resulttext.append('is also available in the totalset, check it out online. If not done yet, you will now be signed in.')        # noqa: E501
    requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id,                                 # noqa: E501
                                                                                        chatbot_key,                                # noqa: E501
                                                                                        config[user]['telegram_id'],                # noqa: E501
                                                                                        resulttext))                                # noqa: E501

    # running script per new housenumber
    for housenumber in housenumbers:

        # if already signed in, stop the proces otherwise start
        screenshot_name = "./screenshot/{}_screenshot_signup{}.png".format(user, housenumber)                                       # noqa: E501
        screenshot_confirmation = Path(screenshot_name)
        if screenshot_confirmation.is_file():           
            logging.info('For the combination of {} and {}, a file already exists, so will skip this run.'.format(user,             # noqa: E501
                                                                                                                  housenumber))     # noqa: E501
            continue
        else:                                           
            output_combinatie = 'The following combination is filled out {}, {}'.format(user,                                       # noqa: E501
                                                                                        housenumber)                                # noqa: E501
            requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id,                         # noqa: E501
                                                                                                chatbot_key,                        # noqa: E501
                                                                                                config[user]['telegram_id'],        # noqa: E501
                                                                                                output_combinatie))                 # noqa: E501
            # options for the chromedriver
            chrome_options = utils.set_default_chrome_options()

            # get browser
            url = "https://www.nieuwbouwinhouten.nl/woningen/tussenwoning-herenhuis-woningtype-a077R00001JFZFIQA5/bouwnummer-{}".format(housenumber)    # noqa: E501
            browser = webdriver.Chrome(options=chrome_options)
            browser.get(url)
            browser.implicitly_wait(10)

            # accept cookies
            utils.cookie_accepter(browser)
            time.sleep(1)

            # click on projectfase button
            action = utils.get_action(browser)
            utils.find_project_website(browser, action, user, housenumber)

            # select and send keys from the  application form - first step
            utils.find_elements_and_send_keys(browser, config, user)
            time.sleep(5)

            # select keys from the  application form - second step
            streetname, place = utils.extract_relevant_elements(browser)
            time.sleep(3)

            # send keys form the application form - second
            utils.send_keys_for_application_form(config, user, housenumber, place, streetname, browser)
            time.sleep(5)
            requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id,                         # noqa: E501
                                                                                                chatbot_key,                        # noqa: E501
                                                                                                config[user]['telegram_id'],        # noqa: E501
                                                                                                'Answers are sent.'))               # noqa: E501   
            # send application form
            utils.send_application_form(user, housenumber, browser, action)
            time.sleep(5)
            requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id,                         # noqa: E501
                                                                                                chatbot_key,                        # noqa: E501
                                                                                                config[user]['telegram_id'],        # noqa: E501
                                                                                                'The applicationform is sent.'))    # noqa: E501
            screenshot_confirmation = "./screenshot/{}_screenshot_confirmation{}.png".format(user,                                  # noqa: E501
                                                                                             housenumber)                           # noqa: E501
            browser.save_screenshot(screenshot_confirmation)
            browser.quit()


def check_phase_and_sing_up(config):

    # check if new phases are available
    phase_output = utils.check_phase_status(config)
    usernames, chatbot_id, chatbot_key, chatbot_id2, chatbot_key2, phase_check = utils.extract_settings(config)
    logging.info('The following users are in the userset: {}'.format(usernames))                                                    # noqa: E501

   # if new phase is availble sign-up for each user for different housenumbers
    if phase_check in set(phase_output):    
        logging.info('Running the applicationform sign-up script..')

        # if so, sign in to new phase
        for user in usernames:
            housenumbers = [config[user]["housenumber1"], config[user]["housenumber2"]]                                             # noqa: E501
            sign_in_new_phase(config, phase_output, housenumbers,
                              chatbot_id, chatbot_key, usernames)        
    else:
        # if not, send message to telegram bot
        resulttext = []
        resulttext.append([set(phase_output), 'is only available in the set.'])
        requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id2,                            # noqa: E501
                                                                                            chatbot_key2,                           # noqa: E501
                                                                                            config['nelleke']['telegram_id'],       # noqa: E501
                                                                                            resulttext))         

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('settings.yaml')                # include input from settings
    config.read('.secrets.yaml')                # include input from secrets
    logging.basicConfig(level=logging.INFO)     # setup logging

    # run script
    check_phase_and_sing_up(config)