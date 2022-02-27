// The function used for fog on form
function uploadon() {
    document.getElementById("uploadformfog").style.display = "block";
    var x=window.scrollX;
    var y=window.scrollY;
    window.onscroll=function(){window.scrollTo(x, y);};
}

function uploadoff() {
    document.getElementById("uploadformfog").style.display = "none";
}
// The function used for fog on form


// gets the files from the server to display on the tables
async function getresources(course){
    const response = await fetch('/getresources')
    const data = await response.json()
    console.log(data);
}

document.addEventListener('DOMContentLoaded', function(){
    getresources()
});
// gets the files from the server to display on the tables
