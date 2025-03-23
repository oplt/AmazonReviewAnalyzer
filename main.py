from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from dotenv import load_dotenv
import json
from datetime import datetime
import requests
import browser_cookie3

load_dotenv()

def get_domain_cokkies():
    domain = "amazon.com"
    cookies = browser_cookie3.chrome(domain_name=domain)

    cookies_list = []
    for cookie in cookies:
        cookies_list.append({
            "name": cookie.name,
            "value": cookie.value,
            "domain": cookie.domain,
            "path": cookie.path,
            "expires": cookie.expires,
            "secure": cookie.secure and True or False,
            "httponly": cookie.has_nonstandard_attr("HttpOnly"),
        })
    with open("cookies.json", "w") as f:
        json.dump(cookies_list, f, indent=4)

def login():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://www.amazon.com")
    time.sleep(3)

    with open("cookies.json", "r") as file:
        cookies = json.load(file)
        for cookie in cookies:
            # if "domain" not in cookie:
            #     cookie["domain"] = ".amazon.com"
            # if "sameSite" not in cookie or cookie["sameSite"] not in ["Strict", "Lax", "None"]:
            #     cookie["sameSite"] = "Lax"
            cookie.pop("expiry", None)
            driver.add_cookie(cookie)
    driver.refresh()
    return driver

def get_product_review_page(driver):
    product_url = "https://www.amazon.com/Razer-BlackShark-Wireless-Gaming-Headset/dp/B0BY1FXC9N/ref=sr_1_1_sspa?_encoding=UTF8&content-id=amzn1.sym.12129333-2117-4490-9c17-6d31baf0582a&dib=eyJ2IjoiMSJ9.WJZIGcfaxHH2NU1LngCUay4gxKxdbmUPMgelA_mwm_XGL9pR4S-S-TBVEZkGZfJa0l3txlPkvhGz1SBN97ZsnTw8YW4aoEwxxpGtcRpYKQS--xSIBrErV2pxrQblk-HDF6NAGvk1K8yYj_jcaju8DFuhWGap_N7s0wvYwFL7PS2hrilk_OVKwXz5IqnPWnewuh0eqYKXvGS0gkV3ABQPaafrmgCkJIiZ92kZsznVWlI.itmyxXEmxs14cxjdknCM5HuN2eFKT-jm9R2kMsr4ipI&dib_tag=se&keywords=gaming%2Bheadsets&pd_rd_r=28793254-7a79-4ceb-9082-d85e92c8d739&pd_rd_w=1NL0r&pd_rd_wg=zTBVB&qid=1742736001&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1"
    driver.get(product_url)
    reviews_link = driver.find_element(By.XPATH, "//a[contains(@href, '/product-reviews/')]")
    reviews_link.click()
    return driver

def scrape_reviews(driver):
    reviews = []
    while True:
        review_elements = driver.find_elements(By.XPATH, "//li[@data-hook='review']")
        for review in review_elements:
            text = review.find_element(By.XPATH, ".//span[@data-hook='review-body']").text
            rating_text = review.find_element(By.XPATH, ".//a[@data-hook='review-title']/i").get_attribute("textContent")
            rating = rating_text.split(" ")[0]
            date_raw = review.find_element(By.XPATH, ".//span[@data-hook='review-date']").text
            date_str = date_raw.replace("Reviewed in", "").split("on ")[-1]
            date_obj = datetime.strptime(date_str, "%B %d, %Y")
            date = date_obj.strftime("%d/%m/%Y")
            dict = {'date': date,
                    'text': text,
                    'rating': rating,
                    }
            reviews.append(dict)

        try:
            next_page_button = driver.find_element(By.XPATH, "//li[@class='a-last']/a[contains(text(), 'Next page')]")
            next_page_button.click()
            time.sleep(3)
        except:
            break

    reviews_df = pd.DataFrame(reviews)
    reviews_df.to_excel("reviews.xlsx", index=False)
    return reviews_df

def get_product_differentiation(reviews):
    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    MODEL_NAME = "deepseek-r1:8b"

    prompt = f"""Here is a pandas dataframe containging product reviews with dates:
    {reviews}
    Based on these reviews, only point out complaints and negative views and suggest ways to differentiate and improve this product for better sales and customer satisfaction."""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "max_tokens": 150,
        }
    }
    response = requests.post(OLLAMA_API_URL, json=payload)

    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("response", "").strip()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return "Failed to generate recommendations."

if __name__ == "__main__":
    get_domain_cokkies()
    time.sleep(3)

    driver_login = login()
    time.sleep(3)

    driver_review = get_product_review_page(driver_login)
    reviews = scrape_reviews(driver_review)
    recommendations = get_product_differentiation(reviews)
    print(recommendations)
    driver_review.quit()