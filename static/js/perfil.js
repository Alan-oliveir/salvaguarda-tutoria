// static/js/perfil.js
// Controla a visibilidade da seção de edição e o botão correspondente

function toggleEditMode() {
    const editSection = document.getElementById('editSection');
    const editBtn = document.getElementById('editBtn');

    if (editSection.style.display === 'none') {
        editSection.style.display = 'block';
        editBtn.textContent = '❌ Cancelar Edição';
    } else {
        editSection.style.display = 'none';
        editBtn.textContent = '✏️ Editar Perfil';
    }
}

function changePassword() {
    // TODO: implementar modal ou redirect para página de troca de senha
    alert('Funcionalidade de alteração de senha será implementada em breve!');
}
