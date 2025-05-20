import icalendar
import datetime
import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

def charger_calendrier(chemin_fichier_ics):
    """
    Lit un fichier ICS et retourne les événements du calendrier.
    
    Args:
        chemin_fichier_ics (str): Chemin vers le fichier ICS
    
    Returns:
        list: Liste des événements formatés
    """
    try:
        # Lecture du fichier ICS
        with open(chemin_fichier_ics, 'rb') as fichier:
            cal = icalendar.Calendar.from_ical(fichier.read())
        
        # Extraction des événements
        evenements = []
        for composant in cal.walk():
            if composant.name == "VEVENT":
                debut = composant.get('dtstart')
                if debut:
                    debut_dt = debut.dt
                    # Convertir en datetime si c'est une date
                    if isinstance(debut_dt, datetime.date) and not isinstance(debut_dt, datetime.datetime):
                        debut_dt = datetime.datetime.combine(debut_dt, datetime.time.min)
                    
                    # Gestion des fuseaux horaires (conversion en heure locale)
                    if hasattr(debut_dt, 'tzinfo') and debut_dt.tzinfo is not None:
                        debut_dt = debut_dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
                    
                    fin_dt = None
                    if composant.get('dtend'):
                        fin_dt = composant.get('dtend').dt
                        if hasattr(fin_dt, 'tzinfo') and fin_dt.tzinfo is not None:
                            fin_dt = fin_dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
                    
                    # Ajouter l'événement à la liste
                    evenements.append({
                        'id': str(composant.get('uid', '')),
                        'title': str(composant.get('summary', 'Sans titre')),
                        'start': debut_dt.isoformat(),
                        'end': fin_dt.isoformat() if fin_dt else None,
                        'description': str(composant.get('description', '')),
                        'location': str(composant.get('location', '')),
                        'allDay': not isinstance(debut_dt, datetime.datetime)
                    })
        
        return evenements
    
    except Exception as e:
        print(f"Erreur lors de l'analyse du fichier ICS: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def get_events():
    chemin_fichier_ics = os.path.join('masters', 'M2_LOGOS.ics')
    evenements = charger_calendrier(chemin_fichier_ics)
    return jsonify(evenements)

if __name__ == "__main__":
    # Création des répertoires pour les templates s'ils n'existent pas
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    app.run(debug=True)