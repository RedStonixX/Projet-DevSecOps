from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Définition de la table Admin
class Admin(db.Model):
    __tablename__ = 'admins'
    id_admin = db.Column(db.Integer, primary_key=True)
    encrypted_nom_admin = db.Column(db.String(255), nullable=False)
    hash_password = db.Column(db.String(64), nullable=False)
    change_password = db.Column(db.Boolean, default=True)
    is_super_admin = db.Column(db.Boolean, default=False)

# Définition de la table Classe
class Classe(db.Model):
    __tablename__ = 'classes'
    id_classe = db.Column(db.Integer, primary_key=True)
    nom_classe = db.Column(db.String(50), nullable=False)
    eleves = db.relationship('Eleve', backref='classe', lazy=True)

# Définition de la table Eleve
class Eleve(db.Model):
    __tablename__ = 'eleves'
    id_eleve = db.Column(db.Integer, primary_key=True)
    encrypted_nom_eleve = db.Column(db.String(255), nullable=False)
    id_classe = db.Column(db.Integer, db.ForeignKey('classes.id_classe'))
    hash_password = db.Column(db.String(64), nullable=False)
    change_password = db.Column(db.Boolean, default=True)

# Définition de la table Matiere
class Matiere(db.Model):
    __tablename__ = 'matieres'
    id_matiere = db.Column(db.Integer, primary_key=True)
    nom_matiere = db.Column(db.String(50), nullable=False)

# Définition de la table Note
class Note(db.Model):
    __tablename__ = 'notes'
    id_note = db.Column(db.Integer, primary_key=True)
    id_eleve = db.Column(db.Integer, db.ForeignKey('eleves.id_eleve'))
    id_matiere = db.Column(db.Integer, db.ForeignKey('matieres.id_matiere'))
    note = db.Column(db.Numeric(5, 2))

    eleve = db.relationship('Eleve', backref='notes', lazy=True)
    matiere = db.relationship('Matiere', backref='notes', lazy=True)

# Définition de la table Prof
class Prof(db.Model):
    __tablename__ = 'profs'
    id_prof = db.Column(db.Integer, primary_key=True)
    encrypted_nom_prof = db.Column(db.String(255), nullable=False)
    id_matiere = db.Column(db.Integer, db.ForeignKey('matieres.id_matiere'))
    hash_password = db.Column(db.String(64), nullable=False)
    change_password = db.Column(db.Boolean, default=True)
    
    def has_classes(self):
        return ProfClasse.query.filter_by(id_prof=self.id_prof).count() > 0

# Définition de la table ProfClasse
class ProfClasse(db.Model):
    __tablename__ = 'profclasse'
    id_prof = db.Column(db.Integer, db.ForeignKey('profs.id_prof'), primary_key=True)
    id_classe = db.Column(db.Integer, db.ForeignKey('classes.id_classe'), primary_key=True)

    prof = db.relationship('Prof', backref='classes', lazy=True)
    classe = db.relationship('Classe', backref='profs', lazy=True)
