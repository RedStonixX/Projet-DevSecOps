// Affiche les informations des professeurs
function displayProfInfo() {
    const profSelect = document.getElementById('profSelect');
    const profId = profSelect.value;
    const profInfo = document.getElementById('profInfo');
    const profMatiere = document.getElementById('profMatiere');
    const profClasses = document.getElementById('profClasses');

    if (profId) {
        fetch(`/admin/prof_info/${profId}`)
            .then(response => response.json())
            .then(data => {
                profMatiere.textContent = data.matiere;
                profClasses.innerHTML = '';
                data.classes.forEach(classe => {
                    const li = document.createElement('li');
                    li.textContent = classe;
                    profClasses.appendChild(li);
                });
                profInfo.style.display = 'block';
            });
    } else {
        profInfo.style.display = 'none';
    }
}

// Affiche les informations des élèves
function displayEleveInfo() {
    const eleveSelect = document.getElementById('eleveSelect');
    const eleveId = eleveSelect.value;
    const eleveInfo = document.getElementById('eleveInfo');
    const eleveClasse = document.getElementById('eleveClasse');
    const eleveProfs = document.getElementById('eleveProfs');
    const eleveMoyenne = document.getElementById('eleveMoyenne');

    if (eleveId) {
        fetch(`/admin/eleve_info/${eleveId}`)
            .then(response => response.json())
            .then(data => {
                eleveClasse.textContent = data.classe;
                eleveProfs.innerHTML = '';
                data.profs.forEach(prof => {
                    const li = document.createElement('li');
                    li.textContent = `${prof.nom} (${prof.matiere})`;
                    eleveProfs.appendChild(li);
                });
                eleveMoyenne.textContent = parseFloat(data.moyenne).toFixed(2);
                eleveInfo.style.display = 'block';
            });
    } else {
        eleveInfo.style.display = 'none';
    }
}

// Affiche les notes des élèves
function displayEleveNotes() {
    const eleveSelect = document.getElementById('eleveSelect');
    const eleveId = eleveSelect.value;
    const eleveNotes = document.getElementById('eleveNotes');
    const eleveNotesTableBody = document.getElementById('eleveNotesTableBody');

    if (eleveId) {
        fetch(`/admin/eleve_info/${eleveId}`)
            .then(response => response.json())
            .then(data => {
                eleveNotesTableBody.innerHTML = '';
                for (const [matiere, notes] of Object.entries(data.notes)) {
                    const moyenne = parseFloat(data.notes_moyennes[matiere]).toFixed(2);
                    const notesStr = notes.join(', ');
                    const row = `<tr>
                                    <td>${matiere}</td>
                                    <td>${notesStr}</td>
                                    <td>${moyenne}</td>
                                 </tr>`;
                    eleveNotesTableBody.innerHTML += row;
                }
                eleveNotes.style.display = 'block';
            });
    } else {
        eleveNotes.style.display = 'none';
    }
}

let currentEleveId;
let currentMatiere;
let currentNoteIndex;

// Met à jour la sélection de la classe lors de la modification d'un élève
function updateClasseSelect() {
    const eleveSelect = document.getElementById('eleveSelectModal');
    const classeSelectContainer = document.getElementById('classeSelectContainer');
    const classeSelect = document.getElementById('classeSelectModal');
    const showNotesButton = document.getElementById('showNotesButton');
    const selectedEleve = eleveSelect.options[eleveSelect.selectedIndex];
    const classeId = selectedEleve.getAttribute('data-classe');

    classeSelectContainer.style.display = 'block';
    showNotesButton.style.display = 'block';

    for (let i = 0; i < classeSelect.options.length; i++) {
        if (classeSelect.options[i].value == classeId) {
            classeSelect.selectedIndex = i;
            break;
        } else {
            classeSelect.selectedIndex = 0;
        }
    }
}

// Met à jour la matière d'un professeur
function saveProfChanges() {
    const profId = document.getElementById('profSelectModal').value;
    const matiereId = document.getElementById('matiereSelectModal').value;

    fetch('/admin/update_prof_matiere', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prof_id: profId, matiere_id: matiereId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Les modifications ont été enregistrées avec succès.');
            location.reload();
        } else {
            alert('Une erreur est survenue lors de l\'enregistrement des modifications.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Une erreur est survenue lors de l\'enregistrement des modifications.');
    });
}

// Met à jour la classe d'un élève
function saveEleveChanges() {
    const eleveId = document.getElementById('eleveSelectModal').value;
    const classeId = document.getElementById('classeSelectModal').value;

    fetch('/admin/update_eleve_classe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ eleve_id: eleveId, classe_id: classeId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Les modifications ont été enregistrées avec succès.');
            location.reload();
        } else {
            alert('Une erreur est survenue lors de l\'enregistrement des modifications.');
        }
    });
}

// Affiche les notes d'un élève
function showEleveNotes() {
    const eleveId = document.getElementById('eleveSelectModal').value;
    if (!eleveId) {
        alert('Merci de sélectionner un élève.');
        return;
    }

    fetch(`/admin/eleve_info/${eleveId}`)
        .then(response => response.json())
        .then(data => {
            const notesTableBody = document.getElementById('notesEleveTableBody');
            const matiereSelect = document.getElementById('matiereSelect');
            notesTableBody.innerHTML = '';
            matiereSelect.innerHTML = '<option value="" disabled selected>Sélectionner une matière</option>';
            for (const [matiere, notes] of Object.entries(data.notes)) {
                const notesStr = notes.join(', ');
                const row = `<tr>
                                <td>${matiere}</td>
                                <td>${notesStr}</td>
                             </tr>`;
                notesTableBody.innerHTML += row;
                const option = document.createElement('option');
                option.value = matiere;
                option.textContent = matiere;
                matiereSelect.appendChild(option);
            }
            const notesEleveModal = new bootstrap.Modal(document.getElementById('notesEleveModal'));
            notesEleveModal.show();
        });
}

// Affiche les notes d'une matière pour un élève
function displayMatiereNotes() {
    const matiereSelect = document.getElementById('matiereSelect');
    const selectedMatiere = matiereSelect.value;
    const eleveId = document.getElementById('eleveSelectModal').value;

    fetch(`/admin/eleve_info/${eleveId}`)
        .then(response => response.json())
        .then(data => {
            const matiereNotesList = document.getElementById('matiereNotesList');
            matiereNotesList.innerHTML = '';
            const notes = data.notes[selectedMatiere];
            notes.forEach((note, index) => {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                li.innerHTML = `
                    <span>${note}</span>
                    <div>
                        <button class="btn btn-sm btn-warning me-2" onclick="openEditNoteModal(${eleveId}, '${selectedMatiere}', ${index}, ${note})">Modifier</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteNote(${eleveId}, '${selectedMatiere}', ${index})">Supprimer</button>
                    </div>
                `;
                matiereNotesList.appendChild(li);
            });
        });
}

// Ouvre la modal de modification d'une note
function openEditEleveModal(eleveId) {
    const eleveSelectModal = document.getElementById('eleveSelectModal');
    eleveSelectModal.value = eleveId;
    updateClasseSelect();
    const editEleveModal = new bootstrap.Modal(document.getElementById('editEleveModal'));
    editEleveModal.show();
}

// Ouverture de la modal de modification d'un professeur
function openEditProfModal(profId) {
    const profSelectModal = document.getElementById('profSelectModal');
    profSelectModal.value = profId;
    updateMatiereAndClassesSelect();
    const editProfModal = new bootstrap.Modal(document.getElementById('editProfModal'));
    editProfModal.show();
}

// Ouvre la modal de modification d'une note
function openEditNoteModal(eleveId, matiere, noteIndex, note) {
    currentEleveId = eleveId;
    currentMatiere = matiere;
    currentNoteIndex = noteIndex;
    document.getElementById('editNoteInput').value = note;
    const editNoteModal = new bootstrap.Modal(document.getElementById('editNoteModal'));
    editNoteModal.show();
}

// Enregistre les modifications d'une note
function saveNoteChanges() {
    const newNote = document.getElementById('editNoteInput').value;
    fetch('/admin/edit_note', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ eleve_id: currentEleveId, matiere: currentMatiere, note_index: currentNoteIndex, new_note: newNote })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('La note a été modifiée avec succès.');
            displayMatiereNotes();
            const editNoteModal = bootstrap.Modal.getInstance(document.getElementById('editNoteModal'));
            editNoteModal.hide();
        } else {
            alert('Une erreur est survenue lors de la modification de la note.');
        }
    });
}

// Supprime une note
function deleteNote(eleveId, matiere, noteIndex) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette note ?')) {
        fetch('/admin/delete_note', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                eleve_id: eleveId,
                matiere: matiere,
                note_index: noteIndex
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Note supprimée avec succès');
                location.reload();
            } else {
                alert('Erreur lors de la suppression de la note: ' + data.message);
            }
        })
        .catch(error => console.error('Erreur:', error));
    }
}

// Ajoute une note
function addNote() {
    const newNote = document.getElementById('newNoteInput').value;
    const eleveId = document.getElementById('eleveSelectModal').value;
    const matiere = document.getElementById('matiereSelect').value;

    if (!newNote || !eleveId || !matiere) {
        alert('Merci de remplir tous les champs.');
        return;
    }

    fetch('/admin/add_note', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ eleve_id: eleveId, matiere: matiere, new_note: newNote })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('La note a été ajoutée avec succès.');
            displayMatiereNotes();
            document.getElementById('newNoteInput').value = '';
        } else {
            alert('Une erreur est survenue lors de l\'ajout de la note.');
        }
    });
}

// Ajoute une classe
function addClasse() {
    const classeNameInput = document.getElementById('classeNameInput').value;

    if (!classeNameInput) {
        alert('Merci de remplir le nom de la classe.');
        return;
    }

    fetch('/admin/add_classe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nom_classe: classeNameInput })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Classe ajoutée avec succès.');
            location.reload();
        } else {
            alert(data.message);
        }
    });
}

// Supprime une classe
function deleteClasse() {
    const classeId = document.getElementById('classeSelectDelete').value;

    if (!classeId) {
        alert('Merci de sélectionner une classe.');
        return;
    }

    fetch('/admin/delete_classe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id_classe: classeId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('La classe a été supprimée avec succès.');
            location.reload();
        } else {
            alert('Une erreur est survenue lors de la suppression de la classe.');
        }
    });
}

// Supprime un élève
function deleteEleve() {
    const eleveId = document.getElementById('eleveSelectDelete').value;

    if (!eleveId) {
        alert('Merci de sélectionner un élève.');
        return;
    }

    fetch('/admin/delete_eleve', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id_eleve: eleveId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('L\'élève a été supprimé avec succès.');
            location.reload();
        } else {
            alert('Une erreur est survenue lors de la suppression de l\'élève.');
        }
    });
}

// Ajoute une matière
function addMatiere() {
    const matiereNameInput = document.getElementById('matiereNameInput').value;

    if (!matiereNameInput) {
        alert('Merci de remplir le nom de la matière.');
        return;
    }

    fetch('/admin/add_matiere', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nom_matiere: matiereNameInput })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Matière ajoutée avec succès.');
            location.reload();
        } else {
            alert(data.message);
        }
    });
}

// Supprime une matière
function deleteMatiere() {
    const matiereId = document.getElementById('matiereSelectDelete').value;

    if (!matiereId) {
        alert('Merci de sélectionner une matière.');
        return;
    }

    fetch('/admin/delete_matiere', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id_matiere: matiereId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('La matière a été supprimée avec succès.');
            location.reload();
        } else {
            alert('Une erreur est survenue lors de la suppression de la matière.');
        }
    });
}

// Met à jour la sélection de la matière lors de la modification d'un professeur
function updateMatiereAndClassesSelect() {
    const profSelect = document.getElementById('profSelectModal');
    const matiereSelectContainer = document.getElementById('matiereSelectContainer');
    const classesSelectContainer = document.getElementById('classesSelectContainer');
    const addClassSelectContainer = document.getElementById('addClassSelectContainer');
    const matiereSelect = document.getElementById('matiereSelectModal');
    const classesSelect = document.getElementById('classesSelectModal');
    const addClassSelect = document.getElementById('addClassSelectModal');
    const selectedProf = profSelect.options[profSelect.selectedIndex];
    const matiereId = selectedProf.getAttribute('data-matiere');
    const profId = selectedProf.value;

    matiereSelectContainer.style.display = 'block';
    classesSelectContainer.style.display = 'block';
    addClassSelectContainer.style.display = 'block';

    for (let i = 0; i < matiereSelect.options.length; i++) {
        if (matiereSelect.options[i].value == matiereId) {
            matiereSelect.selectedIndex = i;
            break;
        } else {
            matiereSelect.selectedIndex = 0;
        }
    }

    // Mettre à jour la liste des classes
    fetch(`/admin/prof_info/${profId}`)
        .then(response => response.json())
        .then(data => {
            classesSelect.innerHTML = '';
            addClassSelect.innerHTML = '<option value="" disabled selected>Sélectionner une classe</option>';
            const existingClasses = new Set(data.classes);
            data.classes.forEach(classe => {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                li.innerHTML = `
                    <span>${classe}</span>
                    <button class="btn btn-sm btn-danger" onclick="removeClassFromProf(${profId}, '${classe}')">X</button>
                `;
                classesSelect.appendChild(li);
            });
            data.all_classes.forEach(classe => {
                if (!existingClasses.has(classe)) {
                    const option = document.createElement('option');
                    option.value = classe;
                    option.textContent = classe;
                    addClassSelect.appendChild(option);
                }
            });
        });
}

// Supprime une classe d'un professeur
function removeClassFromProf(profId, className) {
    fetch('/admin/remove_class_from_prof', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prof_id: profId, class_name: className })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('La classe a été retirée du professeur avec succès.');
            updateMatiereAndClassesSelect();
        } else {
            alert('Une erreur est survenue lors de la suppression de la classe.');
        }
    });
}

// Vérifie la disponibilité d'une matière pour un professeur
function checkMatiereAvailability() {
    const matiereSelect = document.getElementById('matiereSelectModal');
    const selectedMatiereId = matiereSelect.value;
    const profSelect = document.getElementById('profSelectModal');
    const selectedProfId = profSelect.value;

    fetch(`/admin/check_matiere_availability/${selectedMatiereId}/${selectedProfId}`)
        .then(response => response.json())
        .then(data => {
            const matiereError = document.getElementById('matiereError');
            if (data.available) {
                matiereError.style.display = 'none';
            } else {
                matiereError.style.display = 'block';
                matiereSelect.value = '';
            }
        });
}

// Ajoute une classe à un professeur
function addClassToProf() {
    const profId = document.getElementById('profSelectModal').value;
    const className = document.getElementById('addClassSelectModal').value;

    if (!className) {
        return;
    }

    fetch('/admin/add_class_to_prof', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prof_id: profId, class_name: className })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('La classe a été ajoutée au professeur avec succès.');
            updateMatiereAndClassesSelect();
        } else {
            alert('Une erreur est survenue lors de l\'ajout de la classe.');
        }
    });
}

// Affiche les informations d'une classe
function displayClasseInfo() {
    const classeId = document.getElementById('classeSelect').value;
    const classeInfo = document.getElementById('classeInfo');
    const classeProfs = document.getElementById('classeProfs');
    const classeMoyennesMatieres = document.getElementById('classeMoyennesMatieres');
    const classeMoyenneGenerale = document.getElementById('classeMoyenneGenerale');

    if (!classeId) {
        classeInfo.style.display = 'none';
        return;
    }

    fetch(`/admin/classe_info/${classeId}`)
        .then(response => response.json())
        .then(data => {
            classeProfs.innerHTML = '';
            data.profs.forEach(prof => {
                const li = document.createElement('li');
                li.textContent = `${prof.nom} (${prof.matiere})`;
                classeProfs.appendChild(li);
            });

            classeMoyennesMatieres.innerHTML = '';
            for (const [matiere, moyenne] of Object.entries(data.moyennes_matieres)) {
                const li = document.createElement('li');
                li.textContent = `${matiere} : ${parseFloat(moyenne).toFixed(2)}`;
                classeMoyennesMatieres.appendChild(li);
            }

            classeMoyenneGenerale.textContent = parseFloat(data.moyenne_generale).toFixed(2);

            classeInfo.style.display = 'block';
        });
}

// Supprime un professeur
function deleteProf() {
    const profId = document.getElementById('profSelectDelete').value;

    fetch('/admin/delete_prof', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prof_id: profId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Le professeur a été supprimé avec succès.');
            location.reload();
        } else {
            alert('Une erreur est survenue lors de la suppression du professeur.');
        }
    });
}

// Ouvre la modal de création d'un utilisateur
function openCreateUserModal() {
    const createUserModal = new bootstrap.Modal(document.getElementById('createUserModal'));
    createUserModal.show();
}

// Met à jour le formulaire de création d'utilisateur
function updateUserForm() {
    const userType = document.getElementById('userTypeSelect').value;
    document.getElementById('profForm').style.display = userType === 'prof' ? 'block' : 'none';
    document.getElementById('eleveForm').style.display = userType === 'eleve' ? 'block' : 'none';
}

// Crée un utilisateur
function createUser() {
    const userType = document.getElementById('userTypeSelect').value;
    let url = '';
    let body = {};

    if (userType === 'prof') {
        const profName = document.getElementById('profNameInput').value;
        url = '/admin/create_prof';
        body = { nom_prof: profName };
    } else if (userType === 'eleve') {
        const eleveName = document.getElementById('eleveNameInput').value;
        url = '/admin/create_eleve';
        body = { nom_eleve: eleveName };
    }

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const createUserModal = bootstrap.Modal.getInstance(document.getElementById('createUserModal'));
            createUserModal.hide();
            document.getElementById('newPasswordText').innerText = `Nouveau mot de passe : ${data.password}`;
            const passwordModal = new bootstrap.Modal(document.getElementById('passwordModal'));
            passwordModal.show();
            passwordModal._element.addEventListener('hidden.bs.modal', () => {
                location.reload();
            });
        } else {
            alert(data.message);
        }
    });
}

// Réinitialise le mot de passe d'un élève
function resetElevePassword() {
    const eleveId = document.getElementById('eleveSelectModal').value;

    fetch('/admin/reset_eleve_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ eleve_id: eleveId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const editEleveModal = bootstrap.Modal.getInstance(document.getElementById('editEleveModal'));
            editEleveModal.hide();
            document.getElementById('newPasswordText').innerText = `Nouveau mot de passe : ${data.password}`;
            const passwordModal = new bootstrap.Modal(document.getElementById('passwordModal'));
            passwordModal.show();
            passwordModal._element.addEventListener('hidden.bs.modal', () => {
                location.reload();
            });
        } else {
            alert('Une erreur est survenue lors de la réinitialisation du mot de passe.');
        }
    });
}

// Réinitialise le mot de passe d'un professeur
function resetProfPassword() {
    const profId = document.getElementById('profSelectModal').value;

    fetch('/admin/reset_prof_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prof_id: profId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const editProfModal = bootstrap.Modal.getInstance(document.getElementById('editProfModal'));
            editProfModal.hide();
            document.getElementById('newPasswordText').innerText = `Nouveau mot de passe : ${data.password}`;
            const passwordModal = new bootstrap.Modal(document.getElementById('passwordModal'));
            passwordModal.show();
            passwordModal._element.addEventListener('hidden.bs.modal', () => {
                location.reload();
            });
        } else {
            alert('Une erreur est survenue lors de la réinitialisation du mot de passe.');
        }
    });
}

// Copie le mot de passe généré
function copyPassword() {
    const passwordText = document.getElementById('newPasswordText').innerText.replace('Nouveau mot de passe : ', '');
    navigator.clipboard.writeText(passwordText).then(() => {
        const copyMessage = document.getElementById('copyMessage');
        copyMessage.style.display = 'block';
        setTimeout(() => {
            copyMessage.style.display = 'none';
        }, 2000);
    });
}

// Vérification que les notes entrées par l'utilisateur sont correctes
function validateNoteInput(noteInput) {
    const noteValue = parseFloat(noteInput.value);
    if (isNaN(noteValue) || noteValue < 0 || noteValue > 20) {
        alert('La note doit être un nombre compris entre 0 et 20.');
        return false;
    }
    return true;
}

// Vérification que le formulaire d'ajout de note est correct
function validateAddNoteForm() {
    const noteInput = document.getElementById('newNoteValue');
    return validateNoteInput(noteInput);
}

// Vérification que le formulaire de modification de note est correct
function validateEditNoteForm() {
    const noteInput = document.getElementById('editNoteValue');
    return validateNoteInput(noteInput);
}