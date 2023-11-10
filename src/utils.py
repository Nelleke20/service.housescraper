from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging


def check_phase_status(config):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    url = config["default"]["url_1"]
    browser = webdriver.Chrome(
        ChromeDriverManager().install(), options=chrome_options
    )  # noqa: E501
    browser.get(url)
    html = browser.page_source
    woning_soup = BeautifulSoup(html, "lxml")
    fase_2 = woning_soup.find_all(
        "span", attrs={"class": "property-card__project"}
    )  # noqa: E501
    output = []
    [output.append(re.findall(r"\>(.*)\<", str(i), flags=0)) for i in fase_2]
    output_flat = [
        item for sublist in output for item in sublist
    ]  # check all phases on the web           # noqa: E501
    logging.info(
        "The following phases are in the outputset: {}".format(output_flat)
    )  # noqa: E501
    browser.quit()
    return output_flat


def extract_settings(config):
    usernames = [config["default"]["user_1"]]
    chatbot_id = config["default"]["chatbot_id"]
    chatbot_key = config["default"]["chatbot_key"]
    phase_check = config["default"]["fase_check"]
    return usernames, chatbot_id, chatbot_key, phase_check


def default_request(chatbot_id, chatbot_key, user):
    chat_id = user
    return f"https://api.telegram.org/{chatbot_id}:{chatbot_key}/sendMessage?chat_id={chat_id}"  # noqa: E501


def request_sender(chatbot_id, chatbot_key, user, text):
    default = default_request(chatbot_id, chatbot_key, user)
    output = f"&text={text}"
    requests.get(default + output)


def cookie_accepter(browser, user, housenumber):
    python_button1 = browser.find_element(
        By.XPATH, "/html/body/bpd-cookies/div/div/div/div/button"
    )  # noqa: E501
    logging.info(
        """Button 1 is clicked -
        accepting cookies for
        the combination {user}, {housenumber}."""
    )
    python_button1.click()


def get_action(browser):
    return ActionChains(browser)


def find_project_website(browser, action, user, housenumber):
    browser.execute_script("window.scrollTo(0, 750)")
    time.sleep(3)
    python_button2 = browser.find_element(
        By.XPATH,
        "/html/body/main/section[1]/div/div/div[1]/div[2]/div[1]/button",  # noqa: E501
    )  # noqa: E501
    logging.info(
        f"""Button 2 is clicked -
        click on the sign-up button for
        he combination {user}, {housenumber}."""
    )
    action.move_to_element(python_button2).click().perform()


def find_elements_and_send_keys(browser, config, user):
    # select and send keys from the  application form - first step
    browser.find_element(By.ID, "lead-form-firstname").send_keys(
        config[user]["username"]
    )
    browser.find_element(By.ID, "lead-form-lastname").send_keys(
        config[user]["lastname"]
    )
    browser.find_element(By.ID, "lead-form-email").send_keys(
        config[user]["emailadres"]
    )  # noqa: E501
    browser.find_element(By.ID, "lead-form-phone").send_keys(
        config[user]["phone"]
    )  # noqa: E501
    browser.find_element(By.ID, "lead-form-postalcode").send_keys(
        config[user]["postalcode"]
    )
    browser.find_element(By.ID, "lead-form-housenumber").send_keys(
        config[user]["housnr"]
    )


def extract_relevant_elements(browser):
    # select keys from the  application form - second step
    streetname = browser.find_element(By.ID, "lead-form-streetname")
    place = browser.find_element(By.ID, "lead-form-place")
    return streetname, place


def send_keys_for_application_form(
    config, user, housenumber, place, streetname, browser
):
    logging.info(
        f"""Sending the keys in the sign-up form
        for the combination {user}, {housenumber}."""
    )  # noqa: E501
    streetname.send_keys(config[user]["streetname"])
    place.send_keys(config[user]["place"])
    screenshot_name = "./screenshot/{}_screenshot_signup{}.png".format(
        user, housenumber  # noqa: E501
    )  # noqa: E501
    browser.save_screenshot(screenshot_name)


def send_application_form(user, housenumber, browser, action):
    python_button3 = browser.find_element(
        By.XPATH,
        "/html/body/lead-form/bpd-modal/div/div/bpd-pages/div[1]/bpd-form/form/div[1]/div[14]/button",  # noqa: E501
    )  # noqa: E501
    logging.info(
        """Button 3 is clicked -
        sending the applicationform
        for the combination {user}, {housenumber}."""
    )  # noqa: E501
    action.move_to_element(python_button3).click().perform()


def set_default_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--ignore-certificate-errors")
    return chrome_options
