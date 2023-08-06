// import JSZip from "jszip";
// import { saveAs } from 'file-saver';

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
// async function getfolders(course){
//     const rows = Array.from(document.getElementsByClassName('rowbox'))
//     rows.forEach(row =>{
//         row.remove();
//     });
//     const response = await fetch('/getfolders', {
//         method: 'POST', // *GET, POST, PUT, DELETE, etc.
//         headers: {
//             'Content-Type': 'application/json'
//             // 'Content-Type': 'application/x-www-form-urlencoded',
//         },
//         body: JSON.stringify(course) // body data type must match "Content-Type" header
//     })
//     const data = await response.json()
//     createfolders(data)
//     getresources(course)
// }

// async function getresources(course){
//     const response = await fetch('/getresources', {
//         method: 'POST', // *GET, POST, PUT, DELETE, etc.
//         headers: {
//             'Content-Type': 'application/json'
//             // 'Content-Type': 'application/x-www-form-urlencoded',
//         },
//         body: JSON.stringify(course) // body data type must match "Content-Type" header
//     })
//     const data = await response.json()
//     createresources(data)
// }

// function createresources(materials){
//     var length = materials.length
//     if(length > 0){
//         //for the amount of images
//         for(let i = 0; i < length; i++){
//             //makes a container for the seperate images
//             document.getElementById("routing").innerHTML = materials[i][1]

//             tablerow = document.createElement('tr');
//             tablerow.id = "rowbox" + Number(materials[i][0])
//             tablerow.classList = "rowbox"

//             checkmark = document.createElement('td');
//             checkmark.id = "checkbox"

//             checkmark = document.createElement('td');
//             checkmark.id = "checkbox"
//             checkmarkicon = document.createElement('i');
//             checkmarkicon.classList = "fa-solid fa-circle-check"
//             checkmark.appendChild(checkmarkicon);
//             tablerow.appendChild(checkmark);

//             filetype = document.createElement('td');
//             filetype.id = "tablecells"
//             filetypeicon = document.createElement('i');
//             filetypeicon.classList = "fa-solid fa-file"
//             filetype.appendChild(filetypeicon);
//             tablerow.appendChild(filetype);

//             filename = document.createElement('td');
//             filename.id = "tablecells"
//             filename.classList = "tablecells"
//             link = document.createElement('a')
//             link.href = "/static/resources" + materials[i][1] + "/" + materials[i][5]
//             link.innerHTML = materials[i][5]
//             link.target = "_blank"
//             filename.appendChild(link);
//             tablerow.appendChild(filename);

//             modifieddate = document.createElement('td');
//             modifieddate.id = "tablecells"
//             modifieddate.classList = "tablecells"
//             link2 = document.createElement('a')
//             link2.href = "/static/resources" + materials[i][1] + "/" + materials[i][5]
//             link2.innerHTML = materials[i][7]
//             link2.target = "_blank"
//             modifieddate.appendChild(link2);
//             tablerow.appendChild(modifieddate);

//             username = document.createElement('td');
//             username.id = "tablecells"
//             username.classList = "tablecells"
//             link3 = document.createElement('a')
//             link3.href = "/static/resources" + materials[i][1] + "/" + materials[i][5]
//             link3.innerHTML = materials[i][4]
//             link3.target = "_blank"
//             username.appendChild(link3);
//             tablerow.appendChild(username);

//             document.getElementById("resourcestable").appendChild(tablerow);
//         }
//     }
// }

// function createfolders(materials){
//     var length = materials.length
//     if(length > 0){
//         //for the amount of images
//         for(let i = 0; i < length; i++){
//             //makes a container for the seperate images
//             document.getElementById("routing").innerHTML = materials[i][1]

//             tablerow = document.createElement('tr');
//             tablerow.id = "rowbox" + Number(materials[i][0])
//             tablerow.classList = "rowbox"

//             checkmark = document.createElement('td');
//             checkmark.id = "checkbox"

//             checkmark = document.createElement('td');
//             checkmark.id = "checkbox"
//             checkmarkicon = document.createElement('i');
//             checkmarkicon.classList = "fa-solid fa-circle-check"
//             checkmark.appendChild(checkmarkicon);
//             tablerow.appendChild(checkmark);

//             filetype = document.createElement('td');
//             filetype.id = "tablecells"
//             filetypeicon = document.createElement('i');
//             filetypeicon.classList = "fa-solid fa-folder"
//             filetype.appendChild(filetypeicon);
//             tablerow.appendChild(filetype);

//             filename = document.createElement('td');
//             filename.id = "tablecells"
//             filename.classList = "tablecells"
//             link = document.createElement('a')
//             link.innerHTML = materials[i][5]
//             link.target = "_blank"
//             newfilepath = materials[i][1] + "/" + materials[i][5]
//             link.addEventListener("click",function() {
//                     getfolders(newfilepath)
//                 }
//             );
//             const formroutings = Array.from(document.getElementsByName('route'))
//             formroutinglengths = formroutings.length
//             for (i = 0; i < formroutinglengths; i++) {
//                 formroutings[i].value = newfilepath
//             }
//             filename.appendChild(link);
//             tablerow.appendChild(filename);

//             modifieddate = document.createElement('td');
//             modifieddate.id = "tablecells"
//             modifieddate.classList = "tablecells"
//             link2 = document.createElement('a')
//             link2.innerHTML = materials[i][7]
//             link2.target = "_blank"
//             modifieddate.appendChild(link2);
//             tablerow.appendChild(modifieddate);

//             username = document.createElement('td');
//             username.id = "tablecells"
//             username.classList = "tablecells"
//             link3 = document.createElement('a')
//             link3.innerHTML = materials[i][4]
//             link3.target = "_blank"
//             username.appendChild(link3);
//             tablerow.appendChild(username);


//             document.getElementById("resourcestable").appendChild(tablerow);
//         }
//     }
// }


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

function preview_resource(id_number){
    console.log(id_number)
    document.getElementById(id_number).style.display = "block"
}

function infofog_off(id_number){
    document.getElementById(id_number).style.display = "none"
}
// Allows for Preview of file
selected_elements = []
folder_elements = []
selected_elements_titles = []
folder_elements_titles = []
selected_elements_ids = []
window.addEventListener("DOMContentLoaded", (event) => {
    var checkboxes = document.getElementsByClassName("checkbox") 
    for(var check_box_num = 0; check_box_num < checkboxes.length; check_box_num++){
        var current_checkbox = checkboxes[check_box_num]
        current_checkbox.addEventListener('click', function(check_box_num){
            checkbox_color = getComputedStyle(this).color
            console.log(checkbox_color)


            if (checkbox_color == "rgb(22, 27, 34)"){
                this.style.color="white";
                selected(this,this.id)
                console.log("activate")
            }
            else if(checkbox_color == "rgb(81, 81, 82)"){
                this.style.color="white";
                selected(this,this.id)
                console.log("activate")
            }
            if(checkbox_color == "rgb(255, 255, 255)"){
                this.style.color="#161b22"
                deslected(this,this.id)
                console.log("disactivate")
            }
        })
    }
});

function selected(element,type){ 
    var parent = element.parentElement;
    var children_rows = parent.childNodes;
    var title = children_rows[1].id
    if (type == "folder"){
        var a_element = children_rows[7].childNodes[0]
        var link = decodeURI(a_element.href)
        folder_elements.push(link)
    }
    else{
        console.log("YES")
        var a_element = children_rows[9].childNodes[0]
        var link = decodeURI(a_element.href)
        selected_elements.push(link)
        selected_elements_titles.push(title)
    }
    selected_elements_ids.push(parent.className)
    console.log(selected_elements_ids)
}

function deslected(element,type){
    var parent = element.parentElement;
    var children_rows = parent.childNodes;
    console.log(parent.className)
    if (type == "folder"){
        var a_element = children_rows[7].childNodes[0]
        var link = a_element.href
        var index = folder_elements.indexOf(decodeURI(link));
        if (index > -1) {
            folder_elements.splice(index, 1);
            folder_elements_titles.splice(index,1)
        }
        index = selected_elements_ids.indexOf(parent.className)
        if (index > -1) {
            selected_elements_ids.splice(index, 1);
        }

    }
    else{
        var a_element = children_rows[9].childNodes[0]
        var link = a_element.href
        var index = selected_elements.indexOf(decodeURI(link));
        if (index > -1) {
            selected_elements.splice(index, 1);
            selected_elements_titles.splice(index,1)
        }
        index = selected_elements_ids.indexOf(parent.className)
        if (index > -1) {
            selected_elements_ids.splice(index, 1);
        }
    }
    console.log(selected_elements_ids)
}

async function send_files_for_zip(){
    const response = await fetch('/zip_download_files', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify(selected_elements) // body data type must match "Content-Type" header
    })
    const zip_number = await response.json()
    console.log(zip_number)
    hostname = window.location.hostname	 
    return(zip_number)
}
async function zipit(path_zip){
    console.log(path_zip)
    const response = await fetch('/zipit', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body:JSON.stringify(path_zip)
    })
    console.log("yeah")
    zip_number = await response.json()
}
async function send_folders_for_zip(zip_number){
    const response = await fetch('/folder_zip_download', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify({"folder_elements":folder_elements,"zip_number":zip_number}) // body data type must match "Content-Type" header
    })
    zip_number = await response.json()
    console.log(zip_number)
    hostname = window.location.hostname	
    return (zip_number)
}


async function download_files() {
    let zip_number = ''
    var path_zip = ''
    if (selected_elements.length != 0 || folder_elements.length != 0)
    {
        if (selected_elements.length != 0){
            zip_number = await send_files_for_zip(zip_number)
        }
        if (folder_elements.length != 0){
            zip_number = await send_folders_for_zip(zip_number)
        }
        path_zip = "/static/" + "zip_files/" + zip_number.toString() +"/file.zip"
        console.log(path_zip)
        await zipit(zip_number)
        download_zip(path_zip,"file.zip")
    }
}


function download_zip(url,fileName){
    const downloadLink = document.createElement('a');
    downloadLink.setAttribute('download', fileName)
  
    // Append the link to the DOM (this is required for the download to work in some browsers)
    downloadLink.href = url
    document.body.appendChild(downloadLink);
  
    // Click the link to start the download
    downloadLink.click();
    
    // Remove the link (it's not needed anymore)
    document.body.removeChild(downloadLink);
}
user_access_usernames = []
function select_user(event) {
    console.log("yo")
    var selectElement = event.target;
    var value = selectElement.value;
    selectElement.selectedIndex = -1;
    select_user_function(value)
}

function select_user_function(value){
    console.log(user_access_usernames)
    if (value != ""){
        if (user_access_usernames.includes(value)== false){
            const  user_text_div = document.createElement('div')
            user_access_usernames.push(value)
            console.log(user_access_usernames)
            var original_value = value
            console.log(original_value)
            if (value == "-"){
                value = "Use Parent Folder Permissions"
                user_text_div.style.backgroundColor = "#40798C"
            }
            if (value == "+-"){
                value = "Public"
                user_text_div.style.backgroundColor = "#40798C"
            }
            const  list_div = document.getElementsByClassName("list_area")[0]
            const  user_text = document.createElement('li')
            const x_button = document.createElement("i")
            x_button.id = original_value
            x_button.className = "fa-solid fa-x"
            x_button.addEventListener('click', function(user_text_div,original_value){
                this.parentElement.remove()
                original_value = this.id
                const index = user_access_usernames.indexOf(original_value);
                if (index > -1) { // only splice array when item is found
                    user_access_usernames.splice(index, 1); // 2nd parameter means remove one item only
                }

            })
            user_text_div.className = "user_access_div"
            user_text_div.appendChild(user_text)
            user_text_div.appendChild(x_button)
            user_text_div.background
            user_text.innerHTML = value
            list_div.appendChild(user_text_div)
            const input_value = document.getElementById("user_access_names")
            input_value.value = user_access_usernames
        }
    }
}


function routing_links(route_parts,base_url){
    length = route_parts.length
    current_url = base_url + "resources" + "/" + route_parts[0]
    iteration = 1

    for(let url_element =0; url_element < length; url_element++)
    {
        current_url = base_url + "resources" + "/" + route_parts[0]
        for(let url_part_index=1; url_part_index < iteration; url_part_index++){
            current_url = current_url + ">" + route_parts[url_part_index]
        }
        const link = document.createElement("a")
        link.href = current_url
        link.innerHTML = "/" + route_parts[url_element]
        link.setAttribute('id', "routing")
        console.log(link)
        const container = document.getElementById("routingdiv")
        container.appendChild(link)
        iteration = iteration + 1
    }
}

document.addEventListener("DOMContentLoaded", function(){
    url = decodeURI(window.location.href)
    url_parts = url.split("/")
    console.log(url_parts)
    console.log(url_parts)
    route = url_parts[4]
    route_parts = route.split(">")
    console.log(route_parts)
    console.log(route_parts.length)
    base_url=""
    for(let i = 0; i < 3; i++){
        base_url = base_url + url_parts[i] + "/"
    }
    console.log("base_url")
    console.log(base_url)
    routing_links(route_parts,base_url)
    if (route_parts.length > 1){
        console.log("yoo")
        let select_box = document.getElementsByClassName("dropdown_users")[0]
        const select_item = document.createElement("option")
        select_item.innerHTML = "Use Parent Folder Permissions"
        select_item.value = "-"
        console.log(select_item)
        select_box.prepend(select_item)
        const placeholder = document.getElementById("placeholder")
        placeholder.display = "none"
        select_user_function("-")
    }
});

async function deletion(){
    const response = await fetch('/deletion', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify({"ids":selected_elements_ids}) // body data type must match "Content-Type" header
    })
    const completion = await response.json()
    console.log(completion)
    if (completion == "denied"){
        console.log("made it")
        var text = "You do not own the rights to delete this object"
        alert(text)
        sleep(5000);
    }
    location.reload()
    return(completion)
}

function alert(text){
    const div = document.getElementsByClassName("alert_div")[0]
    div.style.display = "block"
    const alert_text = document.getElementById("alert_text")
    alert_text.innerText = text
}

function sleep(milliseconds) {
    const date = Date.now();
    let currentDate = null;
    do {
      currentDate = Date.now();
    } while (currentDate - date < milliseconds);
  }

