document.addEventListener("DOMContentLoaded", function () {
  const editSection = document.getElementById("editSection");
  const editBtn = document.getElementById("editBtn");
  const cancelBtn = document.getElementById("cancelEditBtn");
  document.querySelector(".btn-change-password");
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
});