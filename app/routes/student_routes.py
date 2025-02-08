from flask import Blueprint, render_template, redirect, url_for, session
from app.models.models import Classe, Eleve, Note, Matiere, Prof
from app.encryption import encrypt_username, decrypt_username

student_bp = Blueprint('student', __name__)

@student_bp.before_request
def check_change_password():
    if 'user_id' in session:
        user = Eleve.query.get(session['user_id'])
        if user and user.change_password:
            return redirect(url_for('main.change_password'))

@student_bp.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session or session['user_type'] != 'eleve':
        return redirect(url_for('main.login'))
    
    eleve_id = session['user_id']
    eleve = Eleve.query.get(eleve_id)
    classe = Classe.query.get(eleve.id_classe)
    notes = Note.query.filter_by(id_eleve=eleve_id).all()
    notes_par_matiere = {}
    
    total_notes = 0
    total_count = 0
    
    for note in notes:
        matiere = Matiere.query.get(note.id_matiere)
        prof = Prof.query.filter_by(id_matiere=matiere.id_matiere).first()
        if matiere.nom_matiere not in notes_par_matiere:
            notes_par_matiere[matiere.nom_matiere] = {
                'prof': decrypt_username(prof.encrypted_nom_prof) if prof else 'N/A',  # Déchiffrer le nom du professeur
                'notes': [],
                'moyenne': 0
            }
        notes_par_matiere[matiere.nom_matiere]['notes'].append(note.note)
        total_notes += note.note
        total_count += 1
    
    moyenne_generale = total_notes / total_count if total_count > 0 else 0
    
    for matiere, details in notes_par_matiere.items():
        details['moyenne'] = sum(details['notes']) / len(details['notes'])
    
    # Calculate class average
    class_notes = Note.query.join(Eleve).filter(Eleve.id_classe == eleve.id_classe).all()
    total_class_notes = sum(note.note for note in class_notes)
    total_class_count = len(class_notes)
    moyenne_classe = total_class_notes / total_class_count if total_class_count > 0 else 0
    
    return render_template('student.html', username=decrypt_username(eleve.encrypted_nom_eleve), classe=classe.nom_classe, moyenne_generale=moyenne_generale, moyenne_classe=moyenne_classe, notes_par_matiere=notes_par_matiere)