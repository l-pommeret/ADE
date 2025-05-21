import os
import json
import icalendar
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from course_data import COURSES, USERS
import datetime

app = Flask(__name__)
app.secret_key = 'logos_master_app_secret_key'  # Clé secrète pour les sessions

# Persistence du stockage des utilisateurs
USERS_FILE = 'users.json'

# Charger les utilisateurs depuis le fichier s'il existe
def load_users():
    global USERS
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            USERS = json.load(f)
    return USERS

# Sauvegarder les utilisateurs dans le fichier
def save_users():
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(USERS, f, indent=4)

# Fonction pour vérifier si un cours peut être sélectionné
def can_select_course(username, semester, course_id):
    user = USERS.get(username)
    if not user:
        return False, "Utilisateur non trouvé"
    
    # Vérifier si le cours est déjà sélectionné
    if course_id in user['selected_courses'][semester]:
        return False, "Ce cours est déjà sélectionné"
    
    # Obtenir le cours à partir de son ID
    course_info = None
    block_id = None
    for block_id, block_data in COURSES[semester]['blocks'].items():
        for course in block_data['courses']:
            if course['id'] == course_id:
                course_info = course
                break
        if course_info:
            break
    
    if not course_info:
        return False, "Cours non trouvé"
    
    # Vérifier les cas spéciaux pour le semestre 4
    if semester == 'semestre4':
        # Vérifier si l'étudiant a choisi le stage (itinéraire stage)
        if 's4_e2' in user['selected_courses'][semester]:
            if course_id != 's4_e2':
                return False, "Vous avez choisi l'itinéraire stage, vous ne pouvez pas sélectionner d'autres cours"
        
        # Si l'étudiant a choisi le mémoire (itinéraire classique)
        elif 's4_e1' in user['selected_courses'][semester]:
            # Vérifier qu'il ne dépasse pas 2 cours en plus du mémoire
            if len(user['selected_courses'][semester]) >= 3 and course_id != 's4_e1':
                return False, "Vous ne pouvez pas sélectionner plus de 2 cours en plus du mémoire"
            
            # Vérifier que les cours viennent de blocs différents
            selected_blocks = []
            for selected_id in user['selected_courses'][semester]:
                if selected_id == 's4_e1':  # Ignorer le mémoire pour cette vérification
                    continue
                for b_id, block_data in COURSES[semester]['blocks'].items():
                    if b_id == 'E':  # Ignorer le bloc mémoire/stage
                        continue
                    for c in block_data['courses']:
                        if c['id'] == selected_id:
                            selected_blocks.append(b_id)
                            break
            
            # Vérifier si le nouveau cours appartient à un bloc déjà sélectionné
            if block_id in selected_blocks and block_id != 'E':
                return False, "Vous devez choisir des cours de blocs différents"
        
        # Si c'est le premier choix et qu'il s'agit du stage
        elif course_id == 's4_e2':
            return True, ""
        
        # Si c'est le premier choix et qu'il s'agit du mémoire
        elif course_id == 's4_e1':
            return True, ""
    
    return True, ""

# Fonction pour vérifier si la sélection de cours d'un utilisateur respecte les règles
def validate_selection(username, semester):
    user = USERS.get(username)
    if not user:
        return False, "Utilisateur non trouvé"
    
    selected_courses = user['selected_courses'][semester]
    if not selected_courses:
        return False, "Aucun cours sélectionné"
    
    # Obtenir les détails des cours sélectionnés
    selected_course_details = []
    for course_id in selected_courses:
        for block_id, block_data in COURSES[semester]['blocks'].items():
            for course in block_data['courses']:
                if course['id'] == course_id:
                    course_copy = course.copy()
                    course_copy['block_id'] = block_id
                    selected_course_details.append(course_copy)
                    break
    
    # Calculer le nombre total d'ECTS
    total_ects = sum(course['ects'] for course in selected_course_details)
    
    # Vérifier le nombre minimum de cours et d'ECTS
    valid_rule = None
    for rule in COURSES[semester]['rules']:
        # Vérifier le nombre de cours
        if len(selected_course_details) < rule['min_courses']:
            continue
        
        # Vérifier le nombre d'ECTS
        if total_ects < rule['min_ects']:
            continue
        
        # Vérifier les exigences par bloc
        block_counts = {}
        for course in selected_course_details:
            block_id = course['block_id']
            block_counts[block_id] = block_counts.get(block_id, 0) + 1
        
        # Vérifier si chaque bloc a le bon nombre de cours
        block_requirements_satisfied = True
        for block_id, required_count in rule['block_requirements'].items():
            if block_counts.get(block_id, 0) < required_count:
                block_requirements_satisfied = False
                break
        
        if not block_requirements_satisfied:
            continue
        
        # Vérifier les règles spéciales
        if 'special' in rule:
            if rule['special'] == "One course of 12 ECTS must be selected":
                if not any(course['ects'] == 12 for course in selected_course_details):
                    continue
        
        valid_rule = rule
        break
    
    if valid_rule:
        return True, f"Sélection valide. Total ECTS: {total_ects}"
    else:
        return False, f"Sélection non valide. Vérifiez les règles du semestre. Total ECTS: {total_ects}"

# Routes de l'application
@app.route('/')
def index():
    if 'username' in session:
        # Rediriger vers l'emploi du temps correspondant au type de compte
        account_type = session.get('account_type', 'm1')
        
        if account_type == 'm2':
            return redirect(url_for('edt', niveau='m2'))
        elif account_type == 'alumni':
            return redirect(url_for('edt', niveau='m2'))  # Les alumni voient l'emploi du temps M2 par défaut
        else:
            return redirect(url_for('edt', niveau='m1'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        user = users.get(username)
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['name'] = user['name']
            session['account_type'] = user.get('account_type', 'm1')
            session['is_admin'] = user.get('is_admin', False)
            flash('Connexion réussie!', 'success')
            
            # Rediriger vers l'emploi du temps correspondant au type de compte
            account_type = user.get('account_type', 'm1')
            if account_type == 'm2':
                return redirect(url_for('edt', niveau='m2'))
            else:
                return redirect(url_for('edt', niveau='m1'))
        else:
            flash('Identifiants incorrects.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        name = request.form['name']
        account_type = request.form['account_type']
        
        users = load_users()
        
        if username in users:
            flash('Ce nom d\'utilisateur est déjà pris.', 'danger')
        elif password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            users[username] = {
                'username': username,
                'password': hashed_password,
                'email': email,
                'name': name,
                'account_type': account_type,
                'is_admin': account_type == 'prof',
                'selected_courses': {
                    'semestre1': [],
                    'semestre2': [],
                    'semestre3': [],
                    'semestre4': []
                },
                'messages': [],
                'attendance_years': [] if account_type == 'alumni' else None,
                'attended_levels': [] if account_type == 'alumni' else None
            }
            save_users()
            flash('Activation du compte réussie! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('login'))
    
    users = load_users()
    user = users.get(session['username'])
    
    # Calculer le nombre total d'ECTS par semestre
    semester_ects = {}
    for semester, course_ids in user['selected_courses'].items():
        total_ects = 0
        for course_id in course_ids:
            for block in COURSES[semester]['blocks'].values():
                for course in block['courses']:
                    if course['id'] == course_id:
                        total_ects += course['ects']
                        break
        semester_ects[semester] = total_ects
    
    return render_template('dashboard.html', 
                           user=user, 
                           courses=COURSES, 
                           semester_ects=semester_ects,
                           is_admin=user.get('is_admin', False),
                           account_type=user.get('account_type', 'm1'))

@app.route('/semester/<semester>')
def semester(semester):
    if 'username' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('login'))
    
    if semester not in COURSES:
        flash('Semestre non trouvé.', 'danger')
        return redirect(url_for('dashboard'))
    
    users = load_users()
    user = users.get(session['username'])
    account_type = user.get('account_type', 'm1')
    is_admin = user.get('is_admin', False)
    
    # Vérification des droits d'accès aux semestres selon le type de compte
    if not is_admin and account_type not in ['prof', 'alumni']:
        if account_type == 'm1' and semester in ['semestre3', 'semestre4']:
            flash('Vous n\'avez pas accès à ce semestre avec votre type de compte.', 'danger')
            return redirect(url_for('dashboard'))
        elif account_type == 'm2' and semester in ['semestre1', 'semestre2']:
            flash('Vous n\'avez pas accès à ce semestre avec votre type de compte.', 'danger')
            return redirect(url_for('dashboard'))
    
    return render_template('semester.html', 
                           semester_id=semester,
                           semester_data=COURSES[semester],
                           user=user,
                           is_admin=is_admin,
                           account_type=account_type)

@app.route('/api/select_course', methods=['POST'])
def select_course():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Veuillez vous connecter'})
    
    data = request.json
    semester = data.get('semester')
    course_id = data.get('course_id')
    username = session['username']
    
    users = load_users()
    user = users.get(username)
    
    # Vérifier si le cours peut être sélectionné
    can_select, message = can_select_course(username, semester, course_id)
    if not can_select:
        return jsonify({'success': False, 'message': message})
    
    # Ajouter le cours à la sélection de l'utilisateur
    user['selected_courses'][semester].append(course_id)
    save_users()
    
    return jsonify({'success': True, 'message': 'Cours sélectionné'})

@app.route('/api/deselect_course', methods=['POST'])
def deselect_course():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Veuillez vous connecter'})
    
    data = request.json
    semester = data.get('semester')
    course_id = data.get('course_id')
    username = session['username']
    
    users = load_users()
    user = users.get(username)
    
    # Vérifier si le cours est bien dans la sélection
    if course_id not in user['selected_courses'][semester]:
        return jsonify({'success': False, 'message': 'Ce cours n\'est pas dans votre sélection'})
    
    # Pour le semestre 4, des règles spéciales s'appliquent
    if semester == 'semestre4':
        # Si c'est le mémoire/stage, il faut vérifier les implications
        if course_id == 's4_e1' or course_id == 's4_e2':
            user['selected_courses'][semester] = []  # Réinitialiser toute la sélection du semestre 4
    
    # Retirer le cours de la sélection
    if course_id in user['selected_courses'][semester]:
        user['selected_courses'][semester].remove(course_id)
    
    save_users()
    
    return jsonify({'success': True, 'message': 'Cours retiré de la sélection'})

@app.route('/api/validate_selection', methods=['POST'])
def api_validate_selection():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Veuillez vous connecter'})
    
    data = request.json
    semester = data.get('semester')
    username = session['username']
    
    is_valid, message = validate_selection(username, semester)
    
    return jsonify({'success': is_valid, 'message': message})

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('login'))
    
    users = load_users()
    user = users.get(session['username'])
    
    return render_template('profile.html', user=user)

@app.route('/profile/update', methods=['POST'])
def update_profile():
    if 'username' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('login'))
    
    username = session['username']
    users = load_users()
    user = users.get(username)
    
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Mettre à jour les informations de base
        user['email'] = email
        user['name'] = name
        session['name'] = name
        
        # Si c'est un alumni, mettre à jour les informations supplémentaires
        if user.get('account_type') == 'alumni':
            attendance_years = request.form.getlist('attendance_years')
            attended_levels = request.form.getlist('attended_levels')
            if attendance_years:
                user['attendance_years'] = attendance_years
            if attended_levels:
                user['attended_levels'] = attended_levels
        
        # Mettre à jour le mot de passe si demandé
        if current_password and new_password and confirm_password:
            if not check_password_hash(user['password'], current_password):
                flash('Mot de passe actuel incorrect.', 'danger')
                return redirect(url_for('profile'))
            
            if new_password != confirm_password:
                flash('Les nouveaux mots de passe ne correspondent pas.', 'danger')
                return redirect(url_for('profile'))
            
            user['password'] = generate_password_hash(new_password)
            flash('Mot de passe mis à jour avec succès.', 'success')
        
        save_users()
        flash('Profil mis à jour avec succès.', 'success')
        return redirect(url_for('profile'))

# Annuaire des utilisateurs
@app.route('/annuaire')
def annuaire():
    if 'username' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('login'))
    
    users = load_users()
    user = users.get(session['username'])
    
    # Récupérer tous les utilisateurs pour l'annuaire
    annuaire_users = []
    for username, user_data in users.items():
        # Récupérer les informations des cours sélectionnés
        selected_courses_info = {}
        for semester, course_ids in user_data.get('selected_courses', {}).items():
            selected_courses_info[semester] = []
            for course_id in course_ids:
                for block in COURSES[semester]['blocks'].values():
                    for course in block['courses']:
                        if course['id'] == course_id:
                            selected_courses_info[semester].append({
                                'id': course_id,
                                'name': course.get('title', 'Cours sans titre'),  # Utiliser 'title' au lieu de 'name'
                                'ects': course['ects']
                            })
                            break
        
        # Créer l'entrée utilisateur pour l'annuaire
        annuaire_users.append({
            'username': username,
            'name': user_data.get('name', username),
            'email': user_data.get('email', ''),
            'account_type': user_data.get('account_type', 'm1'),
            'is_admin': user_data.get('is_admin', False),
            'attendance_years': user_data.get('attendance_years', []),
            'selected_courses': selected_courses_info
        })
    
    # Tri par type de compte et nom
    annuaire_users.sort(key=lambda x: (
        0 if x['is_admin'] else (1 if x['account_type'] == 'alumni' else 2),
        x['name']
    ))
    
    return render_template('annuaire.html', 
                          user=user, 
                          annuaire_users=annuaire_users)

# Messagerie
@app.route('/messages')
def messages():
    if 'username' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('login'))
    
    users = load_users()
    user = users.get(session['username'])
    
    # Liste des utilisateurs pour envoyer des messages
    other_users = []
    for username, user_data in users.items():
        if username != session['username']:
            other_users.append({
                'username': username,
                'name': user_data.get('name', username),
                'account_type': user_data.get('account_type', 'm1')
            })
    
    # Tri par type de compte et nom
    other_users.sort(key=lambda x: (x['account_type'], x['name']))
    
    return render_template('messages.html', 
                          user=user, 
                          messages=user.get('messages', []), 
                          other_users=other_users)

@app.route('/messages/send', methods=['POST'])
def send_message():
    if 'username' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        recipient_username = request.form['recipient']
        subject = request.form['subject']
        content = request.form['content']
        
        if not recipient_username or not subject or not content:
            flash('Veuillez remplir tous les champs.', 'danger')
            return redirect(url_for('messages'))
        
        users = load_users()
        
        # Vérifier que le destinataire existe
        if recipient_username not in users:
            flash('Destinataire introuvable.', 'danger')
            return redirect(url_for('messages'))
        
        # Préparer le message
        message = {
            'id': f"msg_{datetime.datetime.now().timestamp()}",
            'sender': session['username'],
            'sender_name': users[session['username']]['name'],
            'subject': subject,
            'content': content,
            'timestamp': datetime.datetime.now().isoformat(),
            'read': False
        }
        
        # Ajouter le message au destinataire
        if 'messages' not in users[recipient_username]:
            users[recipient_username]['messages'] = []
        
        users[recipient_username]['messages'].append(message)
        save_users()
        
        flash('Message envoyé avec succès.', 'success')
        return redirect(url_for('messages'))
    
    return redirect(url_for('messages'))

@app.route('/messages/read/<message_id>')
def read_message(message_id):
    if 'username' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('login'))
    
    users = load_users()
    user = users.get(session['username'])
    
    # Chercher le message
    message = None
    for msg in user.get('messages', []):
        if msg['id'] == message_id:
            message = msg
            msg['read'] = True  # Marquer comme lu
            break
    
    if not message:
        flash('Message introuvable.', 'danger')
        return redirect(url_for('messages'))
    
    save_users()
    
    return render_template('message_detail.html', user=user, message=message)

@app.route('/messages/delete/<message_id>', methods=['POST'])
def delete_message(message_id):
    if 'username' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('login'))
    
    users = load_users()
    user = users.get(session['username'])
    
    # Chercher et supprimer le message
    messages = user.get('messages', [])
    user['messages'] = [msg for msg in messages if msg['id'] != message_id]
    
    save_users()
    flash('Message supprimé.', 'success')
    
    return redirect(url_for('messages'))

# Fonction pour charger les événements du calendrier depuis un fichier ICS
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
                    
                    # Gestion des fuseaux horaires (conversion en heure locale et correction du décalage)
                    if hasattr(debut_dt, 'tzinfo') and debut_dt.tzinfo is not None:
                        # Correction du décalage horaire - ajout de 2 heures (les horaires sont en UTC)
                        debut_dt = debut_dt.astimezone(datetime.timezone.utc) + datetime.timedelta(hours=2)
                        debut_dt = debut_dt.replace(tzinfo=None)
                    
                    fin_dt = None
                    if composant.get('dtend'):
                        fin_dt = composant.get('dtend').dt
                        if hasattr(fin_dt, 'tzinfo') and fin_dt.tzinfo is not None:
                            # Correction du décalage horaire - ajout de 2 heures
                            fin_dt = fin_dt.astimezone(datetime.timezone.utc) + datetime.timedelta(hours=2)
                            fin_dt = fin_dt.replace(tzinfo=None)
                    
                    # Ajouter l'événement à la liste
                    evenements.append({
                        'id': str(composant.get('uid', '')),
                        'title': str(composant.get('summary', 'Sans titre')),
                        'start': debut_dt.isoformat(),
                        'end': fin_dt.isoformat() if fin_dt else None,
                        'description': str(composant.get('description', '')),
                        'location': str(composant.get('location', '')),
                        'allDay': not isinstance(debut_dt, datetime.datetime),
                        'isCustom': False
                    })
        
        return evenements
    
    except Exception as e:
        print(f"Erreur lors de l'analyse du fichier ICS: {e}")
        return []

# Chemin de stockage pour les événements personnalisés
CUSTOM_EVENTS_DIR = 'custom_events'
CUSTOM_EVENTS_M1 = os.path.join(CUSTOM_EVENTS_DIR, 'M1_custom_events.json')
CUSTOM_EVENTS_M2 = os.path.join(CUSTOM_EVENTS_DIR, 'M2_custom_events.json')

# S'assurer que le répertoire d'événements personnalisés existe
os.makedirs(CUSTOM_EVENTS_DIR, exist_ok=True)

def load_custom_events(niveau):
    """Charge les événements personnalisés depuis un fichier JSON."""
    file_path = CUSTOM_EVENTS_M1 if niveau == 'm1' else CUSTOM_EVENTS_M2
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []
    except Exception as e:
        print(f"Erreur lors du chargement des événements personnalisés: {e}")
        return []

def save_custom_events(events, niveau):
    """Sauvegarde les événements personnalisés dans un fichier JSON."""
    file_path = CUSTOM_EVENTS_M1 if niveau == 'm1' else CUSTOM_EVENTS_M2
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des événements personnalisés: {e}")
        return False

def sync_custom_events_to_ics():
    """Synchronise les événements personnalisés avec les fichiers ICS."""
    # Créer un fichier JSON au même format que ceux utilisés par les scripts logos_M1.py et logos_M2.py
    m1_events = load_custom_events('m1')
    m2_events = load_custom_events('m2')
    
    # Chemins des fichiers JSON utilisés par les scripts logos_M*.py
    m1_custom_events_json = os.path.join('masters', "M1_LOGOS_custom_events.json")
    m2_custom_events_json = os.path.join('masters', "M2_LOGOS_custom_events.json")
    
    # Convertir les événements dans le format attendu par les scripts logos_M*.py
    m1_events_for_ics = []
    for event in m1_events:
        event_converted = {}
        for key, value in event.items():
            # Convertir les propriétés spéciales
            if key in ['isCustom', 'for_m1', 'for_m2']:
                continue
            if key == 'id':
                event_converted['uid'] = value
            else:
                event_converted[key] = value
        
        # Ajouter les props supplémentaires
        event_converted['for_m1'] = event.get('for_m1', True)
        event_converted['for_m2'] = event.get('for_m2', False)
        
        m1_events_for_ics.append(event_converted)
    
    m2_events_for_ics = []
    for event in m2_events:
        event_converted = {}
        for key, value in event.items():
            # Convertir les propriétés spéciales
            if key in ['isCustom', 'for_m1', 'for_m2']:
                continue
            if key == 'id':
                event_converted['uid'] = value
            else:
                event_converted[key] = value
        
        # Ajouter les props supplémentaires
        event_converted['for_m1'] = event.get('for_m1', False)
        event_converted['for_m2'] = event.get('for_m2', True)
        
        m2_events_for_ics.append(event_converted)
    
    # Sauvegarder les événements au format attendu par les scripts logos_M*.py
    try:
        with open(m1_custom_events_json, 'w', encoding='utf-8') as f:
            json.dump(m1_events_for_ics, f, ensure_ascii=False, indent=4)
        
        with open(m2_custom_events_json, 'w', encoding='utf-8') as f:
            json.dump(m2_events_for_ics, f, ensure_ascii=False, indent=4)
        
        return True
    except Exception as e:
        print(f"Erreur lors de la synchronisation des événements personnalisés: {e}")
        return False

# Nouvelle route pour l'emploi du temps
@app.route('/edt/<niveau>')
def edt(niveau):
    if 'username' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('login'))
    
    users = load_users()
    user = users.get(session['username'])
    account_type = user.get('account_type', 'm1')
    is_admin = user.get('is_admin', False)
    
    if niveau not in ['m1', 'm2']:
        flash('Niveau non valide.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Le titre de la page dépend du niveau sélectionné
    title = f"Emploi du temps M{'1' if niveau == 'm1' else '2'} LOGOS"
    
    # Vérifier les restrictions d'accès (sauf pour les alumni et les profs qui peuvent tout voir)
    if not is_admin and account_type not in ['prof', 'alumni']:
        if account_type == 'm1' and niveau == 'm2':
            flash('Les étudiants M1 ne peuvent pas voir l\'emploi du temps M2.', 'danger')
            return redirect(url_for('edt', niveau='m1'))
        elif account_type == 'm2' and niveau == 'm1':
            flash('Les étudiants M2 ne peuvent pas voir l\'emploi du temps M1.', 'danger')
            return redirect(url_for('edt', niveau='m2'))
    
    return render_template('edt.html', 
                          title=title,
                          niveau=niveau,
                          user=user,
                          is_admin=is_admin,
                          account_type=account_type)

# API pour récupérer les événements de l'emploi du temps
@app.route('/api/events/<niveau>')
def get_events(niveau):
    if 'username' not in session:
        return jsonify({'error': 'Vous devez être connecté pour accéder à ces données.'}), 401
    
    if niveau not in ['m1', 'm2']:
        return jsonify({'error': 'Niveau non valide.'}), 400
    
    # Choisir le bon fichier ICS en fonction du niveau
    chemin_fichier_ics = os.path.join('masters', f"M{'1' if niveau == 'm1' else '2'}_LOGOS.ics")
    
    # Charger les événements du calendrier
    evenements = charger_calendrier(chemin_fichier_ics)
    return jsonify(evenements)

# API pour ajouter un événement personnalisé (admin uniquement)
@app.route('/api/add_custom_event', methods=['POST'])
def add_custom_event():
    if 'username' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Vous n\'avez pas les droits nécessaires.'}), 403
    
    data = request.json
    
    # Validation de base
    if not data.get('title') or not data.get('start') or not data.get('end'):
        return jsonify({'success': False, 'message': 'Informations manquantes.'}), 400
    
    # Déterminer les niveaux affectés
    for_m1 = data.get('for_m1', True)
    for_m2 = data.get('for_m2', True)
    
    # Générer un ID unique
    event_id = f"custom_{datetime.datetime.now().timestamp()}_{data.get('title', '')}"
    
    # Créer l'événement
    event = {
        'id': event_id,
        'title': data.get('title'),
        'start': data.get('start'),
        'end': data.get('end'),
        'description': data.get('description', ''),
        'location': data.get('location', ''),
        'for_m1': for_m1,
        'for_m2': for_m2,
        'isCustom': True
    }
    
    # Ajouter l'événement aux fichiers respectifs
    if for_m1:
        events_m1 = load_custom_events('m1')
        events_m1.append(event)
        save_custom_events(events_m1, 'm1')
    
    if for_m2:
        events_m2 = load_custom_events('m2')
        events_m2.append(event)
        save_custom_events(events_m2, 'm2')
    
    # Synchroniser avec les fichiers ICS
    sync_custom_events_to_ics()
    
    return jsonify({'success': True, 'id': event_id})

# API pour mettre à jour un événement personnalisé (admin uniquement)
@app.route('/api/update_custom_event', methods=['POST'])
def update_custom_event():
    if 'username' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Vous n\'avez pas les droits nécessaires.'}), 403
    
    data = request.json
    event_id = data.get('id')
    
    # Validation de base
    if not event_id or not data.get('title') or not data.get('start') or not data.get('end'):
        return jsonify({'success': False, 'message': 'Informations manquantes.'}), 400
    
    # Déterminer les niveaux affectés
    for_m1 = data.get('for_m1', True)
    for_m2 = data.get('for_m2', True)
    
    # Créer l'événement mis à jour
    updated_event = {
        'id': event_id,
        'title': data.get('title'),
        'start': data.get('start'),
        'end': data.get('end'),
        'description': data.get('description', ''),
        'location': data.get('location', ''),
        'for_m1': for_m1,
        'for_m2': for_m2,
        'isCustom': True
    }
    
    # Mettre à jour l'événement dans les fichiers respectifs
    updated = False
    
    # Mettre à jour dans M1 si nécessaire
    events_m1 = load_custom_events('m1')
    for i, event in enumerate(events_m1):
        if event.get('id') == event_id:
            if for_m1:
                events_m1[i] = updated_event
            else:
                events_m1.pop(i)
            updated = True
            save_custom_events(events_m1, 'm1')
            break
    
    # Mettre à jour dans M2 si nécessaire
    events_m2 = load_custom_events('m2')
    for i, event in enumerate(events_m2):
        if event.get('id') == event_id:
            if for_m2:
                events_m2[i] = updated_event
            else:
                events_m2.pop(i)
            updated = True
            save_custom_events(events_m2, 'm2')
            break
    
    # Ajouter si l'événement n'existait pas déjà
    if not updated:
        if for_m1:
            events_m1.append(updated_event)
            save_custom_events(events_m1, 'm1')
        
        if for_m2:
            events_m2.append(updated_event)
            save_custom_events(events_m2, 'm2')
    
    # Synchroniser avec les fichiers ICS
    sync_custom_events_to_ics()
    
    return jsonify({'success': True})

# API pour supprimer un événement personnalisé (admin uniquement)
@app.route('/api/delete_custom_event', methods=['POST'])
def delete_custom_event():
    if 'username' not in session or not session.get('is_admin', False):
        return jsonify({'success': False, 'message': 'Vous n\'avez pas les droits nécessaires.'}), 403
    
    data = request.json
    event_id = data.get('id')
    
    # Validation de base
    if not event_id:
        return jsonify({'success': False, 'message': 'ID d\'événement manquant.'}), 400
    
    deleted = False
    
    # Supprimer de M1
    events_m1 = load_custom_events('m1')
    for i, event in enumerate(events_m1):
        if event.get('id') == event_id:
            events_m1.pop(i)
            save_custom_events(events_m1, 'm1')
            deleted = True
            break
    
    # Supprimer de M2
    events_m2 = load_custom_events('m2')
    for i, event in enumerate(events_m2):
        if event.get('id') == event_id:
            events_m2.pop(i)
            save_custom_events(events_m2, 'm2')
            deleted = True
            break
    
    if deleted:
        # Synchroniser avec les fichiers ICS
        sync_custom_events_to_ics()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Événement non trouvé.'}), 404

# API pour récupérer tous les événements personnalisés (admin uniquement)
@app.route('/api/custom_events')
def get_all_custom_events():
    if 'username' not in session or not session.get('is_admin', False):
        return jsonify({'error': 'Vous n\'avez pas les droits nécessaires.'}), 403
    
    # Combiner les événements des deux niveaux
    events_m1 = load_custom_events('m1')
    events_m2 = load_custom_events('m2')
    
    # Éliminer les doublons (événements qui existent dans les deux niveaux)
    all_events = {}
    for event in events_m1 + events_m2:
        all_events[event.get('id')] = event
    
    return jsonify(list(all_events.values()))

# API pour récupérer les événements personnalisés pour un niveau spécifique
@app.route('/api/custom_events/<niveau>')
def get_custom_events(niveau):
    if 'username' not in session:
        return jsonify({'error': 'Vous devez être connecté pour accéder à ces données.'}), 401
    
    if niveau not in ['m1', 'm2']:
        return jsonify({'error': 'Niveau non valide.'}), 400
    
    # Charger les événements du niveau spécifié
    events = load_custom_events(niveau)
    
    return jsonify(events)

# Initialisation de l'application
if __name__ == '__main__':
    # Si le fichier users.json n'existe pas, créer un utilisateur par défaut
    if not os.path.exists(USERS_FILE):
        # Initialiser avec un utilisateur par défaut
        USERS = {
            "admin": {
                "username": "admin",
                "password": generate_password_hash("admin"),
                "email": "admin@logos.fr",
                "name": "Administrateur",
                "account_type": "prof",
                "is_admin": True,
                "selected_courses": {
                    "semestre1": [],
                    "semestre2": [],
                    "semestre3": [],
                    "semestre4": []
                }
            },
            "etudiant_m1": {
                "username": "etudiant_m1",
                "password": generate_password_hash("etudiant"),
                "email": "etudiant_m1@logos.fr",
                "name": "Étudiant M1 Test",
                "account_type": "m1",
                "is_admin": False,
                "selected_courses": {
                    "semestre1": [],
                    "semestre2": [],
                    "semestre3": [],
                    "semestre4": []
                }
            },
            "etudiant_m2": {
                "username": "etudiant_m2",
                "password": generate_password_hash("etudiant"),
                "email": "etudiant_m2@logos.fr",
                "name": "Étudiant M2 Test",
                "account_type": "m2",
                "is_admin": False,
                "selected_courses": {
                    "semestre1": [],
                    "semestre2": [],
                    "semestre3": [],
                    "semestre4": []
                }
            }
        }
        save_users()
    else:
        load_users()
    
    # Créer les répertoires s'ils n'existent pas
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(host='0.0.0.0', debug=True, port=5001)