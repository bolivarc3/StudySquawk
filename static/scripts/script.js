var tab = document.getElementsByClassName("tab");
document.addEventListener('DOMContentLoaded', function(){

    //when the page loads grab the two tabs and switch them
    var disabledtab = document.getElementById("disabledtab");
    var activetab = document.getElementById("activetab");
    disabledtab.addEventListener("click", tabswitch);
    getData()
});

function tabswitch(){
    //grabs id of disabled and if of active tab
    var disabledtab = document.getElementById("disabledtab");
    var activetab = document.getElementById("activetab");

    disabledtab.id = "activetab";
    activetab.id  = "disabledtab";

    var disabledtab = document.getElementById("disabledtab");
    var activetab = document.getElementById("activetab");
    disabledtab.addEventListener("click", tabswitch);

    //changes content of the body
    const bodydiv = document.getElementById("bodydiv")
    var display = window.getComputedStyle(document.getElementById("bodydiv"), null).display;
    console.log(typeof(display))
    if (display == "block"){
        console.log("hello")
        bodydiv.style.display = "none"
    }
    else{
        bodydiv.style.display = "block"
    }
}

async function getData(){
    const response = await fetch('/getcourses')
    const data = await response.json()
    console.log(data);
}