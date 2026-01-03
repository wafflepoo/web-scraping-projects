from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import csv
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode
import os
import logging
from dataclasses import dataclass, field, fields, asdict




# Création d'une instance personnalisée d'options pour Selenium
options = webdriver.ChromeOptions()




# Clé API personnelle que j'ai créée pour accéder au proxy ScrapeOps
API_KEY = "e28fe030-20d5-4fb3-9767-317ba76e0190"




# Configuration du logger pour afficher les messages d'information et d'erreur
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)








@dataclass
class SearchData:
  name: str
  link: str
  result_number: int
  page_number: int




  def __post_init__(self):
      self.check_string_fields()




  def check_string_fields(self):
      # Vérification et nettoyage des chaînes de caractères pour éviter les espaces inutiles
      for field in fields(self):
          if isinstance(getattr(self, field.name), str):
              if getattr(self, field.name) == '':
                  setattr(self, field.name, f"No {field.name}")
                  continue
              value = getattr(self, field.name)
              setattr(self, field.name, value.strip())








class DataPipeline:
  def __init__(self, csv_filename="", storage_queue_limit=50):
      self.names_seen = []  # Liste pour éviter les doublons
      self.storage_queue = []  # File d'attente des données avant écriture
      self.storage_queue_limit = storage_queue_limit  # Nombre limite d'éléments avant sauvegarde
      self.csv_filename = csv_filename  # Nom du fichier CSV
      self.csv_file_open = False




  def save_to_csv(self):
      # Sauvegarde des données dans un fichier CSV
      self.csv_file_open = True
      self.data_to_save = []
      self.data_to_save.extend(self.storage_queue)
      self.storage_queue.clear()
      if not self.data_to_save:
          return
      keys = [field.name for field in fields(self.data_to_save[0])]




      file_exists = os.path.isfile(self.csv_filename) and os.path.getsize(self.csv_filename) > 0
      with open(self.csv_filename, mode="a", newline="", encoding="UTF-8") as output_file:
          writer = csv.DictWriter(output_file, fieldnames=keys)
          if not file_exists:
              writer.writeheader()
          for item in self.data_to_save:
              writer.writerow(asdict(item))
      self.csv_file_open = False




  def is_duplicate(self, input_data):
      # Vérification si l'élément a déjà été ajouté pour éviter les doublons
      if input_data.name in self.names_seen:
          logger.warning(f"Duplicate item found: {input_data.name}. Item dropped")
          return True
      self.names_seen.append(input_data.name)
      return False




  def add_data(self, scraped_data):
      # Ajout des données après vérification des doublons
      if self.is_duplicate(scraped_data) == False:
          self.storage_queue.append(scraped_data)
          if len(self.storage_queue) >= self.storage_queue_limit and self.csv_file_open == False:
              self.save_to_csv()




  def close_pipeline(self):
      # Fermeture et sauvegarde des données restantes si nécessaire
      if self.csv_file_open:
          time.sleep(3)
      if len(self.storage_queue) > 0:
          self.save_to_csv()








def get_scrapeops_url(url):
  # Fonction qui génère une URL avec le proxy ScrapeOps en utilisant l'API que j'ai créée
  payload = {'api_key': API_KEY, 'url': url, 'country': 'us'}
  proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
  return proxy_url








# Fonction qui effectue une recherche Google et récupère les résultats


def search_page(query, page, location):
   driver = webdriver.Chrome(options=options)  # Démarrage du navigateur avec les options définies
   driver.get(get_scrapeops_url(f"https://www.google.com/search?q={query}&start={page * 10}"))  # Requête vers Google


   divs = driver.find_elements(By.CSS_SELECTOR,
                               "div > div > div > div > div > div > div > div > div > div > div > div > div > div")
   results = []
   index = 0  # Numérotation des résultats
   last_link = ""


   for div in divs:
       if index >= 5:  # Limite à 5 résultats par page
           break


       title = div.find_elements(By.CSS_SELECTOR, "h3")
       link = div.find_elements(By.CSS_SELECTOR, "a")
       if len(title) > 0 and len(link) > 0:
           site_info = {"title": title[0].text, "link": link[0].get_attribute("href"), "result_number": index,
                        "page": page}
           if site_info["link"] != last_link:
               results.append(site_info)
               index += 1
               last_link = site_info["link"]
   driver.quit()
   # Affichage des résultats dans la sortie du code
   for res in results:
       print(f"Page {res['page'] + 1} - Result {res['result_number'] + 1}: {res['title']} ({res['link']})")




   return results






# Fonction pour rechercher plusieurs pages en parallèle
def full_search(query, pages=2, location="United States"):
  full_results = []
  page_numbers = list(range(0, pages))




  with ThreadPoolExecutor(max_workers=5) as executor:
      future_results = executor.map(search_page, [query] * pages, page_numbers, [location] * pages)
      for page_result in future_results:
          full_results.extend(page_result)
  return full_results








if __name__ == "__main__":
  logger.info("Starting scrape")
  data_pipeline = DataPipeline(csv_filename="production-search.csv")




  # Recherche du terme "DeepSeek" sur Google
  search_results = full_search("Recette Ramadan")




  for result in search_results:
      search_data = SearchData(name=result["title"], link=result["link"], result_number=result["result_number"],
                               page_number=result["page"])
      data_pipeline.add_data(search_data)




  data_pipeline.close_pipeline()
  logger.info("Scrape Complete")




