import icalendar
import datetime
import pytz
import os
from dateutil.rrule import rrulestr
from dateutil.tz import tzlocal

def sauvegarder_calendrier(chemin_fichier_ics, chemin_fichier_txt=None):
    """
    Lit un fichier ICS, affiche les événements du calendrier et les sauvegarde dans un fichier TXT.
    
    Args:
        chemin_fichier_ics (str): Chemin vers le fichier ICS
        chemin_fichier_txt (str, optional): Chemin vers le fichier TXT de sortie.
                                          Par défaut, utilise le même nom que le fichier ICS avec l'extension .txt
    """
    if not os.path.exists(chemin_fichier_ics):
        print(f"Erreur: Le fichier {chemin_fichier_ics} n'existe pas.")
        return
    
    # Si aucun nom de fichier de sortie n'est fourni, utiliser le même nom avec extension .txt
    if chemin_fichier_txt is None:
        base_nom = os.path.splitext(chemin_fichier_ics)[0]
        chemin_fichier_txt = f"{base_nom}.txt"
    
    try:
        # Lecture du fichier ICS
        with open(chemin_fichier_ics, 'rb') as fichier:
            cal = icalendar.Calendar.from_ical(fichier.read())
        
        # Tri des événements par date
        evenements = []
        for composant in cal.walk():
            if composant.name == "VEVENT":
                debut = composant.get('dtstart')
                if debut:
                    debut_dt = debut.dt
                    # Convertir en datetime si c'est une date
                    if isinstance(debut_dt, datetime.date) and not isinstance(debut_dt, datetime.datetime):
                        debut_dt = datetime.datetime.combine(debut_dt, datetime.time.min)
                    
                    # Ajouter l'événement à la liste
                    evenements.append({
                        'debut': debut_dt,
                        'fin': composant.get('dtend').dt if composant.get('dtend') else None,
                        'resume': str(composant.get('summary', 'Sans titre')),
                        'description': str(composant.get('description', '')),
                        'lieu': str(composant.get('location', '')),
                        'recurrent': True if composant.get('rrule') else False
                    })
        
        # Trier les événements par date de début
        evenements.sort(key=lambda x: x['debut'])
        
        # Préparer le contenu à sauvegarder
        contenu = []
        
        if not evenements:
            message = "Aucun événement trouvé dans le calendrier."
            contenu.append(message)
            print(message)
            return
        
        contenu.append("=== CALENDRIER ===\n")
        jour_courant = None
        
        for evt in evenements:
            jour = evt['debut'].date()
            
            # Ajouter l'en-tête du jour si on change de jour
            if jour_courant != jour:
                jour_courant = jour
                contenu.append(f"\n{jour.strftime('%A %d %B %Y').capitalize()}")
                contenu.append("-" * 30)
            
            # Ajouter l'heure de début et de fin
            heure_debut = evt['debut'].strftime('%H:%M')
            heure_fin = evt['fin'].strftime('%H:%M') if evt['fin'] else "??:??"
            
            contenu.append(f"{heure_debut} - {heure_fin} : {evt['resume']}")
            
            if evt['recurrent']:
                contenu.append("  Note: Événement récurrent")
                
            if evt['lieu'] and evt['lieu'] != 'None':
                contenu.append(f"  Lieu: {evt['lieu']}")
            
            if evt['description'] and evt['description'] != 'None':
                # Limiter la description pour la lisibilité
                desc_lignes = evt['description'].split('\n')
                desc_formatee = "\n    ".join([ligne[:80] + ("..." if len(ligne) > 80 else "") for ligne in desc_lignes[:3]])
                contenu.append(f"  Description: {desc_formatee}")
                
                # Indiquer s'il y a plus de lignes
                if len(desc_lignes) > 3:
                    contenu.append("    [...]")
            
            contenu.append("")
        
        # Sauvegarder dans le fichier texte
        with open(chemin_fichier_txt, 'w', encoding='utf-8') as fichier_sortie:
            fichier_sortie.write("\n".join(contenu))
        
        print(f"Calendrier sauvegardé avec succès dans {chemin_fichier_txt}")
        
        # Afficher également le contenu à l'écran
        for ligne in contenu:
            print(ligne)
            
    except Exception as e:
        print(f"Erreur lors de l'analyse du fichier ICS: {e}")

if __name__ == "__main__":
    # Remplacer par le chemin de votre fichier ICS
    chemin_fichier_ics = "M2_LOGOS.ics"
    
    # Vous pouvez également spécifier un nom de fichier de sortie personnalisé
    # chemin_fichier_txt = "mon_calendrier.txt"
    
    # Appel avec le chemin de sortie par défaut (même nom, extension .txt)
    sauvegarder_calendrier(chemin_fichier_ics)
    
    # Ou appel avec un chemin de sortie personnalisé
    # sauvegarder_calendrier(chemin_fichier_ics, "mon_calendrier.txt")