async function getData(){
    const data = await fetch('/getcourseposts', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify(course) // body data type must match "Content-Type" header
    })
    ;
}
async function updatehac(){
    const data = await fetch('/update_hac', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
    ;
}


function loadposts(posts){
    length = posts.length

    for(let i = 0; i < length; i++){
        //postscontainer
        postdiv = document.createElement('div');
        postdiv.classList = "postdiv";
        postdiv.setAttribute("onclick",`document.forms['post-form${posts[i][1]}'].submit()`);


        var form = document.createElement("form")
        form.setAttribute("method", "POST");
        form.setAttribute("action", `/${posts[i][2]}/post/${posts[i][1]}`);
        form.setAttribute("name", `post-form${posts[i][1]}`)
        form.classList = "postbuttonform"
        form.setAttribute("type", "submit");

        var input = document.createElement("input")
        form.setAttribute("method", "POST");
        form.setAttribute("action", `/${posts[i][2]}/post/${posts[i][1]}`);
        form.setAttribute("name", `post-form${posts[i][1]}`)


        coursename = document.createElement("h5")
        coursename.innerText = `${posts[i][2]}`

        username = document.createElement("h5")
        username.innerText = `${posts[i][3]}`

        posttitle = document.createElement("h3")
        posttitle.innerText = `${posts[i][4]}`

        document.getElementById("postscontainer").appendChild(postdiv);
        postdiv.appendChild(form)
        postdiv.appendChild(coursename)
        postdiv.appendChild(username)
        postdiv.appendChild(posttitle)

    }
}

document.addEventListener("DOMContentLoaded", function(e){
    character_limiting()
})

function character_limiting(){
    var digitPeriodRegExp = new RegExp(/\/|>|\\/g);
    let inputs = document.getElementsByClassName("limited_form")
    for(let i = 0; i < inputs.length; i++){
        input = inputs[i]
        input.addEventListener('input', function(event) {
            let result = true
            while (result == true){
                input = event.target
                var splitValue = input.value.split('');
                var charactersToFilter = 0;
                var filteredSplitValue = splitValue.map(function(character) {
                        let result = digitPeriodRegExp.test(character)
                        if(result) {
                            charactersToFilter++;
                            return '';
                        }
                    
                        return character;
                    });
                
                if(!charactersToFilter) {
                    return;
                }
                
                input.value = filteredSplitValue.join('');
                
                /*
                * We need to keep track of the caret position, which is the `selectionStart`
                * property, otherwise if our caret is in the middle of the value, pressing an
                * invalid character would send our caret to the end of the value.
                */
                var charactersBeforeSelectionStart = filteredSplitValue.slice(0, input.selectionStart);
                var filteredCharactersBeforeSelectionStart = charactersBeforeSelectionStart.filter(function(character) {
                        return !character;
                    });
                var totalFilteredCharactersBeforeSelectionStart = filteredCharactersBeforeSelectionStart.length;
                var newSelectionStart = input.selectionStart - totalFilteredCharactersBeforeSelectionStart;
                
                input.selectionStart = newSelectionStart;
                input.selectionEnd = input.selectionStart;
            }
        })
    }

}