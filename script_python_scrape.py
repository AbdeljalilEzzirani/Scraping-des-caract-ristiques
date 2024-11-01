from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

path = '/usr/local/bin/chromedriver'
chrome_service = Service(path)
driver = webdriver.Chrome(service=chrome_service)

data = []

def boucle_to_pages(num_pages=2):
    base_url = 'https://www.avito.ma/fr/maroc/appartements'
    for page in range(1, num_pages + 1):
        url_page = f"{base_url}?o={page}"
        print(f"Scraping page {page}: {url_page}")
        page_data = go_to_scrap(url_page)
        traitement(page_data)
    print("Data processing completed.")

def go_to_scrap(url):
    driver.get(url)
    time.sleep(3)
    links = []

    retries = 3
    for attempt in range(retries):
        try:
            link_elements = driver.find_elements(By.XPATH, "//a[@class='sc-1jge648-0 eTbzNs']")
            links = [link.get_attribute('href') for link in link_elements]
            if links:
                break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            time.sleep(2)
            continue

    for link in links:
        driver.get(link)
        try:
            Titre = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//h1[@class="sc-1g3sn3w-12 jUtCZM"]'))
            ).text
            Localisation = driver.find_element(By.XPATH, "//span[@class='sc-1x0vz2r-0 iotEHk']").text
            Price = driver.find_element(By.XPATH, "//div[@class='sc-1g3sn3w-10 leGvyq']").text.replace("\u202f", " ")

            Nbr_Chambres = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div/div[3]/div[1]/div[2]/div[1]/div[1]/div[2]/div[4]/div[1]/div[1]/div').text if driver.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div/div[3]/div[1]/div[2]/div[1]/div[1]/div[2]/div[4]/div[1]/div[1]/div') else 'Nan'
            Nbr_Salle_de_bain = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div/div[3]/div[1]/div[2]/div[1]/div[1]/div[2]/div[4]/div[1]/div[2]/div/span').text if driver.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div/div[3]/div[1]/div[2]/div[1]/div[1]/div[2]/div[4]/div[1]/div[2]/div/span') else 'Nan'
            Surface_Total = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div/div[3]/div[1]/div[2]/div[1]/div[1]/div[2]/div[4]/div[1]/div[3]/div/span').text if driver.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div/div[3]/div[1]/div[2]/div[1]/div[1]/div[2]/div[4]/div[1]/div[3]/div/span') else 'Nan'
            all_info = driver.find_element(By.XPATH, '//div[@class="sc-qmn92k-0 cjptpz"]').text

            data.append({
                "Titre": Titre,
                "Price": Price,
                "Localisation": Localisation,
                "Nbr_Chambres": Nbr_Chambres,
                "Nbr_Salle_de_bain": Nbr_Salle_de_bain,
                "Surface_Total": Surface_Total,
                "all_info": all_info
            })
        except Exception as e:
            print("Error: Some details could not be scraped for this listing.")
            print(e)
    return data

def traitement(liste):
    rows = []
    for items in liste:
        info = items['all_info'].split('\n')
        row = {
            'Titre': items['Titre'],
            'Price': items['Price'],
            'Localisation': items['Localisation'],
            'chambre': items['Nbr_Chambres'],
            'bain': items['Nbr_Salle_de_bain'],
            'surface': items['Surface_Total']
        }
        info_dict = {}
        for i in range(0, len(info), 2):
            key = info[i].strip()
            value = info[i + 1].strip() if i + 1 < len(info) else ''
            info_dict[key] = value

        row['type'] = info_dict.get('Type', 'N/A')
        row['secteur'] = info_dict.get('Secteur', 'N/A')
        row['syndic'] = info_dict.get('Frais de syndic / mois', 'N/A')
        row['salon'] = info_dict.get('Salons', 'N/A')
        row['surface_habitable'] = info_dict.get('Surface habitable', 'N/A')
        row['Âge du bien'] = info_dict.get('Âge du bien', 'N/A')
        row['Étage'] = info_dict.get('Étage', 'N/A')

        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv('donnees_extraites.csv', index=False)
    print("Data saved to data.csv")
    return df

boucle_to_pages(num_pages=2)


