from app import create_app
from app.models.models import Admin, Prof, Eleve, db
from app.encryption import encrypt_username

# Création d'une instance de l'application Flask
app = create_app()

# Exécution des requêtes dans le contexte de l'application Flask
with app.app_context():
    # Récupération des utilisateurs
    admins = Admin.query.all()
    profs = Prof.query.all()
    eleves = Eleve.query.all()

    # Mise à jour des noms chiffrés pour les administrateurs
    for admin in admins:
        admin.encrypted_nom_admin = encrypt_username(admin.nom_admin)

    # Mise à jour des noms chiffrés pour les professeurs
    for prof in profs:
        prof.encrypted_nom_prof = encrypt_username(prof.nom_prof)

    # Mise à jour des noms chiffrés pour les élèves
    for eleve in eleves:
        eleve.encrypted_nom_eleve = encrypt_username(eleve.nom_eleve)

    # Validation des modifications dans la base de données
    db.session.commit()
    print("Données chiffrées et mises à jour avec succès !")