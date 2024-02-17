
document.addEventListener("DOMContentLoaded", function(){
    document.getElementById("x-element-login-div").addEventListener("click",function(){
        loginoff()
    })
    // document.getElementById.addEventListener("click",signupoff())
})

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
    window.onscroll = function(){

    };
    event.stopPropagation();
}

function loginoff(){
    document.getElementById("loginfog").style.display = "none";
    window.onscroll = function(){

    };
    event.stopPropagation();
}