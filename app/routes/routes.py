from flask import render_template, Blueprint, request, redirect, url_for, flash, session
from app.models.models import Admin, Prof, Eleve, db
from app.encryption import encrypt_username, decrypt_username
import datetime
import hashlib

main = Blueprint('main', __name__)

@main.before_app_request
def refresh_session():
    """Met à jour la session et la supprime après 15 minutes d'inactivité."""
    if 'last_activity' in session:
        last_activity = session.get('last_activity')

        if isinstance(last_activity, str):
            last_activity = datetime.datetime.fromisoformat(last_activity)
        
            if (datetime.datetime.now(datetime.timezone.utc) - last_activity).total_seconds() > 900:
                session.clear()
                return redirect(url_for('main.login'))
    
    session['last_activity'] = datetime.datetime.now(datetime.timezone.utc).isoformat()

def hash_password(password):
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, hashed_password):
    """Vérifie si le mot de passe correspond au hash"""
    return hash_password(password) == hashed_password

@main.route('/')
def home():
    if 'user_type' in session:
        if session['user_type'] == 'prof':
            return redirect(url_for('prof.prof_dashboard'))
        elif session['user_type'] == 'eleve':
            return redirect(url_for('student.student_dashboard'))
        elif session['user_type'] == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        encrypted_username = encrypt_username(username)  # Chiffrer le nom d'utilisateur
        print(f"Nom d'utilisateur saisi: {username}")
        print(f"Nom d'utilisateur chiffré: {encrypted_username}")

        user = Admin.query.filter_by(encrypted_nom_admin=encrypted_username).first() or \
               Prof.query.filter_by(encrypted_nom_prof=encrypted_username).first() or \
               Eleve.query.filter_by(encrypted_nom_eleve=encrypted_username).first()

        if user:
            print(f"Utilisateur trouvé: {user.nom_admin if isinstance(user, Admin) else user.nom_prof if isinstance(user, Prof) else user.nom_eleve}")
        else:
            print("Utilisateur non trouvé")

        if user and check_password(password, user.hash_password):
            if isinstance(user, Prof):
                if not user.has_classes() or user.id_matiere is None:
                    flash('Votre compte n\'est pas encore configuré. Veuillez contacter l\'administrateur.')
                    return redirect(url_for('main.login'))
            elif isinstance(user, Eleve):
                if user.id_classe is None:
                    flash('Votre compte n\'est pas encore configuré. Veuillez contacter l\'administrateur.')

            session['user_id'] = user.id_admin if isinstance(user, Admin) else user.id_prof if isinstance(user, Prof) else user.id_eleve
            session['user_type'] = 'admin' if isinstance(user, Admin) else 'prof' if isinstance(user, Prof) else 'eleve'
            if user.change_password:
                return redirect(url_for('main.change_password'))
            return redirect(url_for('admin.admin_dashboard') if session['user_type'] == 'admin' else url_for('prof.prof_dashboard') if session['user_type'] == 'prof' else url_for('student.student_dashboard'))
        else:
            flash('Identifiant ou mot de passe incorrect.')
    return render_template('login.html')

@main.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        user_id = session['user_id']
        user_type = session['user_type']

        user = Admin.query.get(user_id) if user_type == 'admin' else \
               Prof.query.get(user_id) if user_type == 'prof' else \
               Eleve.query.get(user_id)

        if user:
            user.hash_password = hash_password(new_password)
            user.change_password = False
            db.session.commit()
            flash('Mot de passe changé avec succès.')
            return redirect(url_for('main.login'))

    return render_template('change_password.html')

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))