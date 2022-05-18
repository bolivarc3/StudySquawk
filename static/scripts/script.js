async function getData(){
    const data = await fetch('/getcourseposts', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify(course) // body data type must match "Content-Type" header
    })
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
        form.setAttribute("action", `/${posts[i][2]}/post/${posts[i][1]}`);
        form.setAttribute("name", `post-form${posts[i][3]}`)
        form.classList = "postbuttonform"
        form.setAttribute("type", "submit");

        var input = document.createElement("input")
        form.setAttribute("method", "POST");
        form.setAttribute("action", `/${posts[i][2]}/post/${posts[i][1]}`);
        form.setAttribute("name", `post-form${posts[i][3]}`)


        coursename = document.createElement("h5")
        coursename.innerText = `${posts[i][2]}`

        username = document.createElement("h5")
        username.innerText = `${posts[i][3]}`

        posttitle = document.createElement("h3")
        posttitle.innerText = `${posts[i][5]}`

        document.getElementById("postscontainer").appendChild(postdiv);
        postdiv.appendChild(form)
        postdiv.appendChild(coursename)
        postdiv.appendChild(username)
        postdiv.appendChild(posttitle)

    }
}