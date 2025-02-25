from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models.models import Classe, Admin, Prof, Eleve, Note, Matiere, ProfClasse, db
from app.routes.routes import hash_password
from app.encryption import encrypt_username, decrypt_username
import string
import random

admin_bp = Blueprint('admin', __name__)

# Vérifier si l'utilisateur est connecté et est un administrateur
@admin_bp.before_request
def check_change_password():
    if 'user_id' in session:
        user = Admin.query.get(session['user_id'])
        if user and user.change_password:
            return redirect(url_for('main.change_password'))

# Route pour la page d'accueil de l'administrateur
@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('main.login'))
    
    admin_id = session['user_id']
    admin = Admin.query.get(admin_id)
    admins = Admin.query.all()
    profs = Prof.query.all()
    eleves = Eleve.query.all()
    classes = Classe.query.all()
    matieres = Matiere.query.all()

    alert_messages = []
    for eleve in eleves:
        if eleve.id_classe is None:
            alert_messages.append(f'Élève sans classe : {decrypt_username(eleve.encrypted_nom_eleve)}')
    for prof in profs:
        if not prof.has_classes() or prof.id_matiere is None:
            alert_messages.append(f'Professeur sans classe ou matière : {decrypt_username(prof.encrypted_nom_prof)}')
    for user in admins + profs + eleves:
        if user.change_password:
            if user in admins:
                decrypted_name = decrypt_username(user.encrypted_nom_admin)
            elif user in profs:
                decrypted_name = decrypt_username(user.encrypted_nom_prof)
            else:
                decrypted_name = decrypt_username(user.encrypted_nom_eleve)
            alert_messages.append(f'Utilisateur doit changer son mot de passe : {decrypted_name}')
    
    return render_template('admin.html', username=decrypt_username(admin.encrypted_nom_admin), admins=admins, profs=profs, eleves=eleves, classes=classes, matieres=matieres, alert_messages=alert_messages)

# Route pour afficher les informations d'un professeur
@admin_bp.route('/admin/prof_info/<int:prof_id>')
def prof_info(prof_id):
    prof = Prof.query.get(prof_id)
    matiere = Matiere.query.get(prof.id_matiere).nom_matiere if prof.id_matiere else None
    classes = Classe.query.join(ProfClasse).filter(ProfClasse.id_prof == prof_id).all()
    class_names = [classe.nom_classe for classe in classes]
    all_classes = [classe.nom_classe for classe in Classe.query.all()]
    
    return jsonify(matiere=matiere, classes=class_names, all_classes=all_classes)

# Route pour afficher les informations d'un élève
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

# Route pour mettre à jour la classe d'un élève
@admin_bp.route('/admin/update_eleve_classe', methods=['POST'])
def update_eleve_classe():
    data = request.get_json()
    eleve_id = data.get('eleve_id')
    classe_id = data.get('classe_id')
    
    eleve = Eleve.query.get(eleve_id)
    eleve.id_classe = classe_id
    db.session.commit()
    
    return jsonify({'success': True})

# Route pour mettre à jour la note d'un élève
@admin_bp.route('/admin/edit_note', methods=['POST'])
def edit_note():
    data = request.get_json()
    eleve_id = data.get('eleve_id')
    matiere = data.get('matiere')
    note_index = data.get('note_index')
    new_note = data.get('new_note')
    
    try:
        new_note = float(new_note)
        if new_note < 0 or new_note > 20:
            raise ValueError("La note doit être comprise entre 0 et 20.")
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    
    notes = Note.query.filter_by(id_eleve=eleve_id, id_matiere=Matiere.query.filter_by(nom_matiere=matiere).first().id_matiere).all()
    if note_index < len(notes):
        notes[note_index].note = new_note
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

# Route pour supprimer une note
@admin_bp.route('/admin/delete_note', methods=['POST'])
def delete_note():
    data = request.get_json()
    eleve_id = data.get('eleve_id')
    matiere = data.get('matiere')
    note_index = data.get('note_index')
    
    matiere_id = Matiere.query.filter_by(nom_matiere=matiere).first().id_matiere
    notes = Note.query.filter_by(id_eleve=eleve_id, id_matiere=matiere_id).all()
    
    if note_index < len(notes):
        db.session.delete(notes[note_index])
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Note non trouvée ou index invalide'}), 404

# Route pour ajouter une note
@admin_bp.route('/admin/add_note', methods=['POST'])
def add_note():
    data = request.get_json()
    eleve_id = data.get('eleve_id')
    matiere = data.get('matiere')
    new_note = data.get('new_note')
    
    try:
        new_note = float(new_note)
        if new_note < 0 or new_note > 20:
            raise ValueError("La note doit être comprise entre 0 et 20.")
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    
    matiere_id = Matiere.query.filter_by(nom_matiere=matiere).first().id_matiere
    note = Note(id_eleve=eleve_id, id_matiere=matiere_id, note=new_note)
    db.session.add(note)
    db.session.commit()
    
    return jsonify({'success': True})

# Route pour ajouter une classe
@admin_bp.route('/admin/add_classe', methods=['POST'])
def add_classe():
    data = request.get_json()
    nom_classe = data.get('nom_classe')

    if Classe.query.filter_by(nom_classe=nom_classe).first():
        return jsonify({'success': False, 'message': 'Le nom de la classe existe déjà.'}), 400

    classe = Classe(nom_classe=nom_classe)
    db.session.add(classe)
    db.session.commit()

    return jsonify({'success': True})

# Route pour supprimer une classe
@admin_bp.route('/admin/delete_classe', methods=['POST'])
def delete_classe():
    data = request.get_json()
    classe_id = data.get('id_classe')
    
    Eleve.query.filter_by(id_classe=classe_id).update({'id_classe': None})
    
    ProfClasse.query.filter_by(id_classe=classe_id).delete()
    
    classe = Classe.query.get(classe_id)
    db.session.delete(classe)
    db.session.commit()
    
    return jsonify({'success': True})

# Route pour supprimer un élève
@admin_bp.route('/admin/delete_eleve', methods=['POST'])
def delete_eleve():
    data = request.get_json()
    eleve_id = data.get('id_eleve')
    
    Note.query.filter_by(id_eleve=eleve_id).delete()
    
    eleve = Eleve.query.get(eleve_id)
    db.session.delete(eleve)
    db.session.commit()
    
    return jsonify({'success': True})

# Route pour ajouter une matière
@admin_bp.route('/admin/add_matiere', methods=['POST'])
def add_matiere():
    data = request.get_json()
    nom_matiere = data.get('nom_matiere')

    if Matiere.query.filter_by(nom_matiere=nom_matiere).first():
        return jsonify({'success': False, 'message': 'Le nom de la matière existe déjà.'}), 400

    matiere = Matiere(nom_matiere=nom_matiere)
    db.session.add(matiere)
    db.session.commit()

    return jsonify({'success': True})

# Route pour supprimer une matière
@admin_bp.route('/admin/delete_matiere', methods=['POST'])
def delete_matiere():
    data = request.get_json()
    matiere_id = data.get('id_matiere')
    
    Note.query.filter_by(id_matiere=matiere_id).delete()
    
    Prof.query.filter_by(id_matiere=matiere_id).update({'id_matiere': None})
    
    matiere = Matiere.query.get(matiere_id)
    db.session.delete(matiere)
    db.session.commit()
    
    return jsonify({'success': True})

# Route pour mettre à jour la matière d'un professeur
@admin_bp.route('/admin/update_prof_matiere', methods=['POST'])
def update_prof_matiere():
    data = request.get_json()
    prof_id = data.get('prof_id')
    matiere_id = data.get('matiere_id')
    
    prof = Prof.query.get(prof_id)
    prof.id_matiere = matiere_id
    db.session.commit()
    
    return jsonify({'success': True})

# Route pour supprimer une classe d'un professeur
@admin_bp.route('/admin/remove_class_from_prof', methods=['POST'])
def remove_class_from_prof():
    data = request.get_json()
    prof_id = data.get('prof_id')
    class_name = data.get('class_name')
    
    classe = Classe.query.filter_by(nom_classe=class_name).first()
    ProfClasse.query.filter_by(id_prof=prof_id, id_classe=classe.id_classe).delete()
    db.session.commit()
    
    return jsonify({'success': True})

# Route pour ajouter une classe à un professeur
@admin_bp.route('/admin/add_class_to_prof', methods=['POST'])
def add_class_to_prof():
    data = request.get_json()
    prof_id = data.get('prof_id')
    class_name = data.get('class_name')
    
    classe = Classe.query.filter_by(nom_classe=class_name).first()
    prof_classe = ProfClasse(id_prof=prof_id, id_classe=classe.id_classe)
    db.session.add(prof_classe)
    db.session.commit()
    
    return jsonify({'success': True})

# Route pour afficher les informations d'une classe
@admin_bp.route('/admin/classe_info/<int:classe_id>')
def classe_info(classe_id):
    profs = Prof.query.join(ProfClasse).filter(ProfClasse.id_classe == classe_id).all()
    notes = Note.query.join(Eleve).filter(Eleve.id_classe == classe_id).all()

    prof_info = [{'nom': prof.nom_prof, 'matiere': Matiere.query.get(prof.id_matiere).nom_matiere} for prof in profs]

    notes_par_matiere = {}
    for note in notes:
        matiere = Matiere.query.get(note.id_matiere).nom_matiere
        if matiere not in notes_par_matiere:
            notes_par_matiere[matiere] = []
        notes_par_matiere[matiere].append(note.note)

    moyennes_matieres = {matiere: float(sum(notes)) / len(notes) for matiere, notes in notes_par_matiere.items()}
    moyenne_generale = float(sum(sum(notes) for notes in notes_par_matiere.values())) / sum(len(notes) for notes in notes_par_matiere.values())

    return jsonify(profs=prof_info, moyennes_matieres=moyennes_matieres, moyenne_generale=moyenne_generale)

# Route pour supprimer un professeur
@admin_bp.route('/admin/delete_prof', methods=['POST'])
def delete_prof():
    data = request.get_json()
    prof_id = data.get('prof_id')
    
    prof = Prof.query.get(prof_id)
    if prof:
        ProfClasse.query.filter_by(id_prof=prof_id).delete()
        db.session.delete(prof)
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Professeur non trouvé'}), 404

# Route pour créer un professeur
@admin_bp.route('/admin/create_prof', methods=['POST'])
def create_prof():
    data = request.get_json()
    nom_prof = data.get('nom_prof')
    
    if Prof.query.filter_by(nom_prof=nom_prof).first():
        return jsonify({'success': False, 'message': 'Le nom du professeur existe déjà.'}), 400
    
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    hashed_password = hash_password(password)
    encrypted_nom_prof = encrypt_username(nom_prof)  # Chiffrer le nom d'utilisateur
    
    new_prof = Prof(nom_prof=nom_prof, encrypted_nom_prof=encrypted_nom_prof, hash_password=hashed_password, change_password=True)
    db.session.add(new_prof)
    db.session.commit()
    
    return jsonify({'success': True, 'password': password})

# Route pour créer un élève
@admin_bp.route('/admin/create_eleve', methods=['POST'])
def create_eleve():
    data = request.get_json()
    nom_eleve = data.get('nom_eleve')
    
    if Eleve.query.filter_by(nom_eleve=nom_eleve).first():
        return jsonify({'success': False, 'message': 'Le nom de l\'élève existe déjà.'}), 400
    
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    hashed_password = hash_password(password)
    encrypted_nom_eleve = encrypt_username(nom_eleve)  # Chiffrer le nom d'utilisateur
    
    new_eleve = Eleve(nom_eleve=nom_eleve, encrypted_nom_eleve=encrypted_nom_eleve, hash_password=hashed_password, change_password=True)
    db.session.add(new_eleve)
    db.session.commit()
    
    return jsonify({'success': True, 'password': password})

# Route pour réinitialiser le mot de passe d'un élève
@admin_bp.route('/admin/reset_eleve_password', methods=['POST'])
def reset_eleve_password():
    data = request.get_json()
    eleve_id = data.get('eleve_id')
    
    eleve = Eleve.query.get(eleve_id)
    if eleve:
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        hashed_password = hash_password(password)
        eleve.hash_password = hashed_password
        eleve.change_password = True
        db.session.commit()
        return jsonify({'success': True, 'password': password})
    else:
        return jsonify({'success': False, 'message': 'Élève non trouvé'}), 404

# Route pour réinitialiser le mot de passe d'un professeur
@admin_bp.route('/admin/reset_prof_password', methods=['POST'])
def reset_prof_password():
    data = request.get_json()
    prof_id = data.get('prof_id')
    
    prof = Prof.query.get(prof_id)
    if prof:
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        hashed_password = hash_password(password)
        prof.hash_password = hashed_password
        prof.change_password = True
        db.session.commit()
        return jsonify({'success': True, 'password': password})
    else:
        return jsonify({'success': False, 'message': 'Professeur non trouvé'}), 404

# Route pour vérifier la disponibilité d'une matière pour un professeur
@admin_bp.route('/admin/check_matiere_availability/<int:matiere_id>/<int:prof_id>', methods=['GET'])
def check_matiere_availability(matiere_id, prof_id):
    other_prof = Prof.query.filter(Prof.id_prof != prof_id, Prof.id_matiere == matiere_id).first()
    if other_prof:
        return jsonify({'available': False})
    return jsonify({'available': True})