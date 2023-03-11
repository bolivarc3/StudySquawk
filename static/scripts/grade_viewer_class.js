document.addEventListener("DOMContentLoaded", function() {
    grade_average_calculator()
  });

function grade_average_calculator(){
    var total_score = 0
    var total_avalible_points = 0
    var grade_assignments_rows = document.getElementsByClassName("grade_assignment_data_row")
    console.log(grade_assignments_rows.length)
    for (var row = 0; row < grade_assignments_rows.length; row++){
        console.log("loop")
        var tds = grade_assignments_rows[row].querySelectorAll("td")
        var weight = parseFloat(tds[4].textContent)
        if (weight != 0){
            console.log("weight")
            console.log(weight)
            var score = tds[5].textContent
            if (score != ''){
                if (score == 'N'){
                    score = 0
                }
                score = parseFloat(score)
                total_score = total_score +  score
                total_avalible_points = total_avalible_points + parseFloat(tds[6].textContent)
            }
        }
    }
    console.log(total_score)
    console.log(total_avalible_points)
    var Grade_Average = total_score/total_avalible_points*100
    Grade_Average = Grade_Average.toFixed(3)
    const text = document.getElementsByClassName("grade_average")[0]
    text.innerHTML = Grade_Average
}