
var calendar;
var month;
var year;
var month_list = ["January","February","March","April","May","June","July","August","September","October","November","December"];
async function grab_user_info(){
    const response = await fetch("/gethacattendance", {
        method:"POST"
    });
    var attendance_info = await response.json();
    const months = Object.keys(attendance_info);
    const d = new Date();
    month = d.getMonth();
    year = d.getFullYear();
    calendar = attendance_info
    main(attendance_info, month, year)
}

document.addEventListener("DOMContentLoaded", function() {
    const status_element = document.getElementById("status")
    status_element.innerHTML = "Loading . . ."
    grab_user_info()
    document.getElementById("back_attendance").addEventListener('click',function(){
        const calendarbody = document.getElementById("calendarbody");
            while (calendarbody.firstChild) {
                calendarbody.removeChild(calendarbody.lastChild);
            }
        if (month-1 >= 0){
            month = month -1
        }
        else{
            month = month_list.length-1
            year = year-1
        }
        main(calendar,month,year)
    })
    document.getElementById("forward_attendance").addEventListener('click',function(){
        const calendarbody = document.getElementById("calendarbody");
        while (calendarbody.firstChild) {
            calendarbody.removeChild(calendarbody.lastChild);
        }
        if (month+1 <= month_list.length-1){
            month = month +1
        }
        else{
            month = 0
            year = year+1
        }
        main(calendar,month,year)
    })
})

function main(calendar,month,year){
    const status_element = document.getElementById("status")
    status_element.innerHTML = ""
    var attendance_info = calendar['attendance']
    var current_month_year = String(month_list[month]) + " " + String(year)
    status_element.innerHTML = current_month_year
    var current_month = attendance_info[current_month_year]
    const calendar_body = document.getElementById("calendarbody")
    for(row=0; row<current_month.length; row++){
        const created_row = document.createElement('tr')
        for(day = 0; day < current_month[row].length; day++){
            const day_cell = document.createElement("td")
            var current_day_number = String(current_month[row][day][0]).replaceAll(',','')
            var current_day_event = String(current_month[row][day][1]).replaceAll(',','')
            event_coloring(day_cell, current_day_event)
            day_cell.innerHTML =  current_day_number
            created_row.appendChild(day_cell)
        }
        calendar_body.appendChild(created_row)
    }
}

function event_coloring(day_cell, current_day_event){
    var event = current_day_event.toLowerCase()
    if (event.includes("absent") == true){
        day_cell.style.backgroundColor = "red";
    }
    if (event.includes("school business") == true){
        day_cell.style.backgroundColor = "blue";
    }
    if (event.includes("parent note") == true){
        day_cell.style.backgroundColor = "green";
    }
}