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