// Suppression d'un administrateur
function deleteAdmin() {
    const adminId = document.getElementById('adminSelect').value;
    if (adminId) {
        fetch(`/superadmin/delete_admin/${adminId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Administrateur supprimé avec succès.');
                location.reload();
            } else {
                alert('Erreur lors de la suppression de l\'administrateur.');
            }
        });
    } else {
        alert('Veuillez sélectionner un administrateur.');
    }
}

// Ajout d'un administrateur
function addAdmin() {
    const adminName = document.getElementById('adminName').value;
    if (adminName) {
        fetch('/superadmin/add_admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nom_admin: adminName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('newPasswordText').innerText = data.password;
                const passwordModal = new bootstrap.Modal(document.getElementById('passwordModal'));
                passwordModal.show();
                passwordModal._element.addEventListener('hidden.bs.modal', () => {
                    location.reload();
                });
            } else {
                alert('Erreur lors de l\'ajout de l\'administrateur.');
            }
        });
    } else {
        alert('Veuillez remplir tous les champs.');
    }
}

// Copie du mot de passe généré
function copyPassword() {
    const passwordText = document.getElementById('newPasswordText').innerText;
    navigator.clipboard.writeText(passwordText).then(() => {
        const copyMessage = document.getElementById('copyMessage');
        copyMessage.style.display = 'block';
        setTimeout(() => {
            copyMessage.style.display = 'none';
        }, 2000);
    });
}