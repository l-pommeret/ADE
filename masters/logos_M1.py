from icalendar import Calendar, Event
import os
import json
from datetime import datetime

def read_calendar(file_path):
    """Lit un fichier ICS et retourne un objet Calendar."""
    with open(file_path, 'rb') as f:
        return Calendar.from_ical(f.read())

def save_calendar(calendar, file_path):
    """Sauvegarde un objet Calendar dans un fichier ICS."""
    with open(file_path, 'wb') as f:
        f.write(calendar.to_ical())

def backup_custom_events(calendar_path, custom_events_json):
    """
    Sauvegarde les événements personnalisés d'un calendrier.
    Les événements personnalisés sont identifiés par un UID qui commence par 'custom_'.
    
    Args:
        calendar_path: Chemin vers le fichier calendrier ICS
        custom_events_json: Chemin vers le fichier JSON où sauvegarder les événements
    """
    if not os.path.exists(calendar_path):
        print(f"Calendrier non trouvé: {calendar_path}")
        return []
    
    try:
        # Lire le calendrier
        cal = read_calendar(calendar_path)
        
        # Extraire les événements personnalisés
        custom_events = []
        for component in cal.walk():
            if component.name == "VEVENT":
                uid = str(component.get('uid', ''))
                if uid.startswith('custom_'):
                    # Convertir l'événement en dictionnaire pour le JSON
                    event_dict = {}
                    for key, value in component.items():
                        if key == 'dtstart' or key == 'dtend':
                            # Stocker la date au format ISO
                            event_dict[key] = value.dt.isoformat()
                        else:
                            # Stocker les autres valeurs en texte
                            event_dict[key] = str(value)
                    
                    # Stocker les props supplémentaires
                    if 'for_m1' in component:
                        event_dict['for_m1'] = bool(component['for_m1'])
                    else:
                        event_dict['for_m1'] = True
                        
                    if 'for_m2' in component:
                        event_dict['for_m2'] = bool(component['for_m2'])
                    else:
                        event_dict['for_m2'] = True
                    
                    custom_events.append(event_dict)
        
        # Sauvegarder dans le fichier JSON
        with open(custom_events_json, 'w', encoding='utf-8') as f:
            json.dump(custom_events, f, ensure_ascii=False, indent=4)
            
        print(f"Sauvegarde de {len(custom_events)} événements personnalisés dans {custom_events_json}")
        return custom_events
    
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des événements personnalisés: {e}")
        return []

def restore_custom_events(calendar, custom_events_json):
    """
    Restaure les événements personnalisés dans un calendrier.
    
    Args:
        calendar: Objet Calendar où ajouter les événements
        custom_events_json: Chemin vers le fichier JSON contenant les événements
    """
    if not os.path.exists(custom_events_json):
        print(f"Fichier d'événements personnalisés non trouvé: {custom_events_json}")
        return calendar
    
    try:
        # Charger les événements du fichier JSON
        with open(custom_events_json, 'r', encoding='utf-8') as f:
            custom_events = json.load(f)
        
        # Créer et ajouter chaque événement au calendrier
        for event_dict in custom_events:
            event = Event()
            
            # Ajouter les propriétés de base
            for key, value in event_dict.items():
                if key in ['for_m1', 'for_m2']:  # Ignorer les props spéciales
                    continue
                
                if key == 'dtstart' or key == 'dtend':
                    # Recréer les dates à partir du format ISO
                    if 'T' in value:  # Datetime
                        dt = datetime.fromisoformat(value)
                    else:  # Date
                        dt = datetime.strptime(value, '%Y-%m-%d').date()
                    event.add(key, dt)
                else:
                    event.add(key, value)
            
            # Ajouter l'événement au calendrier
            calendar.add_component(event)
        
        print(f"Restauration de {len(custom_events)} événements personnalisés")
        return calendar
    
    except Exception as e:
        print(f"Erreur lors de la restauration des événements personnalisés: {e}")
        return calendar

def create_custom_calendar(source_files, course_filters, output_file):
    """
    Crée un calendrier personnalisé en sélectionnant des cours spécifiques.
    Préserve les événements personnalisés existants.
    
    Args:
        source_files: Liste de chemins vers les fichiers ICS sources
        course_filters: Dictionnaire où les clés sont les noms des fichiers sources 
                       et les valeurs sont des listes de mots-clés pour filtrer les cours
        output_file: Chemin du fichier ICS de sortie
    """
    # Définir le chemin pour les événements personnalisés
    custom_events_json = f"{os.path.splitext(output_file)[0]}_custom_events.json"
    
    # Sauvegarder les événements personnalisés existants
    backup_custom_events(output_file, custom_events_json)
    
    # Créer un nouveau calendrier
    custom_cal = Calendar()
    custom_cal.add('prodid', '-//Custom Calendar//FR')
    custom_cal.add('version', '2.0')
    custom_cal.add('calscale', 'GREGORIAN')
    custom_cal.add('method', 'REQUEST')
    
    # Pour chaque fichier source
    for source_file in source_files:
        # Obtenir le nom du fichier sans l'extension
        file_name = os.path.basename(source_file)
        
        # Vérifier si nous avons des filtres pour ce fichier
        if file_name not in course_filters:
            continue
        
        # Lire le calendrier source
        cal = read_calendar(source_file)
        
        # Pour chaque événement dans le calendrier
        for component in cal.walk():
            if component.name == "VEVENT":
                # Vérifier si l'événement correspond à l'un de nos filtres
                summary = str(component.get('summary', ''))
                
                # Si le résumé contient l'un des mots-clés pour ce fichier
                if any(keyword.lower() in summary.lower() for keyword in course_filters[file_name]):
                    # Ajouter l'événement à notre calendrier personnalisé
                    custom_cal.add_component(component)
    
    # Restaurer les événements personnalisés
    custom_cal = restore_custom_events(custom_cal, custom_events_json)
    
    # Sauvegarder le calendrier personnalisé
    save_calendar(custom_cal, output_file)
    print(f"Calendrier personnalisé créé avec succès : {output_file}")

# Exemple d'utilisation
if __name__ == "__main__":
    # Liste des fichiers sources
    source_files = [
        "M1_MFA.ics",
        "M2_LMFI.ics",
        # Ajoutez d'autres fichiers ICS si nécessaire
    ]
    
    # Définir les filtres pour chaque fichier
    # Format: nom_fichier: [liste de mots-clés]
    course_filters = {
        "M2_LMFI.ics": ["Cours préliminaire de logique"],
        "M1_MFA.ics": ["Logique", "Algorithmique", "Complexite", "Incompletude et indecidabilites", "Theorie des ensembles", "Statistique fondamentale"],

        # Ajoutez d'autres filtres si nécessaire
    }
    
    # Créer le calendrier personnalisé
    create_custom_calendar(source_files, course_filters, "M1_LOGOS.ics")