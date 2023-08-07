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