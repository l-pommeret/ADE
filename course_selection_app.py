import os
import json
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
        return redirect(url_for('dashboard'))
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
            flash('Connexion réussie!', 'success')
            return redirect(url_for('dashboard'))
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
                'selected_courses': {
                    'semestre1': [],
                    'semestre2': [],
                    'semestre3': [],
                    'semestre4': []
                }
            }
            save_users()
            flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
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
                           semester_ects=semester_ects)

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
    
    return render_template('semester.html', 
                           semester_id=semester,
                           semester_data=COURSES[semester],
                           user=user)

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
                "selected_courses": {
                    "semestre1": [],
                    "semestre2": [],
                    "semestre3": [],
                    "semestre4": []
                }
            },
            "etudiant": {
                "username": "etudiant",
                "password": generate_password_hash("etudiant"),
                "email": "etudiant@logos.fr",
                "name": "Étudiant Test",
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
    
    app.run(debug=True, port=5001)