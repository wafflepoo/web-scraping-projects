# Importation des bibliothèques nécessaires
from selenium import webdriver  # Pour automatiser le navigateur
from selenium.webdriver.chrome.options import Options  # Configurer Chrome pour Selenium
from selenium.webdriver.common.by import By  # Pour sélectionner les éléments HTML avec Selenium
from bs4 import BeautifulSoup  # Pour parser le HTML et extraire les données
import time  # Pour attendre le chargement des pages dynamiques
import re  # Pour nettoyer les textes extraits
import json


# --- Configuration de Selenium ---
options = Options()
options.add_argument("--headless")  # Mode sans interface graphique pour exécuter plus rapidement
options.add_argument("--disable-blink-features=AutomationControlled")  # Empêche la détection comme bot
options.add_argument("--no-sandbox")  # Évite certains problèmes d'exécution dans des environnements sécurisés
options.add_argument("--disable-dev-shm-usage")  # Optimisation pour les systèmes avec peu de mémoire partagée
options.add_argument("--disable-infobars")  # Supprime les infobars Chrome "Selenium est en cours d’exécution"
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")  # Simule un navigateur réel


# ---  Lancement du navigateur Chrome via Selenium ---
driver = webdriver.Chrome(options=options)


# --- Chargement de la page produit ---
url = "https://www.cdiscount.com/informatique/clavier-souris-webcam/casque-de-gaming-sans-fil-turtle-beach-stealth/f-1070219-tur0731855021048.html?idOffre=-1"
driver.get(url)


# --- 📌 Pourquoi time.sleep(5) ? ---
# La page charge ses avis clients dynamiquement via JavaScript. Si on récupère le HTML immédiatement,
# les avis risquent de ne pas encore être chargés.
time.sleep(5)  # Attente pour s'assurer que tout le contenu dynamique est bien chargé


# --- Récupération du HTML chargé dynamiquement ---
soup = BeautifulSoup(driver.page_source, "html.parser")


# --- Fermeture du navigateur après récupération du contenu ---
driver.quit()


# --- Sélection des avis clients ---
reviews = soup.select("li.c-customer-reviews__item")  # Sélectionne tous les avis sous forme de liste


if not reviews:
   print("Aucun avis trouvé.")
else:
   print(f"{len(reviews)} avis trouvés !")


   review_data = []  # Liste pour stocker les avis
   total_rating = 0  # Pour calculer la moyenne des notes


   # --- 📌 Extraction des informations clés de chaque avis ---
   for review in reviews[:5]:  # Limite à 5 avis pour éviter un traitement trop long
       # ---  Extraction du nom de l'auteur ---
       author_tag = review.select_one("span.c-customer-review__author")  # Sélectionne le nom de l’auteur
       author = author_tag.get_text(strip=True).replace("• publié le", "").strip() if author_tag else "Anonyme"


       # ---  Extraction de la note (étoiles) ---
       rating_tag = review.select_one("span.c-stars-result")  # Sélectionne la note sous forme de nombre
       rating = int(rating_tag["data-score"]) / 20 if rating_tag and rating_tag.has_attr("data-score") else 0
       #  Les notes sont stockées en pourcentage (ex: 80 pour 4 étoiles), donc on divise par 20.


       # ---  Extraction du commentaire ---
       comment_tag = review.select_one("div.o-text")  # Sélectionne le texte du commentaire
       comment = comment_tag.get_text(strip=True) if comment_tag else "Pas de commentaire"


       # ---  Nettoyage des données extraites ---
       comment = re.sub(r"\s+", " ", comment)  # Supprime les espaces en trop pour éviter les retours à la ligne mal placés


       # ---  Stockage des avis sous forme de dictionnaire ---
       review_data.append({
           "Nom": author,
           "Note": rating,
           "Commentaire": comment
       })
       total_rating += rating  # Ajoute la note pour calculer la moyenne plus tard


   # ---  Calcul de la moyenne des notes ---
   average_rating = total_rating / len(review_data) if review_data else 0


   # ---  Analyse du sentiment général en fonction de la moyenne des notes ---
   sentiment = "⚠️ Mitigé" if average_rating < 3 else "👍 Très Positif" if average_rating >= 4 else "😐 Moyennement apprécié"


   # ---  Affichage des résultats ---
   print("\n **Top 5 Avis Clients :**")
   for r in review_data:
       print("\n---------------------")
       print("👤 **Nom**         :", r["Nom"])
       print("⭐ **Note**        : {} / 5".format(r["Note"]))
       print("💬 **Commentaire** :", r["Commentaire"])


   # --- Affichage du résumé ---
   print("\n **Moyenne des notes :** {:.2f} / 5".format(average_rating))
   print(" **Analyse du sentiment général :**", sentiment)






# --- Sauvegarde des avis dans un fichier JSON ---
output = {
    "produit_url": url,
    "nombre_avis_extraits": len(review_data),
    "moyenne_note": round(average_rating, 2),
    "sentiment": sentiment,
    "avis": review_data
}

with open("avis_cdiscount.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

print("\n Les avis ont été enregistrés dans 'avis_cdiscount.json'")
