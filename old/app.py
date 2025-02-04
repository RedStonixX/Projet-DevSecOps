from flask import Flask, jsonify, render_template, redirect, url_for, request, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'secret_key'

db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'ent'
}

@app.route('/')
def home():
    if 'user_type' in session:
        if session['user_type'] == 'teacher':
            return redirect(url_for('teachers'))
        elif session['user_type'] == 'student':
            return redirect(url_for('students'))
        elif session['user_type'] == 'admin':
            return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Vérifier si l'utilisateur est un administrateur
        cursor.execute("SELECT * FROM Admins WHERE nom_admin = %s AND password = %s", (username, password))
        admin = cursor.fetchone()

        if admin:
            session['user_type'] = 'admin'
            session['username'] = username
            return jsonify({'status': 'success', 'redirect_url': url_for('admin')})

        # Vérifier si l'utilisateur est un professeur
        cursor.execute("SELECT * FROM Profs WHERE nom_prof = %s", (username,))
        prof = cursor.fetchone()

        if prof:
            if prof['password'] == 'null':
                return jsonify({'status': 'password_null', 'user_type': 'prof', 'user_id': prof['id_prof']})
            elif prof['password'] == password:
                session['user_type'] = 'teacher'
                session['username'] = username
                return jsonify({'status': 'success', 'redirect_url': url_for('teachers')})

        # Vérifier si l'utilisateur est un élève
        cursor.execute("SELECT * FROM Eleves WHERE nom_eleve = %s", (username,))
        eleve = cursor.fetchone()

        if eleve:
            if eleve['password'] == 'null':
                return jsonify({'status': 'password_null', 'user_type': 'eleve', 'user_id': eleve['id_eleve']})
            elif eleve['password'] == password:
                session['user_type'] = 'student'
                session['username'] = username
                return jsonify({'status': 'success', 'redirect_url': url_for('students')})

        cursor.close()
        conn.close()

        flash('Utilisateur ou mot de passe incorrect')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/set_password', methods=['POST'])
def set_password():
    user_type = request.form['user_type']
    user_id = request.form['user_id']
    new_password = request.form['new_password']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if user_type == 'eleve':
        cursor.execute("UPDATE Eleves SET password = %s WHERE id_eleve = %s", (new_password, user_id))
    elif user_type == 'prof':
        cursor.execute("UPDATE Profs SET password = %s WHERE id_prof = %s", (new_password, user_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'status': 'success'})

@app.route('/students')
def students():
    if 'user_type' in session and session['user_type'] == 'student':
        username = session['username']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer les informations de l'élève et sa classe
        cursor.execute("""
            SELECT Eleves.nom_eleve, Classes.nom_classe, Eleves.id_classe 
            FROM Eleves 
            JOIN Classes ON Eleves.id_classe = Classes.id_classe 
            WHERE Eleves.nom_eleve = %s
        """, (username,))
        eleve = cursor.fetchone()
        
        # Récupérer les notes de l'élève et le nom du professeur pour chaque matière
        cursor.execute("""
            SELECT Matieres.nom_matiere, Notes.note, Profs.nom_prof 
            FROM Notes 
            JOIN Matieres ON Notes.id_matiere = Matieres.id_matiere 
            JOIN Profs ON Matieres.id_matiere = Profs.id_matiere 
            WHERE Notes.id_eleve = (SELECT id_eleve FROM Eleves WHERE nom_eleve = %s)
        """, (username,))
        notes = cursor.fetchall()
        
        # Organiser les notes par matière et calculer la moyenne pour chaque matière
        notes_par_matiere = {}
        for note in notes:
            matiere = note['nom_matiere']
            if matiere not in notes_par_matiere:
                notes_par_matiere[matiere] = {
                    'prof': note['nom_prof'],
                    'notes': [],
                    'moyenne': 0
                }
            notes_par_matiere[matiere]['notes'].append(note['note'])
        
        # Calculer la moyenne des notes pour chaque matière
        for matiere, details in notes_par_matiere.items():
            details['moyenne'] = sum(details['notes']) / len(details['notes'])
        
        # Calculer la moyenne des notes de l'élève
        cursor.execute("""
            SELECT AVG(Notes.note) as moyenne_eleve 
            FROM Notes 
            WHERE Notes.id_eleve = (SELECT id_eleve FROM Eleves WHERE nom_eleve = %s)
        """, (username,))
        moyenne_eleve = cursor.fetchone()['moyenne_eleve']
        
        # Calculer la moyenne des notes de la classe
        cursor.execute("""
            SELECT AVG(Notes.note) as moyenne_classe 
            FROM Notes 
            JOIN Eleves ON Notes.id_eleve = Eleves.id_eleve 
            WHERE Eleves.id_classe = %s
        """, (eleve['id_classe'],))
        moyenne_classe = cursor.fetchone()['moyenne_classe']
        
        cursor.close()
        conn.close()
        
        if eleve:
            return render_template('students.html', username=eleve['nom_eleve'], classe=eleve['nom_classe'], notes_par_matiere=notes_par_matiere, moyenne_eleve=moyenne_eleve, moyenne_classe=moyenne_classe)
    return redirect(url_for('login'))

@app.route('/teachers')
def teachers():
    if 'user_type' in session and session['user_type'] == 'teacher':
        username = session['username']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer les informations du professeur et sa matière
        cursor.execute("""
            SELECT Profs.nom_prof, Matieres.nom_matiere, Profs.id_prof 
            FROM Profs 
            JOIN Matieres ON Profs.id_matiere = Matieres.id_matiere 
            WHERE Profs.nom_prof = %s
        """, (username,))
        prof = cursor.fetchone()
        
        # Récupérer les classes enseignées par le professeur
        cursor.execute("""
            SELECT Classes.id_classe, Classes.nom_classe 
            FROM Classes 
            JOIN ProfClasse ON Classes.id_classe = ProfClasse.id_classe 
            WHERE ProfClasse.id_prof = %s
        """, (prof['id_prof'],))
        classes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if prof:
            return render_template('teachers.html', username=prof['nom_prof'], matiere=prof['nom_matiere'], classes=classes)
    return redirect(url_for('login'))

@app.route('/get_eleves/<int:id_classe>', methods=['GET'])
def get_eleves(id_classe):
    if 'user_type' in session and session['user_type'] == 'teacher':
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer les élèves de la classe sélectionnée
        cursor.execute("""
            SELECT Eleves.id_eleve, Eleves.nom_eleve 
            FROM Eleves 
            WHERE Eleves.id_classe = %s
        """, (id_classe,))
        eleves = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(eleves)
    return redirect(url_for('login'))

@app.route('/get_notes/<int:id_eleve>', methods=['GET'])
def get_notes_eleve(id_eleve):
    if 'user_type' in session and session['user_type'] == 'admin':
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT m.nom_matiere, n.note
            FROM Notes n
            LEFT JOIN Matieres m ON n.id_matiere = m.id_matiere
            WHERE n.id_eleve = %s
        """, (id_eleve,))
        notes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Regrouper les notes par matière
        notes_par_matiere = {}
        for note in notes:
            matiere = note['nom_matiere']
            if matiere not in notes_par_matiere:
                notes_par_matiere[matiere] = []
            notes_par_matiere[matiere].append(note['note'])
        
        return jsonify(notes=notes_par_matiere)
    return redirect(url_for('login'))

@app.route('/get_notes/<int:id_classe>', methods=['GET'])
def get_notes_classe(id_classe):
    if 'user_type' in session and session['user_type'] == 'teacher':
        username = session['username']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer l'id de la matière enseignée par le professeur
        cursor.execute("""
            SELECT id_matiere 
            FROM Profs 
            WHERE nom_prof = %s
        """, (username,))
        id_matiere = cursor.fetchone()['id_matiere']
        
        # Récupérer les notes des élèves de la classe sélectionnée pour la matière du professeur
        cursor.execute("""
            SELECT Eleves.nom_eleve, Notes.note 
            FROM Notes 
            JOIN Eleves ON Notes.id_eleve = Eleves.id_eleve 
            WHERE Notes.id_matiere = %s AND Eleves.id_classe = %s
        """, (id_matiere, id_classe))
        notes = cursor.fetchall()
        
        # Organiser les notes par élève
        notes_par_eleve = {}
        for note in notes:
            eleve = note['nom_eleve']
            if eleve not in notes_par_eleve:
                notes_par_eleve[eleve] = []
            notes_par_eleve[eleve].append(note['note'])
        
        cursor.close()
        conn.close()
        
        return jsonify(notes_par_eleve)
    return redirect(url_for('login'))

@app.route('/add_note', methods=['POST'])
def add_note():
    if 'user_type' in session and session['user_type'] == 'teacher':
        username = session['username']
        eleve_id = request.form['eleve']
        note = request.form['note']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Récupérer l'id de la matière enseignée par le professeur
        cursor.execute("""
            SELECT id_matiere 
            FROM Profs 
            WHERE nom_prof = %s
        """, (username,))
        id_matiere = cursor.fetchone()[0]
        
        # Ajouter la note pour l'élève dans la matière du professeur
        cursor.execute("""
            INSERT INTO Notes (id_eleve, id_matiere, note) 
            VALUES (%s, %s, %s)
        """, (eleve_id, id_matiere, note))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Note ajoutée avec succès')
        return redirect(url_for('teachers'))
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if 'user_type' in session and session['user_type'] == 'admin':
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT e.id_eleve, e.nom_eleve, c.nom_classe, 
            GROUP_CONCAT(DISTINCT p.nom_prof) as professeurs, 
            ROUND(AVG(n.note), 2) as moyenne 
            FROM Eleves e
            LEFT JOIN Classes c ON e.id_classe = c.id_classe
            LEFT JOIN ProfClasse pc ON c.id_classe = pc.id_classe
            LEFT JOIN Profs p ON pc.id_prof = p.id_prof
            LEFT JOIN Notes n ON n.id_eleve = e.id_eleve
            GROUP BY e.id_eleve
        """)
        eleves = cursor.fetchall()

        cursor.execute("SELECT id_eleve, nom_eleve, id_classe FROM Eleves")
        eleves_base = cursor.fetchall()
        
        cursor.execute("SELECT id_matiere, nom_matiere FROM Matieres")
        matieres = cursor.fetchall()
        
        cursor.execute("SELECT id_classe, nom_classe FROM Classes")
        classes = cursor.fetchall()
        
        cursor.execute("""
            SELECT p.id_prof, p.nom_prof, p.id_matiere, m.nom_matiere, 
            GROUP_CONCAT(c.nom_classe) as classes 
            FROM Profs p
            LEFT JOIN ProfClasse pc ON p.id_prof = pc.id_prof
            LEFT JOIN Classes c ON pc.id_classe = c.id_classe
            LEFT JOIN Matieres m ON p.id_matiere = m.id_matiere
            GROUP BY p.id_prof
        """)
        profs = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin.html', eleves=eleves, matieres=matieres, classes=classes, profs=profs, eleves_base=eleves_base)
    return redirect(url_for('login'))

@app.route('/get_prof_info/<int:id_prof>', methods=['GET'])
def get_prof_info(id_prof):
    if 'user_type' in session and session['user_type'] == 'admin':
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer les classes et la matière du professeur sélectionné
        cursor.execute("""
            SELECT Classes.nom_classe, Matieres.nom_matiere 
            FROM Profs 
            JOIN ProfClasse ON Profs.id_prof = ProfClasse.id_prof 
            JOIN Classes ON ProfClasse.id_classe = Classes.id_classe 
            JOIN Matieres ON Profs.id_matiere = Matieres.id_matiere 
            WHERE Profs.id_prof = %s
        """, (id_prof,))
        prof_info = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(prof_info)
    return redirect(url_for('login'))

@app.route('/get_classe_info/<int:classe_id>', methods=['GET'])
def get_classe_info(classe_id):
    if 'user_type' in session and session['user_type'] == 'admin':
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.nom_classe, 
                   GROUP_CONCAT(DISTINCT e.nom_eleve) as eleves, 
                   GROUP_CONCAT(DISTINCT p.nom_prof) as professeurs, 
                   ROUND(AVG(n.note), 2) as moyenne 
            FROM Classes c
            LEFT JOIN Eleves e ON c.id_classe = e.id_classe
            LEFT JOIN ProfClasse pc ON c.id_classe = pc.id_classe
            LEFT JOIN Profs p ON pc.id_prof = p.id_prof
            LEFT JOIN Notes n ON e.id_eleve = n.id_eleve
            WHERE c.id_classe = %s
            GROUP BY c.id_classe
        """, (classe_id,))
        classe_info = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify(classe_info)
    return redirect(url_for('login'))

@app.route('/get_eleve_details/<int:eleve_id>', methods=['GET'])
def get_eleve_details(eleve_id):
    if 'user_type' in session and session['user_type'] == 'admin':
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_classe FROM Eleves WHERE id_eleve = %s", (eleve_id,))
        eleve_info = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify(eleve_info)
    return redirect(url_for('login'))

@app.route('/get_eleve_info/<int:id_eleve>', methods=['GET'])
def get_eleve_info(id_eleve):
    if 'user_type' in session and session['user_type'] == 'admin':
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer la classe, les professeurs et les notes de l'élève sélectionné
        cursor.execute("""
            SELECT Classes.nom_classe, Profs.nom_prof, Notes.note 
            FROM Eleves 
            JOIN Classes ON Eleves.id_classe = Classes.id_classe 
            JOIN Notes ON Eleves.id_eleve = Notes.id_eleve 
            JOIN Profs ON Notes.id_matiere = Profs.id_matiere 
            WHERE Eleves.id_eleve = %s
        """, (id_eleve,))
        eleve_info = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(eleve_info)
    return redirect(url_for('login'))

@app.route('/add_matiere', methods=['GET', 'POST'])
def add_matiere():
    if 'user_type' in session and session['user_type'] == 'admin':
        if request.method == 'POST':
            nom_matiere = request.form['nom_matiere']
            
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO Matieres (nom_matiere) 
                VALUES (%s)
            """, (nom_matiere,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Matière ajoutée avec succès')
            return redirect(url_for('admin'))
        
        return render_template('add_matiere.html')
    return redirect(url_for('login'))

@app.route('/add_classe', methods=['GET', 'POST'])
def add_classe():
    if 'user_type' in session and session['user_type'] == 'admin':
        if request.method == 'POST':
            nom_classe = request.form['nom_classe']
            
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO Classes (nom_classe) 
                VALUES (%s)
            """, (nom_classe,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Classe ajoutée avec succès')
            return redirect(url_for('admin'))
        
        return render_template('add_classe.html')
    return redirect(url_for('login'))

@app.route('/add_eleve', methods=['GET', 'POST'])
def add_eleve():
    if 'user_type' in session and session['user_type'] == 'admin':
        if request.method == 'POST':
            nom_eleve = request.form['nom_eleve']
            id_classe = request.form.get('id_classe')
            
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO Eleves (nom_eleve, id_classe, password) 
                VALUES (%s, %s, %s)
            """, (nom_eleve, id_classe, 'null'))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Élève ajouté avec succès')
            return redirect(url_for('admin'))
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_classe, nom_classe FROM Classes")
        classes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('add_eleve.html', classes=classes)
    return redirect(url_for('login'))

@app.route('/add_prof', methods=['GET', 'POST'])
def add_prof():
    if 'user_type' in session and session['user_type'] == 'admin':
        if request.method == 'POST':
            nom_prof = request.form['nom_prof']
            id_matiere = request.form.get('id_matiere')
            id_classe = request.form.get('id_classe')
            
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO Profs (nom_prof, id_matiere, password) 
                VALUES (%s, %s, %s)
            """, (nom_prof, id_matiere, 'null'))
            
            prof_id = cursor.lastrowid
            
            if id_classe:
                cursor.execute("""
                    INSERT INTO ProfClasse (id_prof, id_classe) 
                    VALUES (%s, %s)
                """, (prof_id, id_classe))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Professeur ajouté avec succès')
            return redirect(url_for('admin'))
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_matiere, nom_matiere FROM Matieres")
        matieres = cursor.fetchall()
        cursor.execute("SELECT id_classe, nom_classe FROM Classes")
        classes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('add_prof.html', matieres=matieres, classes=classes)
    return redirect(url_for('login'))

@app.route('/edit_eleve', methods=['POST'])
def edit_eleve():
    if 'user_type' in session and session['user_type'] == 'admin':
        id_eleve = request.form['id_eleve']
        id_classe = request.form['id_classe'] if request.form['id_classe'] else None
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE Eleves 
            SET id_classe = %s 
            WHERE id_eleve = %s
        """, (id_classe, id_eleve))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Classe de l\'élève mise à jour avec succès')
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route('/delete_eleve', methods=['POST'])
def delete_eleve():
    if 'user_type' in session and session['user_type'] == 'admin':
        id_eleve = request.form['id_eleve']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Delete rows from Notes where id_eleve matches
        cursor.execute("DELETE FROM Notes WHERE id_eleve = %s", (id_eleve,))
        
        # Delete the élève itself
        cursor.execute("DELETE FROM Eleves WHERE id_eleve = %s", (id_eleve,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Élève supprimé avec succès')
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route('/edit_prof', methods=['POST'])
def edit_prof():
    if 'user_type' in session and session['user_type'] == 'admin':
        id_prof = request.form['id_prof']
        id_matiere = request.form['id_matiere'] if 'id_matiere' in request.form else None
        add_class = request.form['add_class'] if 'add_class' in request.form and request.form['add_class'] else None

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        if id_matiere:
            cursor.execute("""
                UPDATE Profs 
                SET id_matiere = %s 
                WHERE id_prof = %s
            """, (id_matiere, id_prof))

        if add_class:
            cursor.execute("""
                INSERT INTO ProfClasse (id_prof, id_classe) 
                VALUES (%s, %s)
            """, (id_prof, add_class))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Informations du professeur mises à jour avec succès')
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route('/delete_prof', methods=['POST'])
def delete_prof():
    if 'user_type' in session and session['user_type'] == 'admin':
        id_prof = request.form['id_prof']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Delete rows from ProfClasse where id_prof matches
        cursor.execute("DELETE FROM Profclasse WHERE id_prof = %s", (id_prof,))
        
        # Delete the prof itself
        cursor.execute("DELETE FROM Profs WHERE id_prof = %s", (id_prof,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Professeur supprimé avec succès')
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route('/remove_class_from_prof/<int:prof_id>/<class_name>', methods=['POST'])
def remove_class_from_prof(prof_id, class_name):
    if 'user_type' in session and session['user_type'] == 'admin':
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE pc FROM ProfClasse pc
            JOIN Classes c ON pc.id_classe = c.id_classe
            WHERE pc.id_prof = %s AND c.nom_classe = %s
        """, (prof_id, class_name))

        conn.commit()
        cursor.close()
        conn.close()

        return '', 204
    return redirect(url_for('login'))

@app.route('/edit_matiere', methods=['POST'])
def edit_matiere():
    if 'user_type' in session and session['user_type'] == 'admin':
        id_matiere = request.form['id_matiere']
        # Add logic to update the matière if needed
        flash('Matière mise à jour avec succès')
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route('/delete_matiere', methods=['POST'])
def delete_matiere():
    if 'user_type' in session and session['user_type'] == 'admin':
        id_matiere = request.form['id_matiere']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Delete rows from Notes where id_matiere matches
        cursor.execute("DELETE FROM Notes WHERE id_matiere = %s", (id_matiere,))
        
        # Update Profs table to set id_matiere to NULL where id_matiere matches
        cursor.execute("UPDATE Profs SET id_matiere = NULL WHERE id_matiere = %s", (id_matiere,))
        
        # Delete the matière itself
        cursor.execute("DELETE FROM Matieres WHERE id_matiere = %s", (id_matiere,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Matière supprimée avec succès')
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route('/edit_classe', methods=['POST'])
def edit_classe():
    if 'user_type' in session and session['user_type'] == 'admin':
        id_classe = request.form['id_classe']
        # Add logic to update the classe if needed
        flash('Classe mise à jour avec succès')
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route('/delete_classe', methods=['POST'])
def delete_classe():
    if 'user_type' in session and session['user_type'] == 'admin':
        id_classe = request.form['id_classe']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Update ProfClasse table to set id_classe to NULL where id_classe matches
        cursor.execute("UPDATE ProfClasse SET id_classe = NULL WHERE id_classe = %s", (id_classe,))
        
        # Update Eleves table to set id_classe to NULL where id_classe matches
        cursor.execute("UPDATE Eleves SET id_classe = NULL WHERE id_classe = %s", (id_classe,))
        
        # Delete the classe itself
        cursor.execute("DELETE FROM Classes WHERE id_classe = %s", (id_classe,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Classe supprimée avec succès')
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_type', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)