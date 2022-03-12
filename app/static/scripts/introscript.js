function signupon() {
    document.getElementById("signupfog").style.display = "block";
    var x=window.scrollX;
    var y=window.scrollY;
    window.onscroll=function(){window.scrollTo(x, y);};
}

function loginon() {
    document.getElementById("loginfog").style.display = "block";
    var x=window.scrollX;
    var y=window.scrollY;
    window.onscroll=function(){window.scrollTo(x, y);};
}

function signupoff() {
    document.getElementById("signupfog").style.display = "none";
}

function loginoff(){
    document.getElementById("loginfog").style.display = "none";
}