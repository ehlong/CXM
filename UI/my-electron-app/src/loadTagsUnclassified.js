

document.addEventListener("DOMContentLoaded", function() {
    loadImgs();
});


function loadImgs() { 
    let links = ["positive", "bugs", "security", "store", "wants", "junk"];

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
    
}