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
    const response = await fetch('/getresources', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify(course) // body data type must match "Content-Type" header
    })
    const data = await response.json()
    console.log(data);
    createresources(data)
}
// gets the files from the server to display on the tables
    // <table id = "resourcestable">
    //     <tr>
    //         <th id = "tableheader"><i class="fa-solid fa-circle-check"></i></th>
    //         <th id = "tableheader" width = "2%"><i class="fa-solid fa-file"></i></th>
    //         <th id = "tableheader"width ="50%">Name</th>
    //         <th id = "tableheader", width = "24%">Date Modified</th>
    //         <th id = "tableheader", width = "24%">Modified By</th>
    //     </tr>
    //     <link href="/static/resources/Algebra 1/Capture - Copy.PNG">

    //     <tr id = "rowbox">

    //         <td id = "checkbox"><i class="fa-solid fa-circle-check"></td>
    //         <td id = "tablecells"><i class="fa-solid fa-file"></i></td>
    //         <td id = "tablecells"><a href="/static/resources/Algebra 1/Capture - Copy.PNG" target="_blank">Testing File</a></td>
    //         <td id = "tablecells"><a href="/static/resources/Algebra 1/Capture - Copy.PNG" target="_blank">8/20/2022</a></td>
    //         <td id = "tablecells"><a href="/static/resources/Algebra 1/Capture - Copy.PNG" target="_blank">codetest</a></td>
    //     </tr>
    // </table>

function createresources(materials){
    var length = materials.length
    if(length > 0){
        //for the amount of images
        for(let i = 0; i < length; i++){
            material = materials[i];
            //makes a container for the seperate images
            tablerow = document.createElement('tr');
            tablerow.id = "rowbox"

            name = document.createElement('td');
            name.id = "tablecells"

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