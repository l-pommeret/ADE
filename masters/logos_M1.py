from icalendar import Calendar, Event
import os
from datetime import datetime

def read_calendar(file_path):
    """Lit un fichier ICS et retourne un objet Calendar."""
    with open(file_path, 'rb') as f:
        return Calendar.from_ical(f.read())

def save_calendar(calendar, file_path):
    """Sauvegarde un objet Calendar dans un fichier ICS."""
    with open(file_path, 'wb') as f:
        f.write(calendar.to_ical())

def create_custom_calendar(source_files, course_filters, output_file):
    """
    Crée un calendrier personnalisé en sélectionnant des cours spécifiques.
    
    Args:
        source_files: Liste de chemins vers les fichiers ICS sources
        course_filters: Dictionnaire où les clés sont les noms des fichiers sources 
                       et les valeurs sont des listes de mots-clés pour filtrer les cours
        output_file: Chemin du fichier ICS de sortie
    """
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
    
    # Sauvegarder le calendrier personnalisé
    save_calendar(custom_cal, output_file)
    print(f"Calendrier personnalisé créé avec succès : {output_file}")

# Exemple d'utilisation
if __name__ == "__main__":
    # Liste des fichiers sources
    source_files = [
        "M1_MFA.ics",
        # Ajoutez d'autres fichiers ICS si nécessaire
    ]
    
    # Définir les filtres pour chaque fichier
    # Format: nom_fichier: [liste de mots-clés]
    course_filters = {
        "M1_MFA.ics": ["Logique", "Algorithmique", "Complexite", "Incompletude et indecidabilites", "Theorie des ensembles", "Statistique fondamentale"],

        # Ajoutez d'autres filtres si nécessaire
    }
    
    # Créer le calendrier personnalisé
    create_custom_calendar(source_files, course_filters, "M1_LOGOS.ics")