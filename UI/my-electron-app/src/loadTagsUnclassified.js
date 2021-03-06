
let links = ["positive", "bugs", "security", "store", "wants", "junk"];
function loadImgs() { 
    //This function is just to insert image based on class.
    for (var link of links) { 
        //Grab all the elements with -link in them e.g class="positive-link"
        var tweetbox = document.getElementsByClassName(link + "-link"); 

        for(var i = 0; i < tweetbox.length ; i++) {
            //Since we have multiple tweets we need to run through all of them and insert the specific class image. 
            //In this class we just slapped a innerhtml and copy pasta
            tweetbox[i].innerHTML =   
            "<img class=\"" + link + "-gray\" src=\"../img/svgs/" + link + "-gray.svg\" alt=\"uncheck\" title=\" " + link.toUpperCase() + "\"/>" + "\n" +   
            "<img class=\"" + link + "-color\" src=\"../img/svgs/" + link + "-color.svg\" alt=\"check\" title=\"" + link.toUpperCase() + "\"/>";
        }
    }
}

let inferred = 1;
let link;
function getCheckBoxes(n, tweets) { 
    //  Create <div class="inputBox"> </div> 
    var boxes = document.createElement("div");
    boxes.setAttribute("class","inputBox"); 
    //  Now for each class we make a input div with that specific classid and number an exmaple should be <input type="checkbox" id="positive1" name="classification1" value="positive"></input>

    for ( link of links ) {
        var box = document.createElement("input");
        box.setAttribute("type", "checkbox"); 
        box.setAttribute("id", link + n); 
        box.setAttribute("name", link); 
        // box.setAttribute("value", "");
        box.setAttribute("class", n);

        //Check if tweet is there and if it matches with class, mark as checked.
        if(tweets != null) {
            if(typeof tweets['class'] === 'string') { 
                if(tweets['class'] === link || (tweets['class'] === "bugs/glitches" && link === "bugs")) {
                    //box.setAttribute("onchange", "checkInferred(" + link +  n + ");");
                    box.setAttribute("value", n); 
                    box.checked = true; 
                    } 
            }
            else if(Array.isArray(tweets['class'])) { 
                if(tweets['class'].includes(link) || tweets['class'].includes("bugs/gltiches") && link == "bugs")  { 
                    box.setAttribute("onchange", "checkInferred(" + link +  n + ");");
                    box.setAttribute("value", n); 
                    box.cehcked = true; 
                }
                
            }
            box.setAttribute("onchange", "checkInferred(" + link +  n + ");");

        } 

        //  Create label div <label for="bugs/glitches1"
        var l = document.createElement("div"); 
        if(link === "bugs") { 
            l.setAttribute("for", "bugs/glitches" + n); 
        }
        else { 
            l.setAttribute("for", link + n); 
        }
        //create a element <a class=positive-link>
        var a = document.createElement("label"); 
        a.setAttribute("class", link + "-link"); 
        a.setAttribute("for", link+n); 

       
        //  Inside label element we append <a class=positive-link>
        // l.appendChild(box);
        // l.appendChild(a); 
        //  Iside input element we append label
        //box.appendChild(l);

        //  inside of inputBox element we append input
    
        boxes.appendChild(box);
        boxes.appendChild(a);

    }
    //  Return all inputs elements for that specific number. This should return the inputBox that contains everything.
    return boxes; 
}

function checkInferred(c) {
    let id = c.className;
    let tweetInferred = document.getElementById("tweet_inferred" + id);
    let inferred = false;
    let inputs = document.getElementsByClassName(id); 

    var a = [] 
    var b = [] 

    for( var i of inputs) { 
        if(i.hasAttribute('value')) { 
            a.push(i.name);
        }
    }
    for(var i of inputs) { 
        if(i.checked == true) { 
            b.push(i.name); 
        }
    }
    console.log(a);
    console.log(b); 
    if (a.sort().toString() == b.sort().toString()) { 
        tweetInferred.innerHTML = "&#129302;";
    }
    else { 
        tweetInferred.innerHTML = ""; 
    }
}

function get_new_tweets() {
    try { 
        var n = document.getElementById("new_tweets_num"); 
        if(n.value < 1 || n.value > 30 )  {
            alert("Values only between 1-30!");
        }
        else { 
            var tweet_box = document.getElementById("TweetTable");
            tweet_box.innerHTML =
                "<tr>" +
                "<th>Tweet ID</th>" +
                "<th>Date</th>" +
                "<th>Tweet</th>" +
                "<th>Inferred</th>" +
                "<th>Class</th>" + "</tr>";
            // loadTweetBoxes(n.value); 
            httpGetAsync("http://127.0.0.1:5000/unclassified/" + n.value, get_tweet_callback);
        }
    }
    catch { 
        console.log("error occured"); 
    }
}
