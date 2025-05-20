import requests
import re
import json
import time
from concurrent.futures import ThreadPoolExecutor
from collections import Counter

def fetch_ical(code, start="2024-08-23", end="2025-07-17", year=5, fiche_etalon="58598,"):
    """
    Récupère le calendrier iCal pour un code de formation donné.
    """
    url = "https://adeconsult.app.u-paris.fr/jsp/custom/modules/plannings/anonymous_cal.jsp"
    params = {
        "calType": "ical",
        "firstDate": start,
        "lastDate": end,
        "resources": fiche_etalon + str(code),
        "projectId": year,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        
        # Vérifier que nous avons bien reçu un calendrier valide
        if response.status_code == 200 and response.text.startswith("BEGIN:VCALENDAR"):
            return response.text
        else:
            return None
    except Exception as e:
        print(f"Erreur lors de la récupération du calendrier pour le code {code}: {e}")
        return None

def extract_formation_name(ical_content):
    """
    Extrait le nom de formation commun à tous les événements du calendrier iCal.
    """
    if not ical_content or "BEGIN:VEVENT" not in ical_content:
        return None
    
    # Extraire toutes les descriptions d'événements
    description_pattern = re.compile(r'DESCRIPTION:(.*?)(?:END:|UID:)', re.DOTALL)
    descriptions = description_pattern.findall(ical_content)
    
    if not descriptions:
        return None
    
    # Liste pour stocker les formations trouvées dans chaque événement
    all_formations_per_event = []
    
    for description in descriptions:
        # Nettoyer la description et la diviser en lignes
        clean_desc = description.replace('\\n', '\n')
        lines = [line.strip() for line in clean_desc.split('\n') if line.strip()]
        
        # Filtrer les lignes qui semblent être des noms de formation
        # On recherche des motifs comme "M2 DATA", "M1 INFO", etc.
        formation_pattern = re.compile(r'^(M[1-2]|L[1-3])\s+[A-Z0-9/\-]+$')
        alt_formation_pattern = re.compile(r'^(M[1-2]|L[1-3])\-[A-Z0-9/\-]+$')
        
        # Collecter les formations pour cet événement
        event_formations = []
        for line in lines:
            if formation_pattern.match(line) or alt_formation_pattern.match(line):
                event_formations.append(line)
        
        # Si des formations ont été trouvées pour cet événement, les ajouter à la liste
        if event_formations:
            all_formations_per_event.append(set(event_formations))
    
    # S'il n'y a aucun événement avec des formations, retourner None
    if not all_formations_per_event:
        return None
    
    # Trouver l'intersection de toutes les formations (formations communes à tous les événements)
    common_formations = set.intersection(*all_formations_per_event) if all_formations_per_event else set()
    
    # Si aucune formation commune n'est trouvée, essayer une approche alternative
    if not common_formations and all_formations_per_event:
        # Compter la fréquence de chaque formation
        all_formations = [f for event_set in all_formations_per_event for f in event_set]
        formation_counter = Counter(all_formations)
        
        # Considérer comme "communes" les formations qui apparaissent dans au moins 80% des événements
        min_occurrences = 0.8 * len(all_formations_per_event)
        common_formations = [f for f, count in formation_counter.items() if count >= min_occurrences]
    
    return list(common_formations) if common_formations else None

def process_formation_code(code):
    """
    Traite un code de formation: récupère le calendrier, extrait le nom et retourne le résultat.
    """
    print(f"Traitement du code {code}")
    ical_content = fetch_ical(code)
    
    if not ical_content:
        return None
    
    formation_names = extract_formation_name(ical_content)
    
    if formation_names:
        result = {
            "code": code,
            "formation_names": formation_names
        }
        print(f"Code {code}: Formation trouvée - {formation_names}")
        return result
    
    return None

def save_results(results, filename="formations.json"):
    """
    Sauvegarde les résultats dans un fichier JSON.
    """
    # Crée un dictionnaire avec les codes comme clés
    formations_dict = {}
    for result in results:
        if result:
            formations_dict[str(result["code"])] = result["formation_names"]
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(formations_dict, f, ensure_ascii=False, indent=2)
    
    print(f"Résultats sauvegardés dans {filename}")

def test_single_code(code):
    """
    Teste l'extraction pour un seul code de formation.
    """
    result = process_formation_code(code)
    if result:
        print(f"Code {code}: {result['formation_names']}")
    else:
        print(f"Code {code}: Aucune formation trouvée")

def main():
    # Option pour tester un seul code
    test_code = 14629
    test_single_code(test_code)
    
    # Option pour exécuter sur tous les codes
    run_all = input("Voulez-vous exécuter l'extraction pour tous les codes (0-30000)? (o/n): ")
    
    if run_all.lower() != 'o':
        print("Extraction complète annulée.")
        return
    
    start_time = time.time()
    
    # Codes de formation à traiter
    formation_codes = range(30001)
    
    results = []
    
    # Utilisation de ThreadPoolExecutor pour paralléliser les requêtes
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Soumettre les tâches
        futures = [executor.submit(process_formation_code, code) for code in formation_codes]
        
        # Récupérer les résultats au fur et à mesure
        for i, future in enumerate(futures):
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Erreur lors du traitement du code {i}: {e}")
            
            # Affichage de la progression
            if (i + 1) % 100 == 0:
                elapsed_time = time.time() - start_time
                print(f"Progression: {i + 1}/{len(formation_codes)} codes traités ({(i + 1) / len(formation_codes) * 100:.2f}%) - Temps écoulé: {elapsed_time:.2f}s")
                
                # Sauvegarde intermédiaire des résultats
                save_results(results)
    
    # Sauvegarde finale des résultats
    save_results(results)
    
    elapsed_time = time.time() - start_time
    print(f"Traitement terminé en {elapsed_time:.2f} secondes. {len(results)} formations trouvées.")

if __name__ == "__main__":
    main()