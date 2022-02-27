async function getresources(course){
    const response = await fetch('/getresources')
    const data = await response.json()
    console.log(data);
}

document.addEventListener('DOMContentLoaded', function(){
    getresources()
});
