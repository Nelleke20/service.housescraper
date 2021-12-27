import bs4, requests, smtplib,re, json
from selenium import webdriver
import numpy as np
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import time
from selenium.webdriver.common.action_chains import ActionChains
from pathlib import Path
import logging
import configparser

config = configparser.ConfigParser()
config.read('settings.yaml')
config.read('.secrets.yaml')

def web_scraping_fase_and_inlog():
    
    #check is phase 2 is available by selecting all phases available in the preparation phase
    chrome_options = Options()
    chrome_options.add_argument("--headless")          
    url = config['default']['url_1']
    browser = webdriver.Chrome(options=chrome_options)    
    browser.get(url)
    html = browser.page_source
    woning_soup = bs4.BeautifulSoup(html, 'lxml')
    fase_2 = woning_soup.find_all('span',attrs={'class':'property-card__project'})
    
    ResultText = []
    output = []
    for i in fase_2:
        output.append(re.findall(r"\>(.*)\<", str(i), flags=0))
    output_flat = [item for sublist in output for item in sublist]

    output = []
    for i in fase_2:
        output.append(re.findall(r"\>(.*)\<", str(i), flags=0))
    output_flat = [item for sublist in output for item in sublist]
    
    logging.basicConfig(level=logging.INFO)
    logging.info('The following phases are in the outputset: {}'.format(output_flat))

    # Define settings for running the rest of the sign-up script
    fase_check = config['default']['fase_check']     
    usernames = [config['default']['user_1']]      #, config['default']['user_2'], config['default']['user_3'], config['default']['user_4']
    chatbot_id = config['default']['chatbot_id']   
    chatbot_key = config['default']['chatbot_key']   
    chatbot_id2 = config['default']['chatbot_id2'] 
    chatbot_key2 = config['default']['chatbot_key2'] 

    logging.info('The following users are in the userset: {}'.format(usernames))
    logging.info('The following fase is being checked: {}'.format(fase_check))

    if  fase_check in set(output_flat):
        logging.info('Running the applicationform script..')

        #signing in for new project, per user
        for user in usernames:

            #send output to telegram bot
            resulttext = []
            resulttext.append(set(output_flat))
            resulttext.append('is also available in the totalset, check it out online!')
            requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id, chatbot_key, config[user]['telegram_id'], resulttext))

            #defining housenumbers
            housenumbers = [config[user]["housenumber1"], config[user]["housenumber2"]]

            #running script per new housenumber      
            for housenumber in housenumbers:

                #check if already signed in
                screenshot_name = "./screenshot/{}_screenshot_signup{}.png".format(user,housenumber)
                screenshot_confirmation = Path(screenshot_name)
                if screenshot_confirmation.is_file():
                    logging.info('For the combination of {} and {}, a file already exists, so will skip this run.'.format(user, housenumber))                   
                    continue
                                
                #if not, sign in to webpage
                else:
                    #send start info to telegram
                    output_combinatie = 'The following combination is filled out {}, {}'.format(user, housenumber)
                    requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id, chatbot_key, config[user]['telegram_id'], output_combinatie))

                    #options for the chromedriver
                    chrome_options2 = Options()
                    chrome_options2.add_argument("--window-size=1920,1080")
                    chrome_options2.add_argument("--disable-extensions")
                    chrome_options2.add_argument("--proxy-server='direct://'")
                    chrome_options2.add_argument("--proxy-bypass-list=*")
                    chrome_options2.add_argument("--start-maximized")
                    chrome_options2.add_argument('--headless')
                    chrome_options2.add_argument('--disable-gpu')
                    chrome_options2.add_argument('--disable-dev-shm-usage')
                    chrome_options2.add_argument('--no-sandbox')
                    chrome_options2.add_argument('--ignore-certificate-errors')
                    url2 = "https://www.nieuwbouwinhouten.nl/woningen//tussenwoning-herenhuis-woningtype-a077R00001JFZFIQA5/bouwnummer-{}".format(housenumber)                 
                    browser2 = webdriver.Chrome(chrome_options=chrome_options2)            
                    browser2.get(url2)
                    browser2.implicitly_wait(10)

                    #accept cookies
                    python_button1 = browser2.find_element_by_xpath('/html/body/bpd-cookies/div/div/div/div/button')
                    logging.info('Button 1 is clicked - accepting cookies on the website for the combination {}, {}.'.format(user, housenumber))
                    python_button1.click()
           
                    #click on projectfase button
                    action = ActionChains(browser2)
                    browser2.execute_script("window.scrollTo(0, 750)") 
                    time.sleep(3)
                    python_button2 = browser2.find_element_by_xpath("/html/body/main/section[1]/div/div/div[1]/div[2]/div[1]/button")
                    logging.info('Button 2 is clicked - click on the sign-up button for the combination {}, {}.'.format(user, housenumber))
                    action.move_to_element(python_button2).click().perform()

                    #select keys from the  application form - first step
                    username = browser2.find_element_by_id("lead-form-firstname")
                    lastname = browser2.find_element_by_id("lead-form-lastname")
                    emailadres = browser2.find_element_by_id("lead-form-email")
                    phone = browser2.find_element_by_id("lead-form-phone")
                    postalcode = browser2.find_element_by_id("lead-form-postalcode")
                    housnr = browser2.find_element_by_id("lead-form-housenumber")

                    #send keys form the application form - first step
                    username.send_keys(config[user]["username"])
                    lastname.send_keys(config[user]["lastname"])
                    emailadres.send_keys(config[user]["emailadres"])
                    phone.send_keys(config[user]["phone"])
                    postalcode.send_keys(config[user]["postalcode"])
                    housnr.send_keys(config[user]["housnr"])
                    time.sleep(5)

                    #select keys from the  application form - second step
                    streetname = browser2.find_element_by_id("lead-form-streetname")
                    place = browser2.find_element_by_id("lead-form-place")

                    #send keys form the application form - second 
                    time.sleep(3)
                    logging.info('Sending the keys in the sign-up form for the combination {}, {}.'.format(user, housenumber))
                    streetname.send_keys(config[user]["streetname"])
                    place.send_keys(config[user]["place"])
                    screenshot_name = "./screenshot/{}_screenshot_signup{}.png".format(user,housenumber)
                    browser2.save_screenshot(screenshot_name)
                    time.sleep(5)

                    # time.sleep(5)
                    requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id, chatbot_key, config[user]['telegram_id'], 'Answers part one and two are sent.'))                    

                    #send  application form
                    python_button3 = browser2.find_element_by_xpath("/html/body/lead-form/bpd-modal/div/div/bpd-pages/div[1]/bpd-form/form/div[1]/div[14]/button")
                    logging.info('Button 3 is clicked - sending the applicationform for the combination {}, {}.'.format(user, housenumber))
                    action.move_to_element(python_button3).click().perform()
                    time.sleep(5)
                    requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id, chatbot_key, config[user]['telegram_id'], 'The total applicationform is sent.'))                    
                    screenshot_confirmation = "./screenshot/{}_screenshot_confirmation{}.png".format(user,housenumber)
                    browser2.save_screenshot(screenshot_confirmation)
                    time.sleep(5)            

    else:
        resulttext = []
        resulttext.append([set(output_flat), 'is only available in the set.'])

        #send output to my telegram bot
        requests.get("https://api.telegram.org/{}:{}/sendMessage?chat_id={}&text={}".format(chatbot_id2, chatbot_key2, config['nelleke']['telegram_id'], resulttext))                    
                 
    browser.quit()

if __name__ == "__main__":
    web_scraping_fase_and_inlog()

