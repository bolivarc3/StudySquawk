document.addEventListener("DOMContentLoaded", function() {
    // When the document loads, it begins to calculate the grades
    grade_average_calculator()
    var grade_average_calculated = document.getElementsByClassName("grade_average")[0].innerHTML
    localStorage.setItem("grade_average","grade_average")
    const grade_average = document.getElementsByClassName("grade_average")[1]
    grade_average.innerHTML = grade_average_calculated
    var course_name = document.getElementById("course").textContent
    key_name = 'grades_modified' + course_name
    if (localStorage.getItem(key_name) == null) {
        saving_edited_table()
    }
    key_name = 'current_grades' + course_name
    var current_table = grab_table()
    localStorage.setItem(key_name,JSON.stringify(current_table));
    //grabs the edit button and adds the click event to switch modes.
    var edit_button = document.getElementsByClassName("edit_mode_button")[0]
    edit_button.addEventListener('click', edit_mode)

    var add_row_button = document.getElementsByClassName("add_row")[0]

    add_row_button.addEventListener('click', function(){
        const status = document.getElementById("mode_text")
        var status_text = status.innerText
        if (status_text == "Viewer"){
            return (0)
        }
        const table = document.querySelector('.Grade_Data_Table_Body')
        const newrow = document.createElement('tr')
        newrow.className = "grade_assignment_data_row"

        var today = new Date();
        var dd = String(today.getDate()).padStart(2, '0');
        var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
        var yyyy = today.getFullYear();
        date_text = mm +"/" + dd + "/" + yyyy
        cell_default_text = [date_text, "", "Test Assignment", "Test", "1.00", "0.00", "0.00", "%100"]
        for(datacell = 0; datacell < 8; datacell++){
            hiddencells=[0,1,4,7]
            const cell = document.createElement('td')
            cell.addEventListener('input', function(event) {
                // Get the target element that triggered the event
                const target_item = event.target
                //update to the added classes
                
                target_item.style.backgroundColor = '#B51515'
                grade_average_calculator()
                saving_edited_table()

              })
            cell.setAttribute('contenteditable', true)
            cell.className = "grade_assignment_data"
            if (hiddencells.includes(datacell)){
                cell.id = "show-mobile-table"
            }
            newrow.appendChild(cell)
        }
        table.prepend(newrow)
        
    })
    //grabs all of the cell that modify the grade average
    var cell_data_change = document.getElementsByClassName("grade_assignment_data")
    for(i=0; i < cell_data_change.length; i++){
        //adds listner to check for changes in input for automatic average grading
        cell_data_change[i].addEventListener('input', function(event) {
            // Get the target element that triggered the event
            const target_item = event.target

            //When changed, it changes the color and recalculates the grade
            target_item.style.backgroundColor = '#B51515'
            grade_average_calculator()
            saving_edited_table()
            // localStorage.getItem("name");
            //When changed, it changes the color and recalculates the grade
          })
    }
  });

function saving_edited_table(){

    var course_name = document.getElementById("course").textContent
    var stringified = JSON.stringify(current_table)
    localStorage.setItem(key_name,stringified);
    key_name = 'grades_modified' + course_name
    var current_table = grab_table()
    stringified =  JSON.stringify(current_table)
    localStorage.setItem(key_name,stringified);
}

function grab_table(){
    var rows = document.getElementsByClassName("grade_assignment_data_row");
    const grade_table_data = []
    let current_row = []
    let data=[]
    for (var row=0; row < rows.length; row++) {
        //iterate through rows
        //rows would be accessed using the "row" variable assigned in the for loop
        const data_cell = []
        let cells = rows[row].getElementsByTagName("td")
        for (var i = 0; i < cells.length; i++) {
            //iterate through columns
            //columns would be accessed using the "col" variable assigned in the for loop
            var current_cell = cells[i]
            var color = current_cell.style.backgroundColor
            if (color != ""){
              data.push("modified")
              data.push(current_cell.innerHTML)
            }
            else{
              data.push("")
              data.push(current_cell.innerHTML)
            }
            current_row.push(data)
            data=[]
        }
        // console.log(current_row)
        grade_table_data.push(current_row)
        current_row = []
    }
    return grade_table_data
}

//Manages the edit modes based to the clicking of the button
function edit_mode(edit_button){

    //Grabs the nessary info from button and mode textbox
    var edit_button = document.getElementsByClassName("edit_mode_button")[0]
    var current_mode = document.getElementById("mode_text")
    current_mode_text = current_mode.textContent

    //Changes according to Current Mode
    if (current_mode_text == 'Viewer'){
        var course_name = document.getElementById("course").textContent
        key_name = 'grades_modified' + course_name
        var table_unfiltered = localStorage.getItem(key_name)
        table = JSON.parse(table_unfiltered)
        create_table(table)
        
        edit_button.innerText  = "Exit Edit Mode"
        current_mode.innerText = "Editor"
        var editable_data_cells = document.getElementsByClassName("grade_assignment_data")
        for(cell = 0; cell < editable_data_cells.length; cell++){
            editable_data_cells[cell].setAttribute('contenteditable', true);
        }
        grade_average_calculator()
    }
    else{
        var course_name = document.getElementById("course").textContent
        key_name = 'current_grades' + course_name
        table = JSON.parse(localStorage.getItem(key_name))
        create_table(table)

        edit_button.innerText  = "Edit Grade"
        current_mode.innerText = "Viewer"
        var editable_data_cells = document.getElementsByClassName("grade_assignment_data")
        for(cell = 0; cell < editable_data_cells.length; cell++){
            editable_data_cells[cell].setAttribute('contenteditable', false);
        }
        grade_average_calculator()
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
        cell_default_text = [date_text, "", "Test Assignment", "Test", "1.00", "0.00", "0.00", "%100"]
        for(let datacell = 0; datacell < 8; datacell++){
            hiddencells=[0,1,4,7]
            const cell = document.createElement('td')
            cell.addEventListener('input', function(event) {
                // Get the target element that triggered the event
                const target_item = event.target
                //update to the added classes
                
                target_item.style.backgroundColor = '#B51515'
                grade_average_calculator()
                saving_edited_table()

            })
            cell.setAttribute('contenteditable', true)
            cell.className = "grade_assignment_data"
            if (hiddencells.includes(datacell)){
                cell.id = "show-mobile-table"
            }
            current_cell_color = table[i][datacell][0]
            if (current_cell_color == 'modified'){
                cell.style.backgroundColor="#B51515"
            }
            current_cell_text = table[i][datacell][1]
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
    var grade_assignments_rows = document.getElementsByClassName("grade_assignment_data_row")
    for (var row = 0; row < grade_assignments_rows.length; row++){
        //grabs all of the table data
        var tds = grade_assignments_rows[row].querySelectorAll("td")

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
        if (weight != 0){
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

async function save_calculations(){
    const rows = Array.from(document.getElementsByClassName('rowbox'))
    rows.forEach(row =>{
        row.remove();
    });
    const response = await fetch('grade_save_calculations', {
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