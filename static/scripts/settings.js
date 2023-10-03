function edit_mode(){
    const submit_button = document.getElementById("passwordsubmitbutton")
    const password_input = document.getElementById("password_redo")
    var visibility = submit_button.style.visibility
    if (visibility == "hidden"){
        password_input.disabled = false
        password_input.value = ""
        submit_button.style.visibility = "visible"
    }
    else{
        password_input.disabled = true
        submit_button.style.visibility = "hidden"
    }
}

function delete_post(post_id){
    deletion_post(post_id)
}

async function deletion_post(post_id){
    const response = await fetch('/delete_post', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify({"post_id":post_id}) // body data type must match "Content-Type" header
    })
    location.reload()
}