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



function loadposts(posts){
    console.log("hello")
    console.log(posts)
    length = posts.length

    for(let i = 0; i < length; i++){
        //postscontainer
        postdiv = document.createElement('div');
        postdiv.classList = "postdiv";
        postdiv.setAttribute("onclick",`document.forms['post-form${posts[i][3]}'].submit()`);


        var form = document.createElement("form")
        form.setAttribute("method", "POST");
        form.setAttribute("action", `/${posts[i][1]}/post/${posts[i][0]}`);
        form.setAttribute("name", `post-form${posts[i][3]}`)
        form.classList = "postbuttonform"
        form.setAttribute("type", "submit");

        var input = document.createElement("input")
        form.setAttribute("method", "POST");
        form.setAttribute("action", `/${posts[i][1]}/post/${posts[i][0]}`);
        form.setAttribute("name", `post-form${posts[i][3]}`)


        coursename = document.createElement("h5")
        coursename.innerText = `${posts[i][1]}`

        username = document.createElement("h5")
        username.innerText = `${posts[i][2]}`

        posttitle = document.createElement("h3")
        posttitle.innerText = `${posts[i][3]}`

        document.getElementById("postscontainer").appendChild(postdiv);
        postdiv.appendChild(form)
        postdiv.appendChild(coursename)
        postdiv.appendChild(username)
        postdiv.appendChild(posttitle)

    }
}