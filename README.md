# Studyist
#### Video Demo:  https://youtu.be/oK9QwVXk22A
#### Description:

>application.py

This is where all of the routing for the project is and the management of data.
The first page is called index in where it grabs user info to make an account
Then there is the login page which is where the form is submitted so that the user can login

>helper.py
This has al of the functions that are not routes


>hompage routing
This is the first page that comes up when the user logs in
it is where the user can submit a class name. if the class name doesn't exist, it renders apology
this renders the homepage.html template

>/<course>
This is a dynamic route in which the user can enter into a class through the url
if there is a form submitted which is when the user clicks the post button, it reroutes to the post version of this route
this renders the coursemain.html template

>/<course>/postcreation
This is where the user is sent when trying to create a post
after the post is created it returns back to to the >course routing
this renders the post.html template

>/<course>/post/<postid>
when a user clicks on a post that is on the >course route, it will send them to dynamic routing
the url has a specific id number for the post
this render the viewpost.html template


>apology.html
This takes an argument and return back the user to a page with an error that was found

>layout.html
This template is for all of the pages after the login or index routing. This controls where things go

>viewpost.html
This extends the layout.html, but it contains multiple variable. it grabs the info from the post and it grabs
the array with the replies. When you want to reply, I used a little bit of javascript to make the div a block
This made it have a appear affect


>static/homestyles
This is the styles for the homepage login screen or intro.html

>static/signup
This is the file for the signup at the first page

>static/styles.css
This is the styles for the pages after the signup

>purpose

This project is to help people who have had a hard time in thier classes and they need help from people
who already have experience in those classes.This project contains all highschoo courses and I might expand
but I made this project similar to other platforms but specifically targeted at school. I will continue updating it with new features and perhaps
I will release it.

>future
I am planning to have it have a feed. Also to organize the post by certain catagory. I also
want to publisize it and maybe make it so that it can connect schools and schools can compete with
each other. I want this website to be the center of education and drive within students. the future of
students is collaboration. I also wan ti to have a way so that people can find study partners and also have
a way so that you can login with google or another 1 click sign in. The website needs a new design, so maybe I will
make a new design for the website. I want a new searchbar because the autocorrect feature is cool, but the suggestions
look bad. I have a lot to work on, but this was both a frustrating project and a fun one. I learned a lot.