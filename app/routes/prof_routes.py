from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.models import Classe, Prof, Eleve, Note, Matiere, ProfClasse, db

prof_bp = Blueprint('prof', __name__)

@prof_bp.before_request
def check_change_password():
    if 'user_id' in session:
        user = Prof.query.get(session['user_id'])
        if user and user.change_password:
            return redirect(url_for('main.change_password'))

@prof_bp.route('/prof_dashboard', methods=['GET', 'POST'])
def prof_dashboard():
    if 'user_id' not in session or session['user_type'] != 'prof':
        return redirect(url_for('main.login'))
    
    prof_id = session['user_id']
    prof = Prof.query.get(prof_id)
    matiere = Matiere.query.get(prof.id_matiere)
    
    classes = Classe.query.join(ProfClasse).filter(ProfClasse.id_prof == prof_id).all()
    
    notes_par_eleve = {}
    selected_classe = None
    moyenne_generale = 0
    if request.method == 'POST':
        classe_id = request.form['classe']
        selected_classe = Classe.query.get(classe_id)
        eleves = Eleve.query.filter_by(id_classe=classe_id).all()
        
        total_notes = 0
        total_count = 0
        
        for eleve in eleves:
            notes = Note.query.filter_by(id_eleve=eleve.id_eleve, id_matiere=prof.id_matiere).all()
            notes_par_eleve[eleve.nom_eleve] = {
                'eleve_id': eleve.id_eleve,
                'notes': [{'id_note': note.id_note, 'note': note.note} for note in notes],
                'moyenne': sum(note.note for note in notes) / len(notes) if notes else 0
            }
            total_notes += sum(note.note for note in notes)
            total_count += len(notes)
        
        if total_count > 0:
            moyenne_generale = total_notes / total_count
    
    return render_template('teacher.html', username=prof.nom_prof, matiere=matiere.nom_matiere, classes=classes, notes_par_eleve=notes_par_eleve, selected_classe=selected_classe, moyenne_generale=moyenne_generale)

@prof_bp.route('/prof/add_note', methods=['POST'])
def prof_add_note():
    eleve_id = request.form['eleve_id']
    new_note_value = request.form['new_note_value']
    new_note = Note(
        id_eleve=eleve_id,
        id_matiere=session['user_id'],
        note=new_note_value
    )
    db.session.add(new_note)
    db.session.commit()
    flash('Nouvelle note ajoutée avec succès')
    return redirect(url_for('prof.prof_dashboard'))

@prof_bp.route('/prof/edit_note/<int:note_id>', methods=['POST'])
def prof_edit_note(note_id):
    new_note_value = request.form['new_note_value']
    note = Note.query.get(note_id)
    if note:
        note.note = new_note_value
        db.session.commit()
        flash('Note modifiée avec succès')
    return redirect(url_for('prof.prof_dashboard'))

@prof_bp.route('/prof/delete_note/<int:note_id>', methods=['POST'])
def prof_delete_note(note_id):
    note = Note.query.get(note_id)
    if note:
        db.session.delete(note)
        db.session.commit()
        flash('Note supprimée avec succès')
    return redirect(url_for('prof.prof_dashboard'))