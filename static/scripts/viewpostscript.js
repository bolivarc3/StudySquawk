
function checktext(){
    var blank = "";
    var form = document.getElementById("inputbodytext").value;

    console.log("hellow")
    if (blank != form){
        console.log("hello")
        document.getElementById("submitbutton").className = "active";
    }
    else{
        document.getElementById("submitbutton").className = "disabled";
    }
}