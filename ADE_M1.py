import requests
import datetime
import re
import os

def fetch_ical(code, start="2024-08-23", end="2025-07-17", year=5, fiche_etalon="58598,"):
    """
    Récupère le calendrier iCal pour un code de formation donné.
    """
    url = "https://adeconsult.app.u-paris.fr/jsp/custom/modules/plannings/anonymous_cal.jsp"
    params = {
        "calType": "ical",
        "firstDate": start,
        "lastDate": end,
        "resources": fiche_etalon + code,
        "projectId": year,
    }

    response = requests.get(url, params=params, timeout=10)
    return response.text

def fix_timezone(ical, ical_name="", enable_FATAL=True):
    """
    Version simplifiée de la fonction fix_timezone pour corriger les problèmes de fuseau horaire
    """
    # On retourne le calendrier tel quel pour cette version simplifiée
    return ical

def get_formation_calendar(formation_name=None, code=None, start="2024-08-23", end="2025-07-17", 
                           year=5, fiche_etalon="58598,", out_dir="."):
    """
    Récupère le calendrier d'une formation par son code.
    
    Arguments:
        formation_name (str): Nom de la formation (facultatif, pour le nom du fichier)
        code (str): Code de la formation à récupérer
        start (str): Date de début au format YYYY-MM-DD
        end (str): Date de fin au format YYYY-MM-DD
        year (int): Année académique (projectId)
        fiche_etalon (str): Fiche étalon
        out_dir (str): Répertoire de sortie pour le fichier ics
        
    Returns:
        str: Chemin du fichier calendrier créé, ou None en cas d'erreur
    """
    # Si aucun code n'est fourni, on ne peut pas continuer
    if not code:
        print("Erreur: Aucun code de formation fourni")
        return None
    
    # Si aucun nom n'est fourni, on utilise le code comme nom
    if not formation_name:
        formation_name = f"Formation-{code}"
    
    # Création du répertoire de sortie si nécessaire
    os.makedirs(out_dir, exist_ok=True)
    
    # Nom du fichier de sortie
    fname = f"{out_dir}/{formation_name}-{code}.ics"
    
    print(f"Récupération du calendrier pour {formation_name} (code: {code})...")
    
    try:
        # Récupération du calendrier
        calendar = fetch_ical(code, start, end, year, fiche_etalon)
        
        # Vérification que nous avons bien reçu un calendrier
        if not calendar.startswith("BEGIN:VCALENDAR"):
            print(f"Erreur: La réponse ne contient pas de calendrier valide.")
            print(f"Début de la réponse: {calendar[:100]}")
            return None
        
        # Enregistrement du calendrier
        with open(fname, "w") as f:
            f.write(calendar)
        
        print(f"Calendrier enregistré dans {fname}")
        return fname
    
    except Exception as e:
        print(f"Erreur lors de la récupération du calendrier: {e}")
        return None

# Exemples d'utilisation
if __name__ == "__main__":
    get_formation_calendar(formation_name="M1-MATH-MFA", code="55513")
    get_formation_calendar(formation_name="M1-MATH-MIC", code="59387")
    get_formation_calendar(formation_name="M1-MATH-MISD", code="47495")

