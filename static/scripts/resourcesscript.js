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

function newfolderoff() {
    document.getElementById("newfolderformfog").style.display = "none";
}

function newfolderon() {
    document.getElementById("newfolderformfog").style.display = "block";
    var x=window.scrollX;
    var y=window.scrollY;
    window.onscroll=function(){window.scrollTo(x, y);};
}


// gets the files from the server to display on the tables
async function getfolders(course){
    const rows = Array.from(document.getElementsByClassName('rowbox'))
    rows.forEach(row =>{
        row.remove();
    });
    const response = await fetch('/getfolders', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify(course) // body data type must match "Content-Type" header
    })
    const data = await response.json()
    createfolders(data)
    getresources(course)
}

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
    createresources(data)
}

function createresources(materials){
    var length = materials.length
    if(length > 0){
        //for the amount of images
        for(let i = 0; i < length; i++){
            //makes a container for the seperate images
            document.getElementById("routing").innerHTML = materials[i][1]

            tablerow = document.createElement('tr');
            tablerow.id = "rowbox" + Number(materials[i][0])
            tablerow.classList = "rowbox"

            checkmark = document.createElement('td');
            checkmark.id = "checkbox"

            checkmark = document.createElement('td');
            checkmark.id = "checkbox"
            checkmarkicon = document.createElement('i');
            checkmarkicon.classList = "fa-solid fa-circle-check"
            checkmark.appendChild(checkmarkicon);
            tablerow.appendChild(checkmark);

            filetype = document.createElement('td');
            filetype.id = "tablecells"
            filetypeicon = document.createElement('i');
            filetypeicon.classList = "fa-solid fa-file"
            filetype.appendChild(filetypeicon);
            tablerow.appendChild(filetype);

            filename = document.createElement('td');
            filename.id = "tablecells"
            filename.classList = "tablecells"
            link = document.createElement('a')
            link.href = "/static/resources" + materials[i][1] + "/" + materials[i][5]
            link.innerHTML = materials[i][5]
            link.target = "_blank"
            filename.appendChild(link);
            tablerow.appendChild(filename);

            modifieddate = document.createElement('td');
            modifieddate.id = "tablecells"
            modifieddate.classList = "tablecells"
            link2 = document.createElement('a')
            link2.href = "/static/resources" + materials[i][1] + "/" + materials[i][5]
            link2.innerHTML = materials[i][7]
            link2.target = "_blank"
            modifieddate.appendChild(link2);
            tablerow.appendChild(modifieddate);

            username = document.createElement('td');
            username.id = "tablecells"
            username.classList = "tablecells"
            link3 = document.createElement('a')
            link3.href = "/static/resources" + materials[i][1] + "/" + materials[i][5]
            link3.innerHTML = materials[i][4]
            link3.target = "_blank"
            username.appendChild(link3);
            tablerow.appendChild(username);

            document.getElementById("resourcestable").appendChild(tablerow);
        }
    }
}

function createfolders(materials){
    var length = materials.length
    if(length > 0){
        //for the amount of images
        for(let i = 0; i < length; i++){
            //makes a container for the seperate images
            document.getElementById("routing").innerHTML = materials[i][1]

            tablerow = document.createElement('tr');
            tablerow.id = "rowbox" + Number(materials[i][0])
            tablerow.classList = "rowbox"

            checkmark = document.createElement('td');
            checkmark.id = "checkbox"

            checkmark = document.createElement('td');
            checkmark.id = "checkbox"
            checkmarkicon = document.createElement('i');
            checkmarkicon.classList = "fa-solid fa-circle-check"
            checkmark.appendChild(checkmarkicon);
            tablerow.appendChild(checkmark);

            filetype = document.createElement('td');
            filetype.id = "tablecells"
            filetypeicon = document.createElement('i');
            filetypeicon.classList = "fa-solid fa-folder"
            filetype.appendChild(filetypeicon);
            tablerow.appendChild(filetype);

            filename = document.createElement('td');
            filename.id = "tablecells"
            filename.classList = "tablecells"
            link = document.createElement('a')
            link.innerHTML = materials[i][5]
            link.target = "_blank"
            newfilepath = materials[i][1] + "/" + materials[i][5]
            link.addEventListener("click",function() {
                    getfolders(newfilepath)
                }
            );
            const formroutings = Array.from(document.getElementsByName('route'))
            formroutinglengths = formroutings.length
            for (i = 0; i < formroutinglengths; i++) {
                formroutings[i].value = newfilepath
            }
            filename.appendChild(link);
            tablerow.appendChild(filename);

            modifieddate = document.createElement('td');
            modifieddate.id = "tablecells"
            modifieddate.classList = "tablecells"
            link2 = document.createElement('a')
            link2.innerHTML = materials[i][7]
            link2.target = "_blank"
            modifieddate.appendChild(link2);
            tablerow.appendChild(modifieddate);

            username = document.createElement('td');
            username.id = "tablecells"
            username.classList = "tablecells"
            link3 = document.createElement('a')
            link3.innerHTML = materials[i][4]
            link3.target = "_blank"
            username.appendChild(link3);
            tablerow.appendChild(username);


            document.getElementById("resourcestable").appendChild(tablerow);
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