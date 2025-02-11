function validateNoteInput(noteInput) {
    const noteValue = parseFloat(noteInput.value);
    if (isNaN(noteValue) || noteValue < 0 || noteValue > 20) {
        alert('La note doit être un nombre compris entre 0 et 20.');
        return false;
    }
    return true;
}

function validateAddNoteForm() {
    const noteInput = document.getElementById('newNoteValue');
    return validateNoteInput(noteInput);
}

function validateEditNoteForm() {
    const noteInput = document.getElementById('newNoteValue');
    return validateNoteInput(noteInput);
}