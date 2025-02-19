from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import urllib.request
import os
from dotenv import load_dotenv
from logger import log_info, log_error

load_dotenv()

# налаштування браузеру

# 0 - запуск у звичайному режимі без докеру, 1 - запуск у докер контейнері
DOCKER_LAUNCH = 0

if DOCKER_LAUNCH:
    # налаштування для докер контейнеру
    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage") 
    chrome_options.add_argument("--disable-gpu") 
    chrome_options.add_argument("--remote-debugging-port=9222") 
    chrome_options.add_argument(f"--user-data-dir={os.getenv('chrome_user_data_dir', '/tmp/chrome-user-data')}")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    service = Service(executable_path=os.environ.get('docker_chromedriver_path'))

    driver = webdriver.Chrome(service=service, options=chrome_options)

else:
    service = Service(executable_path=os.environ.get('chromedriver_path'))

    driver = webdriver.Chrome(service=service)

class LinkedIn:
    login_page =  'https://www.linkedin.com/login/'
    XPATH_DICT = {'login_button': "//button[@type='submit']",
                  'profile_link': "//div[@class='share-box-feed-entry__top-bar']//a[1]",
                  'profile_picture': "(//div[@class='ph5 '])/descendant::button[1]",
                  'profile_picture_img': "(//div[@class='imgedit-profile-photo-frame-viewer__body'])/descendant::img[1]"}

    def __init__(self, username, password):
        '''Ініціалізація даних користувача'''
        self.username = username
        self.password = password


    def login(self):
        '''Функція призначена для авторизації користувача'''
        try:
            #відкриття сторінки
            driver.get(LinkedIn.login_page)
            driver.implicitly_wait(5)

            # отримання полів вводу електроної пошти та паролю
            username = driver.find_element(By.ID, 'username')
            password = driver.find_element(By.ID, 'password')

            #отримання кнопки авторизації
            login_button = driver.find_element(By.XPATH, LinkedIn.XPATH_DICT['login_button'])

            # введення даних до полів електроної пошти та паролю
            username.send_keys(self.username)
            password.send_keys(self.password)

            # натискання кнопки входу
            login_button.click()

            log_info(f'Етап авторизації для користувача [{self.username}] пройдено.')
        except Exception as e:
            log_error(f'Помилка на етапі авторизації користувача [{self.username}]: ', e)

    def go_to_profile_picture(self):
        '''Функція призначена для переходу до сторінки профілю користувача та відкриття аватару натисканням миші'''

        # очікування повної загрузки сторінки, поки не буде знайдено потрібні елементи
        wait = WebDriverWait(driver, 30)

        try:
            # пошук та відкриття сторінки профілю користувача
            profile_link = wait.until(EC.element_to_be_clickable((By.XPATH, LinkedIn.XPATH_DICT['profile_link'])))
            profile_link.click()

            # пошук та відкриття зображення профілю користувача
            profile_picture = driver.find_element(By.XPATH, LinkedIn.XPATH_DICT['profile_picture'])
            profile_picture.click()

            log_info(f'Профіль користувача [{self.username}] знайдено.')

        except Exception as e:
            log_error(f'Помилка на етапі пошуку сторінки користувача [{self.username}]: ', e)

    @staticmethod
    def download_pfp():
        '''Функція призначена для завантаження зображення профілю користувача'''
        try:
            # пошук та отримання атрибуту src у зображення профіля 
            profile_picture_img = driver.find_element(By.XPATH, LinkedIn.XPATH_DICT['profile_picture_img'])
            src = profile_picture_img.get_attribute('src')

            base_path = "images/pfp.png"

            # якщо файл pfp.png існує, буде створено файл pfp_1.png, pfp_2.png і т.д.
            if os.path.exists(base_path):
                counter = 1
                while os.path.exists(f"images/pfp_{counter}.png"):
                    counter += 1
                filename = f"images/pfp_{counter}.png"
            else:
                filename = base_path

            # завантаження зображення
            urllib.request.urlretrieve(src, filename)

            log_info(f'Зображення [{filename}] профілю завантажено успішно.')

            # закриття вікна
            driver.close()
        except:
            log_error('Помилка на етапі завантаження зображення профілю.')

if __name__ == '__main__':

    # отримання даних для входу з файлу середовища .env
    user = LinkedIn(os.environ.get("username"),
                    os.environ.get("password"))
                    
    if not user.username or not user.password:
        print("Не вказано логін або пароль у файлі .env")
        exit()

    user.login()
    user.go_to_profile_picture()
    user.download_pfp()