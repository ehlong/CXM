
document.addEventListener("DOMContentLoaded", function() {
    loadTweetBoxes(9); 
    loadImgs();
    
});

let links = ["positive", "bugs", "security", "store", "wants", "junk"];
function loadImgs() { 
    //This function is just to insert image based on class.
    for (var link of links) { 
        //Grab all the elements with -link in them e.g class="positive-link"
        var tweetbox = document.getElementsByClassName(link + "-link"); 

        for(var i = 0; i < tweetbox.length ; i++) {
            //Since we have multiple tweets we need to run through all of them and insert the specific class image. In this class we just slapped a innerhtml and copy pasta
            tweetbox[i].innerHTML =   
            "<img class=\"" + link + "-gray\" src=\"../img/svgs/" + link + "-gray.svg\" alt=\"uncheck\" title=\" " + link.toUpperCase() + "\"/>" + "\n" +   
            "<img class=\"" + link + "-color\" src=\"../img/svgs/" + link + "-color.svg\" alt=\"check\" title=\"" + link.toUpperCase() + "\"/>";
        
        }
    }
}


function loadTweetBoxes (n) { 
    //  This function will load tweet boxes in by tweet 

    //  First grab the tag that we are inserting into
    let t_box = document.getElementsByClassName("TweetBox"); 

    //  Create simple loop for how many tweets we want to create a box for. 
    for(var i =1; i <= n; i++) { 
        // We create the outer div tag and set attributes 
        // ex <div id ="Tweet#1 class="tweet"> </div>"
        var tweet = document.createElement("div"); 
        tweet.setAttribute("id", "Tweet#" + i); 
        tweet.setAttribute("class", "tweet"); 
        
        //  Set the inner html elements, this is when tweet does not load(this should be over written when we grab tweets) 
        tweet.innerHTML = 
        "<h2>TweetID </h2>" + '\n' + 
        "<p> Tweet Stuffs </p>"; 

        //  create another div that will wrap entire thing into a wrapper and insert it
        var wrapper = document.createElement("div"); 
        wrapper.setAttribute("class", "tweet_wrapper");
        wrapper.appendChild(tweet);

        //We create inputs and insert it inside the wrapper div (this should be on same level as the tweet itself.)
        var checkboxes = getCheckBoxes(i); 
        wrapper.appendChild(checkboxes);

        //  Finally insert into html TweetBox from earlier.
        t_box.item(0).appendChild(wrapper);  
        


    }
    console.log(t_box.item(0)); 
}

function getCheckBoxes(n) { 
    //  Create <div class="inputBox"> </div> 
    var boxes = document.createElement("div");
    boxes.setAttribute("class","inputBox"); 
    
    //  Now for each class we make a input div with that specific classid and number an exmaple should be <input type="checkbox" id="positive1" name="classification1" value="positive"></input> 
    for ( link of links ) { 
        var box = document.createElement("input"); 
        box.setAttribute("type", "checkbox"); 
        box.setAttribute("id", link + n); 
        box.setAttribute("name", "classification" + n); 
        box.setAttribute("value", link); 

        //  Create label div <label for="bugs/glitches1"
        var l = document.createElement("label"); 
        if(link === "bugs") { 
            l.setAttribute("for", "bugs/glitches" + n); 
        }
        else { 
            l.setAttribute("for", link + n); 
        }
        //create a element <a class=positive-link>
        var a = document.createElement("a"); 
        a.setAttribute("class", link + "-link"); 

       
        //  Inside label element we append <a class=positive-link>
        l.appendChild(a);
        //  Iside input element we append label
        box.appendChild(l);

        //  inside of inputBox element we append input
        boxes.appendChild(box); 
    }
    //  Return all inputs elements for that specific number. This should return the inputBox that contains everything.
    return boxes; 

}