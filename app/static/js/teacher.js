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
    const noteInput = document.getElementById('newNoteValue');
    return validateNoteInput(noteInput);
}