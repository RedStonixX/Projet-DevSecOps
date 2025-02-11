from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = 'admins'
    id_admin = db.Column(db.Integer, primary_key=True)
    encrypted_nom_admin = db.Column(db.String(255), nullable=False)
    hash_password = db.Column(db.String(64), nullable=False)
    change_password = db.Column(db.Boolean, default=True)
    is_super_admin = db.Column(db.Boolean, default=False)

class Classe(db.Model):
    __tablename__ = 'classes'
    id_classe = db.Column(db.Integer, primary_key=True)
    nom_classe = db.Column(db.String(50), nullable=False)
    eleves = db.relationship('Eleve', backref='classe', lazy=True)

class Eleve(db.Model):
    __tablename__ = 'eleves'
    id_eleve = db.Column(db.Integer, primary_key=True)
    encrypted_nom_eleve = db.Column(db.String(255), nullable=False)
    id_classe = db.Column(db.Integer, db.ForeignKey('classes.id_classe'))
    hash_password = db.Column(db.String(64), nullable=False)
    change_password = db.Column(db.Boolean, default=True)

class Matiere(db.Model):
    __tablename__ = 'matieres'
    id_matiere = db.Column(db.Integer, primary_key=True)
    nom_matiere = db.Column(db.String(50), nullable=False)

class Note(db.Model):
    __tablename__ = 'notes'
    id_note = db.Column(db.Integer, primary_key=True)
    id_eleve = db.Column(db.Integer, db.ForeignKey('eleves.id_eleve'))
    id_matiere = db.Column(db.Integer, db.ForeignKey('matieres.id_matiere'))
    note = db.Column(db.Numeric(5, 2))

    eleve = db.relationship('Eleve', backref='notes', lazy=True)
    matiere = db.relationship('Matiere', backref='notes', lazy=True)

class Prof(db.Model):
    __tablename__ = 'profs'
    id_prof = db.Column(db.Integer, primary_key=True)
    encrypted_nom_prof = db.Column(db.String(255), nullable=False)
    id_matiere = db.Column(db.Integer, db.ForeignKey('matieres.id_matiere'))
    hash_password = db.Column(db.String(64), nullable=False)
    change_password = db.Column(db.Boolean, default=True)
    
    def has_classes(self):
        return ProfClasse.query.filter_by(id_prof=self.id_prof).count() > 0

class ProfClasse(db.Model):
    __tablename__ = 'profclasse'
    id_prof = db.Column(db.Integer, db.ForeignKey('profs.id_prof'), primary_key=True)
    id_classe = db.Column(db.Integer, db.ForeignKey('classes.id_classe'), primary_key=True)

    prof = db.relationship('Prof', backref='classes', lazy=True)
    classe = db.relationship('Classe', backref='profs', lazy=True)
