/* <div class = "postdiv" type="submit" value = "{{ post[3] }}" onClick="document.forms['post-form{{ post[3] }}'].submit();">
            <!--each post is a submit button with a form -->
            <form name = "post-form{{ post[3] }}", class = "postbuttonform", action = "/{{ course }}/post/{{ post[0] }}", method = "POST">
                <input type="hidden" id="postId" name="postId" value="{{ post[0] }}">
            </form>
            <h5>
                {{ course }}
            </h5>
            <h5>
                {{ post[2] }}
            </h5>
            <br>
            <h3>
                {{ post[3] }}
            </h3>
            <!--each post is a submit button with a form -->
        </div> */






function loadposts(){
    var length = event.target.files.length;
    if(length > 0){
        //for the amount of images 
        for(let i = 0; i < length; i++){
            //
            const img = [];
            img[i] = document.createElement('img');
            img[i].src = URL.createObjectURL(event.target.files[i]);

            //makes a container for the seperate images
            const imagediv = [];
            imagediv[i] = document.createElement('div');
            imagediv[i].id = "imagecontainer" + i;
            imagediv[i].classList = "imagecontainer";

            const imagelist = [];
            imagelist[i] = document.createElement('li');
            imagelist[i].id = "imagelistelement" + i;
            //sets the images into the html
            document.getElementById("horizontal-list").appendChild(imagelist[i]);
            document.getElementById("imagelistelement" + i).appendChild(imagediv[i]);
            document.getElementById("imagecontainer" + i).appendChild(img[i]);
        }
    }
}