from flask import render_template, Blueprint, request, redirect, url_for, flash, session
from app.models.models import Classe, Admin, Prof, Eleve, Note, Matiere, ProfClasse, db

main = Blueprint('main', __name__)

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
        
        # Check if user is an admin
        admin = Admin.query.filter_by(nom_admin=username, password=password).first()
        if admin:
            session['user_id'] = admin.id_admin
            session['user_type'] = 'admin'
            return redirect(url_for('admin.admin_dashboard'))
        
        # Check if user is a prof
        prof = Prof.query.filter_by(nom_prof=username, password=password).first()
        if prof:
            session['user_id'] = prof.id_prof
            session['user_type'] = 'prof'
            return redirect(url_for('prof.prof_dashboard'))
        
        # Check if user is an eleve
        eleve = Eleve.query.filter_by(nom_eleve=username, password=password).first()
        if eleve:
            session['user_id'] = eleve.id_eleve
            session['user_type'] = 'eleve'
            return redirect(url_for('student.student_dashboard'))
        
        flash('Invalid username or password')
    
    return render_template('login.html')

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))