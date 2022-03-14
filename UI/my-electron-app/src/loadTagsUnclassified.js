
document.addEventListener("DOMContentLoaded", function() {
    loadTweetBoxes(9); 
    loadImgs();
    
});

let links = ["positive", "bugs", "security", "store", "wants", "junk"];
function loadImgs() { 

    for (var link of links) { 
        var tweetbox = document.getElementsByClassName(link + "-link"); 
        // let coloredImg = document.createElement("img"); 
        // let grayImg = document.createElement("img"); 
        // coloredImg.setAttribute("class", link + "-color"); 
        // coloredImg.setAttribute("alt", "check"); 
        // coloredImg.setAttribute("title", link.toUpperCase()); 
        // coloredImg.src = "../img/svgs/" + link + "-color.svg"; 
        
        // grayImg.setAttribute("class", link + "-gray"); 
        // grayImg.setAttribute("alt", "check"); 
        // grayImg.setAttribute("title", link.toUpperCase()); 
        // grayImg.src = "../img/svgs/" + link + "-gray.svg"; 
        for(var i = 0; i < tweetbox.length ; i++) {
            tweetbox[i].innerHTML =   
            "<img class=\"" + link + "-gray\" src=\"../img/svgs/" + link + "-gray.svg\" alt=\"uncheck\" title=\" " + link.toUpperCase() + "\"/>" + "\n" +   
            "<img class=\"" + link + "-color\" src=\"../img/svgs/" + link + "-color.svg\" alt=\"check\" title=\"" + link.toUpperCase() + "\"/>";
        
        }
    }
}


function loadTweetBoxes (n) { 
    let t_box = document.getElementsByClassName("TweetBox"); 

    for(var i =1; i <= n; i++) { 
        var tweet = document.createElement("div"); 
        tweet.setAttribute("id", "Tweet#" + i); 
        tweet.setAttribute("class", "tweet"); 
        tweet.innerHTML = 
        "<h2>TweetID </h2>" + '\n' + 
        "<p> Tweet Stuffs </p>"; 
        console.log(tweet);
        t_box.item(0).appendChild(tweet)

        var checkboxes = getCheckBoxes(i); 
        t_box.item(0).appendChild(checkboxes); 


    }
    // console.log(t_box); 
}

function getCheckBoxes(n) { 
    var boxes = document.createElement("div");
    
    for ( link of links ) { 
        var box = document.createElement("input"); 
        box.setAttribute("type", "checkbox"); 
        box.setAttribute("id", link + n); 
        box.setAttribute("name", "classification" + n); 
        box.setAttribute("value", link + n); 

        var l = document.createElement("label"); 
        if(link === "bugs") { 
            l.setAttribute("for", "bugs/glitches" + n); 
        }
        else { 
            l.setAttribute("for", link + n); 
        }
        var a = document.createElement("a"); 
        a.setAttribute("class", link + "-link"); 

        l.appendChild(a); 
        box.appendChild(l); 
        boxes.appendChild(box); 
    }
    return boxes; 

}