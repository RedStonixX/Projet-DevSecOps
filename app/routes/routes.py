from flask import render_template, Blueprint, request, redirect, url_for, flash, session
from app.models.models import Admin, Prof, Eleve, db
from app.encryption import encrypt_username
import datetime
import hashlib
import re

main = Blueprint('main', __name__)

LOGIN_URL = 'main.login'

@main.before_app_request
def refresh_session():
    """Met à jour la session et la supprime après 15 minutes d'inactivité."""
    if 'last_activity' in session:
        last_activity = session.get('last_activity')

        if isinstance(last_activity, str):
            last_activity = datetime.datetime.fromisoformat(last_activity)
        
            if (datetime.datetime.now(datetime.timezone.utc) - last_activity).total_seconds() > 900:
                session.clear()
                return redirect(url_for(LOGIN_URL))
    
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
    return redirect(url_for(LOGIN_URL))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        encrypted_username = encrypt_username(username)  # Chiffrer le nom d'utilisateur
        user = find_user_by_encrypted_username(encrypted_username)

        if user and check_password(password, user.hash_password):
            if not is_user_configured(user):
                return redirect(url_for('main.login'))

            set_user_session(user)
            if user.change_password:
                return redirect(url_for('main.change_password'))
            return redirect_user_dashboard()
        else:
            flash('Identifiant ou mot de passe incorrect.')
    return render_template('login.html')

def find_user_by_encrypted_username(encrypted_username):
    user = Admin.query.filter_by(encrypted_nom_admin=encrypted_username).first() or \
           Prof.query.filter_by(encrypted_nom_prof=encrypted_username).first() or \
           Eleve.query.filter_by(encrypted_nom_eleve=encrypted_username).first()
    return user

def is_user_configured(user):
    if isinstance(user, Prof):
        if not user.has_classes() or user.id_matiere is None:
            flash('Votre compte n\'est pas encore configuré. Veuillez contacter l\'administrateur.')
            return False
    elif isinstance(user, Eleve) and user.id_classe is None:
        flash('Votre compte n\'est pas encore configuré. Veuillez contacter l\'administrateur.')
        return False
    return True

def set_user_session(user):
    if isinstance(user, Admin):
        session['user_id'] = user.id_admin
        if user.is_super_admin:
            session['user_type'] = 'superadmin'
        else:
            session['user_type'] = 'admin'
    elif isinstance(user, Prof):
        session['user_id'] = user.id_prof
        session['user_type'] = 'prof'
    else:
        session['user_id'] = user.id_eleve
        session['user_type'] = 'eleve'

def redirect_user_dashboard():
    if session['user_type'] == 'superadmin':
        return redirect(url_for('superadmin.superadmin_dashboard'))
    elif session['user_type'] == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif session['user_type'] == 'prof':
        return redirect(url_for('prof.prof_dashboard'))
    else:
        return redirect(url_for('student.student_dashboard'))

@main.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for(LOGIN_URL))

    if request.method == 'POST':
        new_password = request.form['new_password']
        user_id = session['user_id']
        user_type = session['user_type']

        # Validation du mot de passe
        if not re.match(r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-])(?=.{8,})', new_password):
            flash('Le mot de passe doit contenir au moins 8 caractères, un chiffre, une majuscule et un caractère spécial.', 'danger')
            return redirect(url_for('main.change_password'))

        if user_type == 'admin':
            user = Admin.query.get(user_id)
        elif user_type == 'prof':
            user = Prof.query.get(user_id)
        else:
            user = Eleve.query.get(user_id)

        if user:
            user.hash_password = hash_password(new_password)
            user.change_password = False
            db.session.commit()
            flash('Mot de passe changé avec succès.')
            return redirect(url_for(LOGIN_URL))

    return render_template('change_password.html')

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for(LOGIN_URL))

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404error.html'), 404