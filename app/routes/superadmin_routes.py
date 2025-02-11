import random
import string
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from app.models.models import Admin, db
from app.routes.routes import hash_password
from app.encryption import encrypt_username

superadmin_bp = Blueprint('superadmin', __name__)

# Vérifier si l'utilisateur est connecté et est un superadmin
@superadmin_bp.before_request
def check_superadmin():
    if 'user_id' not in session or session.get('user_type') != 'superadmin':
        return redirect(url_for('main.login'))

# Route pour la page d'accueil du superadmin
@superadmin_bp.route('/superadmin_dashboard')
def superadmin_dashboard():
    admins = Admin.query.filter_by(is_super_admin=False).all()
    return render_template('superadmin.html', admins=admins)

# Route pour la suppression d'un administrateur
@superadmin_bp.route('/superadmin/delete_admin/<int:admin_id>', methods=['DELETE'])
def delete_admin(admin_id):
    admin = Admin.query.get(admin_id)
    if admin:
        db.session.delete(admin)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

# Route pour l'ajout d'un administrateur
@superadmin_bp.route('/superadmin/add_admin', methods=['POST'])
def add_admin():
    data = request.get_json()
    nom_admin = data.get('nom_admin')
    if nom_admin:
        # Vérifier si un administrateur avec le même nom existe déjà
        if Admin.query.filter_by(nom_admin=nom_admin).first():
            return jsonify({'success': False, 'message': 'Le nom de l\'administrateur existe déjà.'})
        
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        hashed_password = hash_password(password)
        encrypted_nom_admin = encrypt_username(nom_admin)
        new_admin = Admin(nom_admin=nom_admin, encrypted_nom_admin=encrypted_nom_admin, hash_password=hashed_password, change_password=True)
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({'success': True, 'password': password})
    return jsonify({'success': False, 'message': 'Le nom de l\'administrateur est requis.'})