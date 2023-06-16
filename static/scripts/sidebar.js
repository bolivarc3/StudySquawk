document.addEventListener("DOMContentLoaded", function(event) {
  //updates the sidebar to update the section that is active
  update_sidebar()
  const menuIconButton = document.querySelector("[data-menu-icon-btn]")
  //sidebar height from the top is determined by the height of the navbar\

  var header = document.getElementById('header_for_page')
  const image_height = header.clientHeight;
  console.log(image_height)
  height = image_height
  height = height.toString() + "px"
  console.log(height)
  document.documentElement.style.setProperty('--header-height', height);
  
  const bottom_bar = document.querySelector('[bottom_bar]');
  var spacerheight = bottom_bar.clientHeight;
  spacerheight = spacerheight.toString() + "px";
  document.documentElement.style.setProperty('--spacer-height', spacerheight);


  menuIconButton.addEventListener("click", () => {
    sidebar.classList.toggle("open")
  })
});

function update_sidebar(){
  var page_identifier = document.getElementById("page-identifier").value
  const sidebar_section = document.getElementById(page_identifier)
  sidebar_section.classList.add("active")
}
