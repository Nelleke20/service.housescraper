from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.action_chains import ActionChains
from pathlib import Path
import logging
import configparser


def check_phase_status(config):
    # check is phase 2 is available by selecting all phases
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    url = config['default']['url_1']
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(url)
    html = browser.page_source
    woning_soup = BeautifulSoup(html, 'lxml')
    fase_2 = woning_soup.find_all('span', attrs={
                                        'class': 'property-card__project'})
    output = []
    for i in fase_2:
        output.append(re.findall(r"\>(.*)\<", str(i), flags=0))
    output_flat = [item for sublist in output for item in sublist]
    logging.info('The following phases are in the outputset: {}'.format(output_flat))                                               # noqa: E501
    browser.quit()
    return output_flat


def sign_in_new_phase(config, phase_output,
                      housenumbers, chatbot_id,
                      chatbot_key):
    logging.info('The following users are in the userset: {}'.format(usernames))                                                    # noqa: E501
    logging.info('Running the applicationform sign-up script..')

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

        # check if already signed in
        screenshot_name = "./screenshot/{}_screenshot_signup{}.png".format(user, housenumber)                                       # noqa: E501
        screenshot_confirmation = Path(screenshot_name)
        if screenshot_confirmation.is_file():
            logging.info('For the combination of {} and {}, a file already exists, so will skip this run.'.format(user,             # noqa: E501
                                                                                                                  housenumber))     # noqa: E501
            continue

        # if not, sign in to webpage
        else:
            # send starting info to telegram
            output_combinatie = 'The following combination is filled out {}, {}'.format(user,                                       # noqa: E501
                                                                                        housenumber)                                # noqa: E501
            requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id,                         # noqa: E501
                                                                                                chatbot_key,                        # noqa: E501
                                                                                                config[user]['telegram_id'],        # noqa: E501
                                                                                                output_combinatie))                 # noqa: E501

            # options for the chromedriver
            chrome_options = Options()
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--proxy-server='direct://'")
            chrome_options.add_argument("--proxy-bypass-list=*")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--ignore-certificate-errors')
            url = "https://www.nieuwbouwinhouten.nl/woningen/tussenwoning-herenhuis-woningtype-a077R00001JFZFIQA5/bouwnummer-{}".format(housenumber)    # noqa: E501
            browser = webdriver.Chrome(chrome_options=chrome_options)
            browser.get(url)
            browser.implicitly_wait(10)

            # accept cookies
            python_button1 = browser.find_element_by_xpath(
                '/html/body/bpd-cookies/div/div/div/div/button')
            logging.info('Button 1 is clicked - accepting cookies for the combination {}, {}.'.format(user,                         # noqa: E501
                                                                                                      housenumber))                 # noqa: E501
            python_button1.click()

            # click on projectfase button
            action = ActionChains(browser)
            browser.execute_script("window.scrollTo(0, 750)")
            time.sleep(3)
            python_button2 = browser.find_element_by_xpath(
             "/html/body/main/section[1]/div/div/div[1]/div[2]/div[1]/button")
            logging.info('Button 2 is clicked - click on the sign-up button for the combination {}, {}.'.format(user,               # noqa: E501
                                                                                                                housenumber))       # noqa: E501
            action.move_to_element(python_button2).click().perform()

            # select and send keys from the  application form - first step
            browser.find_element_by_id("lead-form-firstname").send_keys(
                config[user]["username"])
            browser.find_element_by_id("lead-form-lastname").send_keys(
                [user]["lastname"])
            browser.find_element_by_id("lead-form-email").send_keys(
                config[user]["emailadres"])
            browser.find_element_by_id("lead-form-phone").send_keys(
                config[user]["phone"])
            browser.find_element_by_id("lead-form-postalcode").send_keys(
                config[user]["postalcode"])
            browser.find_element_by_id("lead-form-housenumber").send_keys(
                config[user]["housnr"])
            time.sleep(5)

            # select keys from the  application form - second step
            streetname = browser.find_element_by_id("lead-form-streetname")
            place = browser.find_element_by_id("lead-form-place")

            # send keys form the application form - second
            time.sleep(3)
            logging.info('Sending the keys in the sign-up form for the combination {}, {}.'.format(user,                            # noqa: E501
                                                                                                   housenumber))                    # noqa: E501
            streetname.send_keys(config[user]["streetname"])
            place.send_keys(config[user]["place"])
            screenshot_name = "./screenshot/{}_screenshot_signup{}.png".format(user,                                                # noqa: E501
                                                                               housenumber)                                         # noqa: E501
            browser.save_screenshot(screenshot_name)
            time.sleep(5)
            requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id,                         # noqa: E501
                                                                                                chatbot_key,                        # noqa: E501
                                                                                                config[user]['telegram_id'],        # noqa: E501
                                                                                                'Answers are sent.'))               # noqa: E501
            # send application form
            python_button3 = browser.find_element_by_xpath(
                "/html/body/lead-form/bpd-modal/div/div/bpd-pages/div[1]/bpd-form/form/div[1]/div[14]/button")                      # noqa: E501
            logging.info('Button 3 is clicked - sending the applicationform for the combination {}, {}.'.format(user,               # noqa: E501
                                                                                                                housenumber))       # noqa: E501
            action.move_to_element(python_button3).click().perform()
            time.sleep(5)
            requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id,                         # noqa: E501
                                                                                                chatbot_key,                        # noqa: E501
                                                                                                config[user]['telegram_id'],        # noqa: E501
                                                                                                'The applicationform is sent.'))    # noqa: E501
            screenshot_confirmation = "./screenshot/{}_screenshot_confirmation{}.png".format(user,                                  # noqa: E501
                                                                                             housenumber)                           # noqa: E501
            browser.save_screenshot(screenshot_confirmation)
            browser.quit()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('settings.yaml')                # include input from settings
    config.read('.secrets.yaml')                # include input from secrets
    logging.basicConfig(level=logging.INFO)     # setup logging

    # check if new phases are available
    phase_output = check_phase_status(config)

    # Define settings for running the sign-up script
    usernames = [config['default']['user_1'],
                 config['default']['user_2'],
                 config['default']['user_3'],
                 config['default']['user_4']]
    chatbot_id = config['default']['chatbot_id']
    chatbot_key = config['default']['chatbot_key']
    chatbot_id2 = config['default']['chatbot_id2']
    chatbot_key2 = config['default']['chatbot_key2']
    phase_check = config['default']['fase_check']

    # if new phase is availble sign-up for each user for different housenumbers
    if phase_check in set(phase_output):
        for user in usernames:
            housenumbers = [config[user]["housenumber1"],
                            config[user]["housenumber2"]]
            sign_in_new_phase(config, phase_output, housenumbers,
                              chatbot_id, chatbot_key)
    else:
        # send message to telegram bot
        resulttext = []
        resulttext.append([set(phase_output), 'is only available in the set.'])
        requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id2,                            # noqa: E501
                                                                                            chatbot_key2,                           # noqa: E501
                                                                                            config['nelleke']['telegram_id'],       # noqa: E501
                                                                                            resulttext))                            # noqa: E501
