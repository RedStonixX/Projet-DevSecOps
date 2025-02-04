from flask import Blueprint, render_template, redirect, url_for, session, jsonify
from app.models.models import Classe, Admin, Prof, Eleve, Note, Matiere, ProfClasse

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('main.login'))
    
    if not admin:  # Vérification que l’admin existe bien
        session.clear()  # On supprime la session invalide
        return redirect(url_for('main.login'))

    admin_id = session['user_id']
    admin = Admin.query.get(admin_id)
    profs = Prof.query.all()
    eleves = Eleve.query.all()
    
    return render_template('admin.html', username=admin.nom_admin, profs=profs, eleves=eleves)

@admin_bp.route('/admin/prof_info/<int:prof_id>')
def prof_info(prof_id):
    prof = Prof.query.get(prof_id)
    matiere = Matiere.query.get(prof.id_matiere).nom_matiere
    classes = Classe.query.join(ProfClasse).filter(ProfClasse.id_prof == prof_id).all()
    class_names = [classe.nom_classe for classe in classes]
    
    return jsonify(matiere=matiere, classes=class_names)

@admin_bp.route('/admin/eleve_info/<int:eleve_id>')
def eleve_info(eleve_id):
    eleve = Eleve.query.get(eleve_id)
    classe = Classe.query.get(eleve.id_classe).nom_classe
    notes = Note.query.filter_by(id_eleve=eleve_id).all()
    total_notes = sum(note.note for note in notes)
    moyenne_generale = total_notes / len(notes) if notes else 0
    profs = Prof.query.join(ProfClasse).filter(ProfClasse.id_classe == eleve.id_classe).all()
    prof_info = [{'nom': prof.nom_prof, 'matiere': Matiere.query.get(prof.id_matiere).nom_matiere} for prof in profs]
    
    notes_par_matiere = {}
    for note in notes:
        matiere = Matiere.query.get(note.id_matiere).nom_matiere
        if matiere not in notes_par_matiere:
            notes_par_matiere[matiere] = []
        notes_par_matiere[matiere].append(note.note)
    
    notes_moyennes = {matiere: float(sum(notes) / len(notes)) for matiere, notes in notes_par_matiere.items()}
    
    return jsonify(classe=classe, profs=prof_info, moyenne=float(moyenne_generale), notes=notes_par_matiere, notes_moyennes=notes_moyennes)

@admin_bp.route('/admin/add_note', methods=['POST'])
def admin_add_note():
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/edit_note/<int:note_id>', methods=['POST'])
def admin_edit_note(note_id):
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/delete_note/<int:note_id>', methods=['POST'])
def admin_delete_note(note_id):
    return redirect(url_for('admin.admin_dashboard'))