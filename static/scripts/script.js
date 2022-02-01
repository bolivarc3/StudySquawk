document.addEventListener('DOMContentLoaded', function(){
    //when the page loads grab the two tabs and switch them
    var disabledtab = document.getElementById("disabledtab");
    var activetab = document.getElementById("activetab");
    document.addEventListener("click", tabswitch);
});

function tabswitch(){
    console.log("hello")
    var disabledtab = document.getElementById("disabledtab");
    var activetab = document.getElementById("activetab");
    disabledtab.id = "activetab";
    activetab.id  = "disabledtab";
}