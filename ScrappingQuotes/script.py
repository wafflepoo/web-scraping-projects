## Script Python pour extraire des citations d'un site web et les enregistrer dans un fichier JSON

##Accédez au site Quotes to Scrape : http://quotes.toscrape.com/
##Utilisez les bibliothèques requests et BeautifulSoup pour extraire les 10 premières citations
import requests
from bs4 import BeautifulSoup
import json


# URL du site de citations
URL = "http://quotes.toscrape.com/page/1/"


# Récupération du contenu HTML de la page
response = requests.get(URL)
if response.status_code != 200:
   print("Échec de la récupération de la page.")
   exit()


# Analyse du HTML avec BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Extraction des citations et auteurs
quotes = soup.find_all("span", class_="text")
authors = soup.find_all("small", class_="author")


# Liste pour stocker les citations
quotes_list = []


# Extraire les 10 premières citations avec leurs auteurs
for i in range(min(10, len(quotes))):
   quote_text = quotes[i].text.strip()
   author_name = authors[i].text.strip()
   formatted_quote = f'{quote_text} - {author_name}'
   print(formatted_quote)


   # Ajouter à la liste sous forme de dictionnaire
   quotes_list.append({"quote": quote_text, "author": author_name})


# Bonus : Enregistrer les citations dans un fichier JSON
with open("citations.json", "w", encoding="utf-8") as json_file:
   json.dump(quotes_list, json_file, ensure_ascii=False, indent=4)


print("Les citations ont été enregistrées dans citations.json")
