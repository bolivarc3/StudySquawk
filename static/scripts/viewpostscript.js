
function checktext(){
    var blank = "";
    var form = document.getElementById("inputbodytext").value;

    if (blank != form){
        document.getElementById("submitbutton").className = "active";
    }
    else{
        document.getElementById("submitbutton").className = "disabled";
    }
}


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

function showimage(imagepath){
    img = document.createElement('img');
    img.id = "popupimage"
    img.src = imagepath;
    
    overlay = document.getElementById("overlay")
    overlay.removeChild(overlay.lastChild)
    overlay.appendChild(img)
    overlay_on()
}

function overlay_on() {
    document.getElementById("overlay").style.display = "block";
  }
  
  function overlay_off() {
    document.getElementById("overlay").style.display = "none";
  } 