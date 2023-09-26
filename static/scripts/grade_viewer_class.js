document.addEventListener("DOMContentLoaded", function() {
    // When the document loads, it begins to calculate the grades
    grade_average_calculator()
    //This is the grade average box for when a calculation happens
    var grade_average_calculated = document.getElementsByClassName("grade_average")[0].innerHTML
    //grad average box of the base grade average
    const grade_average = document.getElementsByClassName("grade_average")[1]
    //set the grade averages together at the beginning since no change has happened
    grade_average.innerHTML = grade_average_calculated
    //grabs the edit button and adds the click event to switch modes.
    var edit_button = document.getElementsByClassName("edit_mode_button")[0]
    edit_button.addEventListener('click', edit_mode)

    //creates the adding of row system when a change happens
    var add_row_button = document.getElementsByClassName("add_row")[0]
    add_row_button.style.display = "none"
    add_row_button.addEventListener('click', function(){
        //grabes the table and creates the new row element
        const table = document.querySelector('.Grade_Data_Table_Body')
        const newrow = document.createElement('tr')
        newrow.className = "grade_assignment_data_row"

        //grabs the current date to add to the test assignment
        var today = new Date();
        var dd = String(today.getDate()).padStart(2, '0');
        var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
        var yyyy = today.getFullYear();
        date_text = mm +"/" + dd + "/" + yyyy

        //creates a template for the javascript to create the cells of the table
        cell_default_text = [date_text, "", "Test assignments", "Test", "1.00", "0.00", "0.00", "%100"]
        //for each cell
        for( var datacell = 0; datacell < 8; datacell++){
            //hides certains ones
            hiddencells=[0,1,4,7]
            const cell = document.createElement('td')
            //what happens if the cell is updated
            cell.addEventListener('input', function(event) {
                // Get the target element that triggered the event
                const target_item = event.target
                //update to the added classes

                grade_average_calculator()
                grab_changes()
            })
            
            //makes the cell content ediatable and changes the color to a color that makes the user able to see that it is a added_row
            cell.setAttribute('contenteditable', true)
            cell.style.backgroundColor = "#dba2d7"
            cell.className = "grade_assignments_data"
            cell.id = "added_row"
            cell.textContent = cell_default_text[datacell]
            if (hiddencells.includes(datacell)){
                cell.id = "show-mobile-table"
            }
            //append it to the row
            newrow.appendChild(cell)
        }
        //appends to the table
        table.prepend(newrow)
        //updates the changes on the table for saving
        grab_changes()
        
    })

    //button to clear the changes that was made
    var clear_changes = document.getElementsByClassName("clear_changes")[0]
    //default set to not showing , only when the edit is on
    clear_changes.style.display = 'none'
    clear_changes.addEventListener('click', function(){
        //grabs the keys for the local storage to reset them
        var course =  document.getElementById("course").textContent
        course = course.toString()
        added_rows_key = course + "_added_rows"

        //resets them
        localStorage.setItem(course,JSON.stringify(''))
        localStorage.setItem(added_rows_key,JSON.stringify(''))
        grab_grades()
    })
    //grabs all of the cell that modify the grade average
    var rows = document.getElementsByClassName("grade_assignment_data_row")
    for(var row_index = 0; row_index < rows.length; row_index++){
        let cells = rows[row_index].getElementsByTagName("td")
        for(i=0; i < cells.length; i++){
            //adds listner to check for changes in input for automatic average grading
            cells[i].addEventListener('input', function(event) {
                // Get the target element that triggered the event
                const target_item = event.target

                //When changed, it changes the color and recalculates the grade
                if(target_item.style.backgroundColor != "rgb(219, 162, 215)"){
                    target_item.style.backgroundColor = '#B51515'
                }
                grade_average_calculator()
                grab_changes()
                // saving_edited_table()
                // localStorage.getItem("name");
                //When changed, it changes the color and recalculates the grade
            })
    }
    }
  });

function grab_changes(){
    course =  document.getElementById("course").textContent
    storage_key = course.toString()
    added_rows_storage_key = storage_key + "_added_rows"
    var rows = document.getElementsByClassName("grade_assignment_data_row")
    var added_rows = []
    var assignments = {}
    for(var row_index = 0; row_index < rows.length; row_index++){ 
        var data_cell = []
        var data_cell_added_rows = []
        let cells = rows[row_index].getElementsByTagName("td")
        change = false
        added_table_change = false
        for (var i = 0; i < cells.length; i++) {
            var current_cell = cells[i]
            var color = current_cell.style.backgroundColor
            if (color != ""){
                if (color == "rgb(219, 162, 215)"){
                    data_cell_added_rows.push(current_cell.innerHTML)
                    added_table_change = true
                }
                else{
                    data_cell.push(current_cell.innerHTML)
                    change = true 
                }
            }
            else{
                data_cell.push("null")
            }
        }
        if (change == true){
            var assignment_name = cells[2].innerHTML
            assignments[assignment_name] = data_cell
        }
        if (added_table_change == true){
            added_rows.push(data_cell_added_rows)
        }
        added_table_change = false
        data_cell_added_rows = []
        data_cell=[]
    }
    localStorage.setItem(added_rows_storage_key,JSON.stringify(added_rows))
    localStorage.setItem(course,JSON.stringify(assignments))
    // edit_with_saved_changes()
}

function edit_with_saved_changes(){
    course =  document.getElementById("course").textContent
    storage_key = course.toString()
    saved_data = JSON.parse(localStorage.getItem(storage_key))
    console.log(saved_data)
    if (saved_data != null){
        keys = Object.keys(saved_data) 
        var rows = document.getElementsByClassName("grade_assignment_data_row")
        var assignments = {}
        for(var row_index = 0; row_index < rows.length; row_index++){
            var data_cell = []
            let cells = rows[row_index].getElementsByTagName("td")
            change = false
            if (keys.includes(cells[2].innerHTML) == true){
                assignment_name = cells[2].innerHTML
                assignment_data = saved_data[assignment_name]
                for(var i=0; i < cells.length; i++){
                    if (assignment_data[i] != "null"){
                        cells[i].innerHTML = assignment_data[i]
                        cells[i].style.backgroundColor= "#B51515"
                    }
                }
            }
        }
        create_added_saved_rows()
    }
}

function create_added_saved_rows(){
    course =  document.getElementById("course").textContent
    course = course.toString()
    storage_key = course + "_added_rows"
    saved_data = JSON.parse(localStorage.getItem(storage_key))
    console.log(saved_data)
    for(var added_row_index = 0; added_row_index<saved_data.length; added_row_index++){
        const table = document.querySelector('.Grade_Data_Table_Body')
        const newrow = document.createElement('tr')
        newrow.className = "grade_assignment_data_row"

        var today = new Date();
        var dd = String(today.getDate()).padStart(2, '0');
        var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
        var yyyy = today.getFullYear();
        date_text = mm +"/" + dd + "/" + yyyy
        cell_default_text = [date_text, "", "Test assignments", "Test", "1.00", "0.00", "0.00", "%100"]
        for( var datacell = 0; datacell < 8; datacell++){
            hiddencells=[0,1,4,7]
            const cell = document.createElement('td')
            cell.addEventListener('input', function(event) {
                // Get the target element that triggered the event
                const target_item = event.target
                //update to the added classes
                if(target_item.style.backgroundColor != "rgb(219, 162, 215)"){
                    target_item.style.backgroundColor = '#B51515'
                }
                grade_average_calculator()
                grab_changes()

            })
            cell.setAttribute('contenteditable', true)
            cell.style.backgroundColor = "#dba2d7"
            cell.className = "grade_assignments_data"
            cell.textContent = saved_data[added_row_index][datacell]
            if (hiddencells.includes(datacell)){
                cell.id = "show-mobile-table"
            }
            newrow.appendChild(cell)
        }
        table.prepend(newrow)
    }
}


//Manages the edit modes based to the clicking of the button
function edit_mode(edit_button){

    //Grabs the nessary info from button and mode textbox
    var edit_button = document.getElementsByClassName("edit_mode_button")[0]
    var current_mode = document.getElementById("mode_text")
    current_mode_text = current_mode.textContent

    //Changes according to Current Mode
    if (current_mode_text == 'Viewer'){
        var clear_changes = document.getElementsByClassName("clear_changes")[0]
        clear_changes.style.display = 'block'
        var add_row = document.getElementsByClassName("add_row")[0]
        add_row.style.display = "block"
        var course_name = document.getElementById("course").textContent
        key_name = 'grades_modified' + course_name
        var table_unfiltered = localStorage.getItem(key_name)
        table = JSON.parse(table_unfiltered)
        edit_with_saved_changes()
        contenteditable()
        // create_table(table)
        edit_button.innerText  = "Exit Edit Mode"
        current_mode.innerText = "Editor"
        var editable_data_cells = document.getElementsByClassName("grade_assignments_data")
        for(cell = 0; cell < editable_data_cells.length; cell++){
            editable_data_cells[cell].setAttribute('contenteditable', true);
        }
        grade_average_calculator()
    }
    else{
        console.log("ther other one")
        var clear_changes = document.getElementsByClassName("clear_changes")[0]
        clear_changes.style.display = 'none'
        var add_row = document.getElementsByClassName("add_row")[0]
        add_row.style.display = "none"
        var course_name = document.getElementById("course").textContent
        key_name = 'current_grades' + course_name
        table = JSON.parse(localStorage.getItem(key_name))
        grab_grades()
        notcontenteditable()
        // create_table(table)
        edit_button.innerText  = "Edit Grade"
        current_mode.innerText = "Viewer"
        var editable_data_cells = document.getElementsByClassName("grade_assignments_data")
        for(cell = 0; cell < editable_data_cells.length; cell++){
            editable_data_cells[cell].setAttribute('contenteditable', false);
        }
        grade_average_calculator()
    }
}

function contenteditable(){
    var rows = document.getElementsByClassName("grade_assignment_data_row")
    for(var row_index = 0; row_index < rows.length; row_index++){
        let cells = rows[row_index].getElementsByTagName("td")
        for (var i = 0; i < cells.length; i++) {
            cells[i].contentEditable = "true"
        }
    }
}

function notcontenteditable(){
    var rows = document.getElementsByClassName("grade_assignment_data_row")
    for(var row_index = 0; row_index < rows.length; row_index++){
        let cells = rows[row_index].getElementsByTagName("td")
        for (var i = 0; i < cells.length; i++) {
            cells[i].contentEditable = "false"
        }
    }
}

function create_table(table){ 
    const table_body = document.querySelector('.Grade_Data_Table_Body')
    table_body.innerHTML = ''
    var length = table.length
    for(let i=0;i<length;i++){
        const newrow = document.createElement('tr')
        newrow.className = "grade_assignment_data_row"

        var today = new Date();
        var dd = String(today.getDate()).padStart(2, '0');
        var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
        var yyyy = today.getFullYear();
        date_text = mm +"/" + dd + "/" + yyyy
        cell_default_text = [date_text, "", "Test assignments", "Test", "1.00", "0.00", "0.00", "%100"]
        arrangement = [0,1,2,3,6,4,5,9]
        for(let datacell = 0; datacell < 8; datacell++){
            hiddencells=[0,1,4,7]
            const cell = document.createElement('td')
            cell.addEventListener('input', function(event) {
                // Get the target element that triggered the event
                const target_item = event.target
                //update to the added classes
                if(target_item.style.backgroundColor != "rgb(219, 162, 215)"){
                    if(target_item.style.backgroundColor != "rgb(219, 162, 215)"){
                        target_item.style.backgroundColor = '#B51515'
                    }
                }
                grade_average_calculator()
                grab_changes()

            })
            cell.setAttribute('contenteditable', true)
            cell.className = "grade_assignments_data"
            if (hiddencells.includes(datacell)){
                cell.id = "show-mobile-table"
            }
            current_cell_color = table[i][datacell]
            if (current_cell_color == 'modified'){
                cell.style.backgroundColor="#B51515"
            }
            current_cell_text = table[i][arrangement[datacell]]
            cell.textContent = current_cell_text
            newrow.appendChild(cell)
        }
        table_body.appendChild(newrow)
    }
}

function grade_average_calculator(){
    //Caculates score by adding all valid score points and deviding by total availble points
    var total_score = 0
    var total_avalible_points = 0

    //Looks through every row of the data table
    var grade_assignmentss_rows = document.getElementsByClassName("grade_assignment_data_row")
    for (var row = 0; row < grade_assignmentss_rows.length; row++){
        //grabs all of the table data
        var tds = grade_assignmentss_rows[row].querySelectorAll("td")

        //Checks to see if it is a Valid Number
        if (Number.isNaN(parseFloat(tds[5].textContent)) == true || Number.isNaN(parseFloat(tds[6].textContent)) == true)
        {
            tds[7].innerText = "%100.00"
        }
        else{
            tds[7].innerText = "%" + String(parseFloat(tds[5].textContent)/parseFloat(tds[6].textContent) * 100)
        }

        //Checks to see if the Grade acutally has any weight that applies to it
        var weight = parseFloat(tds[4].textContent)
        var category = tds[3].textContent
        if (weight != 0 && category != "Practice"){
            var score = parseFloat(tds[5].textContent)
            total_score_add = parseFloat(tds[6].textContent)
            //Checks if the score is not empty or is a code letter
            if(score == 'N'){
                score = 0
            }
            if(isNaN(score)){
                score = 0
                total_score_add = 0
            }
            //Adds the score to total score and adds the total availbile points
            total_score = total_score +  score
            total_avalible_points = total_avalible_points + total_score_add
        }
    }

    //Calculates the Grade Average 
    var Grade_Average = (total_score/total_avalible_points)*100
    //Fixes it to 3 decimal Points
    Grade_Average = Grade_Average.toFixed(3)
    //Sets the text element to Grade Average Number
    const grade_average_after_change = document.getElementsByClassName("grade_average")[0]
    grade_average_after_change.innerHTML = Grade_Average + "%"

    var grade_average_current = document.getElementsByClassName("grade_average")[1].textContent.toString()
    grade_average_current = grade_average_current.replace('%','');
    const percent_change_cell = document.getElementById("percent_change_cell")
    const percentage_change_text = document.getElementsByClassName("percentage_change_text")[0]
    var percentage_change = parseFloat((Grade_Average - parseFloat(grade_average_current)).toFixed(2))
    if (percentage_change < 0){
        percent_change_cell.className = "percent_change_cell negative"
        percentage_change_text.innerHTML = percentage_change + "%"
    }
    else if (percentage_change > 0){
        percent_change_cell.className = "percent_change_cell positive"
        percentage_change_text.innerHTML = "+" + percentage_change + "%"
    }
    else if (percentage_change == 0){
        percent_change_cell.className = "percent_change_cell nuetral"
        percentage_change_text.innerHTML = percentage_change + "%"
    }

}

async function grab_grades(){
    const course =  document.getElementById("course").textContent
    var course_name = course.toString()
    const response = await fetch('/grab_course_grades', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify(course_name) // body data type must match "Content-Type" header
    })
    const data = await response.json()
    create_table(data)
    grade_average_calculator()

}