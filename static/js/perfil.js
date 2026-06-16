/* static/js/perfil.js */

document.addEventListener("DOMContentLoaded", function () {
  const editSection = document.getElementById("editSection");
  const editBtn = document.getElementById("editBtn");
  const cancelBtn = document.getElementById("cancelEditBtn");
  const btnSenha = document.querySelector(".btn-change-password");

  if (editBtn && editSection) {
    editBtn.addEventListener("click", function () {
      const aberto = editSection.style.display !== "none";
      editSection.style.display = aberto ? "none" : "block";
      editBtn.textContent = aberto ? "✏️ Editar Perfil" : "❌ Cancelar Edição";
    });
  }

  if (btnSenha) {
    btnSenha.addEventListener("click", function () {
      alert("Funcionalidade de alteração de senha será implementada em breve!");
    });
  }

  function toggleEdit() {
    const aberto = editSection.style.display !== "none";
    editSection.style.display = aberto ? "none" : "block";
  }

  if (editBtn) editBtn.addEventListener("click", toggleEdit);
  if (cancelBtn) cancelBtn.addEventListener("click", toggleEdit);
});
