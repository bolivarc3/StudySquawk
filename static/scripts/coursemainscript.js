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






