from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models.models import Classe, Admin, Prof, Eleve, Note, Matiere, ProfClasse, db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('main.login'))
    
    admin_id = session['user_id']
    admin = Admin.query.get(admin_id)
    profs = Prof.query.all()
    eleves = Eleve.query.all()
    classes = Classe.query.all()
    matieres = Matiere.query.all()
    
    return render_template('admin.html', username=admin.nom_admin, profs=profs, eleves=eleves, classes=classes, matieres=matieres)

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

@admin_bp.route('/admin/update_eleve_classe', methods=['POST'])
def update_eleve_classe():
    data = request.get_json()
    eleve_id = data.get('eleve_id')
    classe_id = data.get('classe_id')
    
    eleve = Eleve.query.get(eleve_id)
    eleve.id_classe = classe_id
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/admin/edit_note', methods=['POST'])
def edit_note():
    data = request.get_json()
    eleve_id = data.get('eleve_id')
    matiere = data.get('matiere')
    note_index = data.get('note_index')
    new_note = data.get('new_note')
    
    notes = Note.query.filter_by(id_eleve=eleve_id, id_matiere=Matiere.query.filter_by(nom_matiere=matiere).first().id_matiere).all()
    if note_index < len(notes):
        notes[note_index].note = new_note
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@admin_bp.route('/admin/delete_note', methods=['POST'])
def delete_note():
    data = request.get_json()
    eleve_id = data.get('id_eleve')
    matiere = data.get('matiere')
    note_index = data.get('note_index')
    
    notes = Note.query.filter_by(id_eleve=eleve_id, id_matiere=Matiere.query.filter_by(nom_matiere=matiere).first().id_matiere).all()
    if note_index < len(notes):
        db.session.delete(notes[note_index])
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@admin_bp.route('/admin/add_note', methods=['POST'])
def add_note():
    data = request.get_json()
    eleve_id = data.get('eleve_id')
    matiere = data.get('matiere')
    new_note = data.get('new_note')
    
    matiere_id = Matiere.query.filter_by(nom_matiere=matiere).first().id_matiere
    note = Note(id_eleve=eleve_id, id_matiere=matiere_id, note=new_note)
    db.session.add(note)
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/admin/add_classe', methods=['POST'])
def add_classe():
    data = request.get_json()
    nom_classe = data.get('nom_classe')
    
    classe = Classe(nom_classe=nom_classe)
    db.session.add(classe)
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/admin/delete_classe', methods=['POST'])
def delete_classe():
    data = request.get_json()
    classe_id = data.get('id_classe')
    
    # Supprimer la valeur id_classe des élèves
    Eleve.query.filter_by(id_classe=classe_id).update({'id_classe': None})
    
    # Supprimer les lignes de la table ProfClasse
    ProfClasse.query.filter_by(id_classe=classe_id).delete()
    
    # Supprimer la classe
    classe = Classe.query.get(classe_id)
    db.session.delete(classe)
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/admin/delete_eleve', methods=['POST'])
def delete_eleve():
    data = request.get_json()
    eleve_id = data.get('id_eleve')
    
    # Supprimer les lignes de la table Notes
    Note.query.filter_by(id_eleve=eleve_id).delete()
    
    # Supprimer l'élève
    eleve = Eleve.query.get(eleve_id)
    db.session.delete(eleve)
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/admin/add_matiere', methods=['POST'])
def add_matiere():
    data = request.get_json()
    nom_matiere = data.get('nom_matiere')
    
    matiere = Matiere(nom_matiere=nom_matiere)
    db.session.add(matiere)
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/admin/delete_matiere', methods=['POST'])
def delete_matiere():
    data = request.get_json()
    matiere_id = data.get('id_matiere')
    
    # Supprimer les lignes de la table Notes
    Note.query.filter_by(id_matiere=matiere_id).delete()
    
    # Supprimer la valeur id_matiere des profs
    Prof.query.filter_by(id_matiere=matiere_id).update({'id_matiere': None})
    
    # Supprimer la matière
    matiere = Matiere.query.get(matiere_id)
    db.session.delete(matiere)
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/admin/update_prof_matiere', methods=['POST'])
def update_prof_matiere():
    data = request.get_json()
    prof_id = data.get('prof_id')
    matiere_id = data.get('matiere_id')
    
    prof = Prof.query.get(prof_id)
    prof.id_matiere = matiere_id
    db.session.commit()
    
    return jsonify({'success': True})

