/* static/js/perfil.js */

document.addEventListener("DOMContentLoaded", function () {
  const editSection = document.getElementById("editSection");
  const editBtn = document.getElementById("editBtn");
  const cancelBtn = document.getElementById("cancelEditBtn");
  const btnSenha = document.querySelector(".btn-change-password");

  if (editBtn && editSection) {
    editBtn.addEventListener("click", function () {
      editSection.style.display = "block";
      editSection.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  if (cancelBtn && editSection) {
    cancelBtn.addEventListener("click", function () {
      editSection.style.display = "none";
    });
  }

  if (btnSenha) {
    btnSenha.addEventListener("click", function () {
      alert("A funcionalidade de alteração de senha já será configurada na próxima etapa!");
    });
  }
});