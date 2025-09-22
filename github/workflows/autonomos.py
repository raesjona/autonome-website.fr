# === AUTONOMOS.PY VERSIE 2.0 (FRANS) ===
import openai
import os
import random
from datetime import datetime
import git

# --- CONFIGURATION ---
openai.api_key = os.getenv('OPENAI_API_KEY')
REPO_PATH = '.' 
POSTS_PATH = '_posts' 

# --- LISTE DE SUJETS (EN FRANÇAIS) ---
sujets = [
    "5 façons de réduire le plastique dans votre appartement",
    "Comment créer un potager vertical sur votre balcon ?",
    "Les meilleures plantes purificatrices d'air pour un petit salon",
    "Vie minimaliste : astuces de rangement pour un petit appartement",
    "DIY : fabriquez votre propre bac à compost pour le balcon",
    "Économiser l'énergie dans un appartement en location : un guide complet",
    "Faire ses courses zéro déchet : comment commencer ?",
    "Produits de nettoyage durables que vous pouvez faire vous-même",
    "Conseils pour un intérieur d'occasion et vintage",
    "Économiser l'eau dans la salle de bain : ajustements simples",
    "Composer une garde-robe capsule : moins de vêtements, plus de style",
    "Pesticides naturels pour vos plantes d'intérieur",
    "Upcycling : donnez une nouvelle vie à de vieux meubles dans votre appartement"
]

# --- FONCTIONS ---

def generer_article(sujet):
    """Génère un article en français avec le puissant modèle GPT-4o."""
    try:
        prompt = f"""
        Rédige un article de blog en français d'environ 500 mots, optimisé pour le SEO, approfondi et captivant sur : '{sujet}'.
        Utilise des titres clairs (markdown ##), des paragraphes courts et un ton expert et serviable.
        Donne des conseils pratiques et uniques directement applicables. Conclus par un résumé percutant.
        Le style d'écriture est fluide, inspirant et destiné aux millennials vivant en ville.
        """
        response = openai.chat.completions.create(
            model="gpt-4o", # Utilise le modèle le plus puissant et mis à niveau
            messages=[
                {"role": "system", "content": "Vous êtes un expert en vie durable et consciente et vous écrivez des articles de blog inspirants."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erreur lors de la génération de l'article : {e}")
        return None

def ajouter_liens_affiliation(texte):
    """Ajoute des liens d'affiliation en fonction des mots-clés."""
    if not os.path.exists(POSTS_PATH):
        os.makedirs(POSTS_PATH)
    donnees_affiliation = os.getenv('AFFILIATE_LINKS', '').split(';')
    if not donnees_affiliation or donnees_affiliation == ['']:
        return texte
    liens_map = {item.split(',')[0]: item.split(',')[1] for item in donnees_affiliation if ',' in item}
    
    for mot_cle, lien in liens_map.items():
        if mot_cle.lower() in texte.lower():
            cta = f'\n\n> **Recommandé : Découvrez [les produits pertinents pour {mot_cle}]({lien}) sur Bol.com !**\n'
            texte += cta
            # Arrête après le premier lien pertinent pour garder l'article naturel
            return texte
    return texte

def publier_sur_github(sujet, contenu):
    """Crée un nouveau fichier de post et le commit sur GitHub."""
    aujourdhui = datetime.now()
    # Crée un nom de fichier convivial pour l'URL
    slug = sujet.lower().replace(' ', '-').replace('?', '').replace(':', '').replace(',', '')[:40]
    nom_fichier = f"{aujourdhui.strftime('%Y-%-m-%-d')}-{slug}.md"
    chemin = os.path.join(POSTS_PATH, nom_fichier)

    front_matter = f"""---
layout: post
title:  "{sujet.replace('"', "'")}"
date:   {aujourdhui.isoformat()}
---
"""
    contenu_complet = front_matter + contenu

    with open(chemin, 'w', encoding='utf-8') as f:
        f.write(contenu_complet)

    try:
        repo = git.Repo(REPO_PATH)
        repo.config_writer().set_value("user", "name", "Autonomos Bot").release()
        repo.config_writer().set_value("user", "email", "bot@github.com").release()
        repo.index.add([chemin])
        repo.index.commit(f"Nouvel article publié : {sujet}")
        origin = repo.remote(name='origin')
        origin.push()
        print(f"Article '{nom_fichier}' publié avec succès.")
    except Exception as e:
        print(f"Erreur lors de la publication sur GitHub : {e}")

# --- SCRIPT PRINCIPAL QUI TOURNE CHAQUE JOUR ---
if __name__ == "__main__":
    sujet_choisi = random.choice(sujets)
    print(f"Sujet choisi : {sujet_choisi}")
    
    texte_article = generer_article(sujet_choisi)
    
    if texte_article:
        article_avec_liens = ajouter_liens_affiliation(texte_article)
        publier_sur_github(sujet_choisi, article_avec_liens)
