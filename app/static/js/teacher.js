
function openEditModal(noteId, noteValue) {
    const editNoteForm = document.getElementById('editNoteForm');
    editNoteForm.action = `{{ url_for('prof.prof_edit_note', note_id=0) }}`.replace('0', noteId);
    document.getElementById('newNoteValue').value = noteValue;
    const editNoteModal = new bootstrap.Modal(document.getElementById('editNoteModal'));
    editNoteModal.show();
}