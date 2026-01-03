import requests
from bs4 import BeautifulSoup

# URL de la recette
url = "https://www.marmiton.org/recettes/oubliez-le-gratin-de-courge-voici-comment-preparer-une-butternut-farcie-facon-tartiflette-s4104199.html"

# Requête HTTP
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")

    with open("recette.txt", "w", encoding="utf-8") as f:

        # --- Titre ---
        title = soup.find("h1")
        if title:
            f.write("Titre de la recette :\n")
            f.write(title.get_text(strip=True) + "\n\n")
        else:
            f.write("Titre non trouvé\n\n")

        # --- Ingrédients ---
        ingredients_section = soup.find("strong", string="Pour deux personnes")
        if ingredients_section:
            ingredients_list = ingredients_section.find_next("ul")
            ingredient_items = ingredients_list.find_all("li")

            f.write("Ingrédients :\n")
            for ingredient in ingredient_items:
                f.write("- " + ingredient.get_text(strip=True) + "\n")
            f.write("\n")
        else:
            f.write("Ingrédients non trouvés\n\n")

        # --- Étapes ---
        steps_section = soup.find("h2", id="af_intertitre_8")
        if steps_section:
            step_paragraphs = steps_section.find_all_next("p")

            f.write("Étapes de préparation :\n")
            for idx, step in enumerate(step_paragraphs, 1):
                f.write(f"{idx}. {step.get_text(strip=True)}\n")
        else:
            f.write("Étapes non trouvées\n")

    print(" Recette enregistrée dans le fichier recette.txt")

else:
    print(" Erreur lors de la récupération :", response.status_code)
