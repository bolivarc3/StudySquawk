/* <div class = "postdiv" type="submit" value = "{{ post[3] }}" onClick="document.forms['post-form{{ post[3] }}'].submit();">
            <!--each post is a submit button with a form -->
            <form name = "post-form{{ post[3] }}", class = "postbuttonform", action = "/{{ course }}/post/{{ post[0] }}", method = "POST">
                <input type="hidden" id="postId" name="postId" value="{{ post[0] }}">
            </form>
            <h5>
                {{ course }}
            </h5>
            <h5>
                {{ post[2] }}
            </h5>
            <br>
            <h3>
                {{ post[3] }}
            </h3>
            <!--each post is a submit button with a form -->
        </div> */






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