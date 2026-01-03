# Importation des bibliothèques nécessaires
import requests # Pour envoyer des requêtes HTTP et récupérer le contenu des pages web
from bs4 import BeautifulSoup # Pour analyser et extraire des données du code HTML
import pandas as pd # Pour manipuler et organiser les données sous forme de tableau# Définition de l'URL de la page contenant le classement de la Ligue 1
url = "https://www.footmercato.net/france/ligue-1/classement"
# Effectuer une requête HTTP GET pour récupérer le contenu de la page web
response = requests.get(url) # `requests.get(url)` envoie une requête au serveur et récupère la page
# La réponse contient le code HTML de la page, que nous allons analyser
# Analyser le HTML récupéré avec BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')
# `response.content` contient le code HTML brut
# `BeautifulSoup(..., 'html.parser')` permet de structurer ce HTML pour faciliter l'extraction des données
# Trouver la partie du code HTML qui contient le tableau de classement des équipes
table = soup.find('div', class_='rankingTable__tableScroll').find('table')
# `find('div', class_='rankingTable__tableScroll')` cherche la div contenant le tableau
# `find('table')` trouve ensuite le tableau HTML dans cette div
# Extraire toutes les lignes du tableau (balises <tr>)
rows = table.find_all('tr')[1:11] # On sélectionne uniquement les 10 premières équipes
# `find_all('tr')` récupère toutes les lignes du tableau (tr = table row)
# `[1:11]` permet d'ignorer la première ligne (les en-têtes du tableau) et de prendre les 10 premières équipes
# Créer une liste vide qui servira à stocker les données extraites du tableau
teams_data = []
# Boucle pour parcourir chaque ligne du tableau et extraire les informations importantes
for row in rows:
    columns = row.find_all('td') # `find_all('td')` récupère toutes les cellules d'une ligne (td = table data)
    # Extraire et nettoyer les données pour chaque colonne
    rank = columns[0].text.strip() # Rang (position dans le classement)
    team = columns[1].text.strip() # Nom de l'équipe
    points = columns[3].text.strip() # Nombre total de points
    wins = columns[6].text.strip() # Nombre de matchs gagnés
    losses = columns[8].text.strip() # Nombre de matchs perdus
    # Ajouter ces informations sous forme de liste dans la liste `teams_data`
    teams_data.append([rank, team, points, wins, losses])
    # Convertir la liste `teams_data` en un tableau structuré avec pandas
    df = pd.DataFrame(teams_data, columns=["Rang", "Équipe", "Points", "Victoires","Défaites"])
# `pd.DataFrame(...)` transforme nos données en un tableau (DataFrame) avec des colonnes bien définies
# Afficher le tableau dans la console
print(df)
# Enregistrer les résultats dans un fichier CSV pour les conserver et les réutiliser plus tard
df.to_csv('classement_ligue1.csv', index=False, encoding='utf-8')# `df.to_csv(...)` enregistre le tableau sous forme de fichier CSV (format compatible avec Excel)
# `index=False` empêche pandas d'ajouter une colonne d'index inutile
# `encoding='utf-8'` garantit que les caractères spéciaux (comme les accents) s'affichent correctement