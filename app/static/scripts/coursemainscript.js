
async function getcourseposts(course){
    const response = await fetch('/getcourseposts', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify(course) // body data type must match "Content-Type" header
    })
    const data = await response.json()
    console.log("hello")
    console.log(data)
    loadposts(data)
}




