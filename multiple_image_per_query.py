import time
import base64
from io import BytesIO
import re
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from PIL import Image

cwd = os.getcwd()
IMAGE_FOLDER = 'download'
os.makedirs(
    name=f'{cwd}/{IMAGE_FOLDER}',
    exist_ok=True
)

# Set up option for Selenium's headless mode
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--headless") # Enable headless mode
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")


driver = webdriver.Edge(
    options=chrome_options
)

SLEEP_TIME = 1

def download_google_images(search_query: str, number_of_images: int) -> str:
    '''Download google images with this function\n
       Takes -> search_query, number_of_images\n
       Returns -> None
    '''

    def scroll_to_bottom():
        '''Scroll to the bottom of the page
        '''
        last_height = driver.execute_script('return document.body.scrollHeight')
        while True:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(SLEEP_TIME)

            new_height = driver.execute_script('return document.body.scrollHeight')
            try:
                element = driver.find_element(
                    by=By.CSS_SELECTOR,
                    value='.YstHxe input'
                )
                element.click()
                time.sleep(SLEEP_TIME)
            except:
                pass

            if new_height == last_height:
                break

            last_height = new_height

    url = 'https://images.google.com/'

    driver.get(
        url=url
    )

    box = driver.find_element(
        by=By.XPATH,
        value="//*[@name='q']"
    )

    box.send_keys(search_query)
    box.send_keys(Keys.ENTER)
    time.sleep(SLEEP_TIME)

    scroll_to_bottom()
    time.sleep(SLEEP_TIME)

    img_results = driver.find_elements(
        by=By.XPATH,
        value="//img[contains(@class,'rg_i Q4LuWd')]"
    )

    total_images = len(img_results)

    print(f'Total images - {total_images}')

    count = 0

    for img_result in img_results:
        try:
            WebDriverWait(
                driver,
                15
            ).until(
                EC.element_to_be_clickable(
                    img_result
                )
            )
            img_result.click()
            time.sleep(SLEEP_TIME)

            actual_imgs = driver.find_elements(
                by=By.XPATH,
                value="//img[contains(@class,'r48jcc pT0Scc iPVvYb')]"
            )

            if (len(actual_imgs) == 0):
                actual_imgs = driver.find_elements(
                    by=By.XPATH,
                    value="//img[contains(@class,'Tt9ew pT0Scc')]"
                )


            src = ''

            for actual_img in actual_imgs:
                if 'https://encrypted' in actual_img.get_attribute('src'):
                    pass
                elif 'http' in actual_img.get_attribute('src'):
                    src += actual_img.get_attribute('src')
                    break
                else:
                    pass

            for actual_img in actual_imgs:
                if src == '' and 'base' in actual_img.get_attribute('src'):
                    src += actual_img.get_attribute('src')

            os.makedirs(
                name=f'{cwd}/{IMAGE_FOLDER}/{search_query}/',
                exist_ok=True
            )

            image_name = search_query.replace('/', ' ')
            image_name = re.sub(pattern=" ", repl="_", string=image_name)
            file_path = f'{IMAGE_FOLDER}/{search_query}/{count}_{image_name}.jpeg'

            if 'https://' in src:
                try:
                    result = requests.get(src, allow_redirects=True, timeout=10)
                    open(file_path, 'wb').write(result.content)
                    img = Image.open(file_path)
                    img = img.convert('RGB')
                    img.save(file_path, 'JPEG')
                    print(f'Count - {count} - Image saved from https.')
                except:
                    print('Bad image.')
                    try:
                        os.unlink(file_path)
                    except:
                        pass
                    count -= 1
            else:
                img_data = src.split(',')
                try:
                    img = Image.open(BytesIO(base64.b64decode(img_data[1])))
                    img = img.convert('RGB')
                    img.save(file_path, 'JPEG')
                    print(f'Count - {count} - Image saved from Base64.')
                except:
                    print('Bad image.')
                    count -= 1
        except ElementClickInterceptedException as e:
            count -= 1
            print(e)
            print('Image is not clickable.')
            driver.quit()

        count += 1

        if count >= total_images:
            print('No more images to download.')
            break
        if count == number_of_images:
            break

tags = [
    'Elon Musk',
    'Tim Cook'
]

for tag in tags:
    print(f'{"="*10} Downloding for the tag - {tag} {"="*10}')
    download_google_images(
        tag,
        5
    )
    print(f'{"="*10} Finished downloding for the tag - {tag} {"="*10}')

driver.quit()