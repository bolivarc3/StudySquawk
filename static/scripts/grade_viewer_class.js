document.addEventListener("DOMContentLoaded", function() {
    // When the document loads, it begins to calculate the grades
    grade_average_calculator()
    //grabs the edit button and adds the click event to switch modes.
    var edit_button = document.getElementsByClassName("edit_mode_button")[0]
    edit_button.addEventListener('click', edit_mode)

    var add_row_button = document.getElementsByClassName("add_row")[0]
    add_row_button.addEventListener('click', function(){
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
    
                //When changed, it changes the color and recalculates the grade
                target_item.style.backgroundColor = '#B51515'
                grade_average_calculator()
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
          })
    }
  });

//Manages the edit modes based to the clicking of the button
function edit_mode(edit_button){

    //Grabs the nessary info from button and mode textbox
    var edit_button = document.getElementsByClassName("edit_mode_button")[0]
    var current_mode = document.getElementById("mode_text")
    current_mode_text = current_mode.textContent

    //Changes according to Current Mode
    if (current_mode_text == 'Viewer'){
        edit_button.innerText  = "Exit Edit Mode"
        current_mode.innerText = "Editor"
        var editable_data_cells = document.getElementsByClassName("grade_assignment_data")
        for(cell = 0; cell < editable_data_cells.length; cell++){
            editable_data_cells[cell].setAttribute('contenteditable', true);
        }
    }
    else{
        edit_button.innerText  = "Edit Grade"
        current_mode.innerText = "Viewer"
        var editable_data_cells = document.getElementsByClassName("grade_assignment_data")
        for(cell = 0; cell < editable_data_cells.length; cell++){
            editable_data_cells[cell].setAttribute('contenteditable', false);
        }
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
        if (Number.isNaN(parseFloat(tds[5].textContent)) == true || Number.isNaN(parseFloat(tds[6].textContent)) == true){
            tds[7].innerText = "%100.00"
        }
        else{
            tds[7].innerText = "%" + String((parseFloat(tds[5].textContent)/parseFloat(tds[6].textContent) * 100).toFixed(2))
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
    var Grade_Average = total_score/total_avalible_points*100
    //Fixes it to 3 decimal Points
    Grade_Average = Grade_Average.toFixed(3)
    //Sets the text element to Grade Average Number
    const text = document.getElementsByClassName("grade_average")[0]
    text.innerHTML = "%" + Grade_Average
}