var tab = document.getElementsByClassName("tab");
document.addEventListener('DOMContentLoaded', function(){
    //when the page loads grab the two tabs and switch them
    var disabledtab = document.getElementById("disabledtab");
    var activetab = document.getElementById("activetab");
    disabledtab.addEventListener("click", tabswitch);
});

function tabswitch(){
    var disabledtab = document.getElementById("disabledtab");
    var activetab = document.getElementById("activetab");
    disabledtab.id = "activetab";
    activetab.id  = "disabledtab";
    var disabledtab = document.getElementById("disabledtab");
    var activetab = document.getElementById("activetab");
    disabledtab.addEventListener("click", tabswitch);
    const response = await fetch('/api')
    const data = await response.json()
    console.log(data);

}