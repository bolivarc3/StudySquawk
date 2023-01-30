const menuIconButton = document.querySelector("[data-menu-icon-btn]")
console.log(menuIconButton)
const sidebar = document.querySelector("[data-sidebar]")
menuIconButton.addEventListener("click", () => {
  console.log("yo")
  sidebar.classList.toggle("open")
})