from flask import render_template, Blueprint, request, redirect, url_for, flash, session
from app.models.models import Admin, Prof, Eleve
import datetime
import hashlib  # Import pour le hashage SHA-256

main = Blueprint('main', __name__)

@main.before_app_request
def refresh_session():
    """Met à jour la session et la supprime après 15 minutes d'inactivité."""
    if 'last_activity' in session:
        last_activity = session.get('last_activity')

        if isinstance(last_activity, str):  # Vérifier si c'est une chaîne de caractères
            last_activity = datetime.datetime.fromisoformat(last_activity)  # Convertir
        
            # Comparer avec l'heure actuelle (UTC)
            if (datetime.datetime.now(datetime.timezone.utc) - last_activity).total_seconds() > 900:  # 15 minutes
                session.clear()  # Supprime la session si inactif trop longtemps
                return redirect(url_for('main.login'))
    
    # Stocke le timestamp en format ISO pour éviter les erreurs de fuseau horaire
    session['last_activity'] = datetime.datetime.now(datetime.timezone.utc).isoformat()

def hash_password(password):
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

@main.route('/')
def home():
    if 'user-type' in session:
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
        hashed_password = hash_password(password)  # Hash du mot de passe entré

        # Vérification dans la table Admin
        admin = Admin.query.filter_by(nom_admin=username, hash_password=hashed_password).first()
        if admin:
            session['user_id'] = admin.id_admin
            session['user_type'] = 'admin'
            return redirect(url_for('admin.admin_dashboard'))

        # Vérification dans la table Prof
        prof = Prof.query.filter_by(nom_prof=username, hash_password=hashed_password).first()
        if prof:
            session['user_id'] = prof.id_prof
            session['user_type'] = 'prof'
            return redirect(url_for('prof.prof_dashboard'))

        # Vérification dans la table Élève
        eleve = Eleve.query.filter_by(nom_eleve=username, hash_password=hashed_password).first()
        if eleve:
            session['user_id'] = eleve.id_eleve
            session['user_type'] = 'eleve'
            return redirect(url_for('student.student_dashboard'))

        flash('Identifiant ou mot de passe incorrect')

    return render_template('login.html')

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))
