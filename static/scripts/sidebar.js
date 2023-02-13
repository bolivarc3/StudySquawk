const menuIconButton = document.querySelector("[data-menu-icon-btn]")
var sidebar = document.querySelector("[data-sidebar]")
var header_height = document.querySelector(".header").clientHeight
console.log(header_height)
header_height = header_height.toString() + "px"
console.log()
document.documentElement.style.setProperty('--header-height', header_height);
menuIconButton.addEventListener("click", () => {
  console.log("yo")
  sidebar.classList.toggle("open")
})
