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

function updateClasseSelect() {
    const eleveSelect = document.getElementById('eleveSelectModal');
    const classeSelect = document.getElementById('classeSelectModal');
    const selectedEleve = eleveSelect.options[eleveSelect.selectedIndex];
    const classeId = selectedEleve.getAttribute('data-classe');

    for (let i = 0; i < classeSelect.options.length; i++) {
        if (classeSelect.options[i].value == classeId) {
            classeSelect.selectedIndex = i;
            break;
        } else {
            classeSelect.selectedIndex = 0;
        }
    }
}

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

function openEditNoteModal(eleveId, matiere, noteIndex, note) {
    currentEleveId = eleveId;
    currentMatiere = matiere;
    currentNoteIndex = noteIndex;
    document.getElementById('editNoteInput').value = note;
    const editNoteModal = new bootstrap.Modal(document.getElementById('editNoteModal'));
    editNoteModal.show();
}

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

function deleteNote(eleveId, matiere, noteIndex) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette note?')) {
        fetch('/admin/delete_note', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ eleve_id: eleveId, matiere: matiere, note_index: noteIndex })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('La note a été supprimée avec succès.');
                displayMatiereNotes();
            } else {
                alert('Une erreur est survenue lors de la suppression de la note.');
            }
        });
    }
}

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

function addClasse() {
    const classeName = document.getElementById('classeNameInput').value;

    if (!classeName) {
        alert('Merci de remplir le nom de la classe.');
        return;
    }

    fetch('/admin/add_classe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nom_classe: classeName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('La classe a été ajoutée avec succès.');
            location.reload();
        } else {
            alert('Une erreur est survenue lors de l\'ajout de la classe.');
        }
    });
}

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

function addMatiere() {
    const matiereName = document.getElementById('matiereNameInput').value;

    if (!matiereName) {
        alert('Merci de remplir le nom de la matière.');
        return;
    }

    fetch('/admin/add_matiere', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nom_matiere: matiereName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('La matière a été ajoutée avec succès.');
            location.reload();
        } else {
            alert('Une erreur est survenue lors de l\'ajout de la matière.');
        }
    });
}

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

function updateMatiereSelect() {
    const profSelect = document.getElementById('profSelectModal');
    const matiereSelect = document.getElementById('matiereSelectModal');
    const selectedProf = profSelect.options[profSelect.selectedIndex];
    const matiereId = selectedProf.getAttribute('data-matiere');

    for (let i = 0; i < matiereSelect.options.length; i++) {
        if (matiereSelect.options[i].value == matiereId) {
            matiereSelect.selectedIndex = i;
            break;
        } else {
            matiereSelect.selectedIndex = 0;
        }
    }
}

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
    });
}