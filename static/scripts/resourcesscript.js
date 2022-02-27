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

// Allows for Preview of file
function showPreview(event){
    var length = event.target.files.length;
    if(length > 0){
        //for the amount of images 
        for(let i = 0; i < length; i++){
            //
            const img = [];
            img[i] = document.createElement('img');
            img[i].src = URL.createObjectURL(event.target.files[i]);

            //makes a container for the seperate images
            const imagediv = [];
            imagediv[i] = document.createElement('div');
            imagediv[i].id = "imagecontainer" + i;
            imagediv[i].classList = "imagecontainer";

            const imagelist = [];
            imagelist[i] = document.createElement('li');
            imagelist[i].id = "imagelistelement" + i;
            //sets the images into the html
            document.getElementById("horizontal-list").appendChild(imagelist[i]);
            document.getElementById("imagelistelement" + i).appendChild(imagediv[i]);
            document.getElementById("imagecontainer" + i).appendChild(img[i]);
        }
    }
}
// Allows for Preview of file