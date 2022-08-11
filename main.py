import random
import time
import configparser
import urllib
from urllib import parse

import schedule as schedule
import undetected_chromedriver as uc
from pip._internal.configuration import Configuration
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

Configuration.holdBrowserOpen = True
from add_user_DB import UserDB, CheckUsersDB

# ==================== Take date in config ======================
config = configparser.ConfigParser()
config.read("config.ini")

email = config['Linkedin']['email']
psw = config['Linkedin']['psw']
# ================================================================


# ========== how many contacts you want to download today ========
download_users = 75


# ==================== Run parser in mobile emulation and take all users links only ======================
class ParsLink:
    count = 0
    count_restart = 0
    marker = None

    def run(self):
        try:
            mobile_emulation = {"deviceName": "Nexus 5"}
            options = Options()

            # ========================== Hide browser==========================================
            # options.add_argument("--headless")
            # options.add_argument("--disable-dev-shm-usage")
            # options.add_argument("--no-sandbox")
            # =================================================================================

            options.add_experimental_option("mobileEmulation", mobile_emulation)
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get(
                'https://www.linkedin.com/checkpoint/rm/sign-in-another-account?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
            time.sleep(2)
            username_fiel = driver.find_element(By.ID, 'username')
            username_fiel.send_keys(email)
            psw_field = driver.find_element(By.ID, 'password')
            psw_field.send_keys(psw)
            button = driver.find_element(By.CLASS_NAME, 'btn__primary--large')
            button.click()
            driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
            time.sleep(5)
            urls_user = []
            # Get scroll height
            last_height = driver.execute_script("return document.body.scrollHeight")
            count = 0
            while True:
                count += 1
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(3)

                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            html = driver.page_source
            urls = re.findall('/in/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', html)
            urls = [i for i in urls if urls.count(i) != 1]
            urls = list(set(urls))
            for u in urls:
                u = urllib.parse.unquote(u)
                if 'https://linkedin.com' + u not in urls_user and 'recent-activity' not in u:
                    urls_user.append('https://linkedin.com' + u)
            print(urls_user)
            driver.quit()
            db = CheckUsersDB()
            answer_db = db.check_user_link(urls_user)
            if answer_db:
                print(f'Parsing start')
                print('answer_db', answer_db)
                self.parser_user(answer_db)
            else:
                ParsLink.marker = False
                print('All users added!!!!!!!!!!!!!!!' + 'or disconnected link')
        except Exception as e:
            print(f'Error {e} *******************************************************')

    # ==================== Run web parser and take all contacts users ======================
    def parser_user(self, urls_user):

        ## ========================== Hide browser==========================================
        # options = uc.ChromeOptions()
        # options.headless = True
        # options.add_argument('--headless')
        # driver = uc.Chrome(options=options)
        ## =================================================================================
        driver = uc.Chrome()
        driver.get(
            'https://www.linkedin.com/checkpoint/rm/sign-in-another-account?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
        time.sleep(2)
        username_fiel = driver.find_element(By.ID, 'username')
        username_fiel.send_keys(email)
        psw_field = driver.find_element(By.ID, 'password')
        psw_field.send_keys(psw)
        button = driver.find_element(By.CLASS_NAME, 'btn__primary--large')
        button.click()
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
        time.sleep(3)

        for user in urls_user[:download_users]:
            ParsLink.count += 1
            try:
                contacts_user = {}
                test_list = ['first_name', 'last_name', 'company', 'position', 'url_linkedin', 'email', 'number_phone']
                driver.get(user + '/overlay/contact-info/')
                n = random.randint(60, 180)
                time.sleep(n)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                html = driver.page_source
                soup = BeautifulSoup(html, 'lxml')
                name = soup.find('h1', id='pv-contact-info').text.strip().split()
                contacts_user.setdefault('first_name', name[0].replace("'", ''))
                contacts_user.setdefault('last_name', name[1].replace("'", ''))
                contacts_user.setdefault('url_linkedin', user)
                found = soup.select('span[class=visually-hidden]')

                for i in range(len(found)):
                    if 'Опыт работы' == found[i].text or 'Experience' == found[i].text:
                        if 'мес.' in found[i + 2].text or 'г.' in found[i + 2].text or 'yr' in found[
                            i + 2].text or 'mos' in found[i + 2].text:
                            company = found[i + 1].text
                            position = found[i + 3].text
                            contacts_user.setdefault('company', company.split('·')[0].strip().replace("'", ''))
                            contacts_user.setdefault('position', position)
                        else:
                            company = found[i + 2].text
                            position = found[i + 1].text
                            contacts_user.setdefault('company', company.split('·')[0].strip().replace("'", ''))
                            contacts_user.setdefault('position', position)

                li_mark = ['ci-phone', 'ci-email']
                for i in li_mark:
                    a = soup.find('section', class_=i)
                    if a:
                        for j in a:
                            if i == 'ci-phone':
                                c = j.text.strip()
                                if '+' in c:
                                    number = c.split()
                                    contacts_user.setdefault('number_phone', number[0])
                            elif i == 'ci-email':
                                c = j.text.strip()
                                if '@' in c:
                                    contacts_user.setdefault('email', c)

                for i in test_list:
                    if i not in contacts_user:
                        contacts_user.setdefault(i, '-')

                # ==================== Insert contact date in BD and take response ================================
                db = UserDB()
                answer_db = db.create_connection(contacts_user)
                try:
                    if answer_db['user']:
                        print(f"User {contacts_user['first_name']} created +++++++++++++++")
                        print(ParsLink.count)
                    else:
                        print('Parsing end')
                except Exception as e:
                    print(f"Some problems {contacts_user['first_name']}, error {e} -----------------")

            except Exception as e:
                print(e, 'Disconnection, link not found! ----------------------')
                if e:
                    driver.quit()
                    a = ParsLink.count_restart
                    if a >= 2:
                        break
                        print('There is a suspicion that the account was temporarily disconnected. Check your account!!!')
                    else:
                        ParsLink.count_restart += 1
                        pr = ParsLink()
                        pr.run()


if __name__ == '__main__':
    pl = ParsLink()
    pl.run()


# ===================== Parser Scheduler ===========================

def repeat_pars():
    pl = ParsLink()
    pl.run()


schedule.every(1).day.at("6:30").do(repeat_pars)

while ParsLink.marker != False:
    schedule.run_pending()
    time.sleep(1)
    print('Contacts download completed')
