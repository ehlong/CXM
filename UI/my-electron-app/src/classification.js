// parses the data from a get request for unclassified tweets
var all_data = {}; 
let range = [0,10]; 

function showPage() {
    document.getElementById("loader").style.display = "none";
    document.getElementById("divForFetch").style.display = "block";
    document.getElementById("loader-container").style.display = "none"; 
}

function get_tweet_callback(data) {

  let tweets = JSON.parse(data)
  all_data = tweets; 
  var i = 1;

  for(var key in tweets) {
    let elementId = "Tweet#" + (i).toString();

    let table = document.getElementById("TweetTable");
    let row = document.createElement("tr");
    row.setAttribute("id", elementId); 
    let tweetKey = document.createElement("td");
    tweetKey.setAttribute("id", "tweet_id"); 
    tweetKey.innerHTML = key;
    let tweetDate = document.createElement("td");
    tweetDate.setAttribute("id", "tweet_date"); 
    tweetDate.innerHTML = tweets[key]['date']
    let tweetText = document.createElement("td")
    tweetText.setAttribute("id", "tweet_text");
    tweetText.innerHTML = tweets[key]['text'];
    let tweetInferred = document.createElement("td");
    tweetInferred.setAttribute("id", "tweet_inferred" + key);
    tweetInferred.innerHTML = "&#129302;";

    let boxes = document.createElement("td")
    boxes.setAttribute("class", "inputBox_wrapper"); 

    var checkboxes = getCheckBoxes(key, tweets[key]);
    boxes.appendChild(checkboxes);

    row.appendChild(tweetKey);
    row.appendChild(tweetDate);
    row.appendChild(tweetText);
    row.appendChild(tweetInferred);
    row.appendChild(boxes);
    table.appendChild(row);

      ++i;
    if(i > range[1]) { 
        break;
    }
  }
  loadImgs();
  showPage();
}

function nextPage(n) { 
    if( (n > 0 && range[1] == Object.keys(all_data).length) || (n < 0 && range[0] <= 0)) { 
        return
    }

    range[0] += n;
    range[1] += n;
    var i = 0; 
    let table = document.getElementById("TweetTable");
    table.innerHTML = "" 
    for(var key in all_data) { 
        i++; 
        if(i > range[0] && i <= range[1]) { 
            let elementId = "Tweet#" + (i).toString();

            let row = document.createElement("tr");
            row.setAttribute("id", elementId); 

            let tweetKey = document.createElement("td");
            tweetKey.setAttribute("id", "tweet_id"); 
            tweetKey.innerHTML = key;

            let tweetDate = document.createElement("td");
            tweetDate.setAttribute("id", "tweet_date"); 
            tweetDate.innerHTML = all_data[key]['date']

            let tweetText = document.createElement("td")
            tweetText.setAttribute("id", "tweet_text");
            tweetText.innerHTML = all_data[key]['text'];

            let tweetInferred = document.createElement("td");
            tweetInferred.setAttribute("id", "tweet_inferred" + key);
            tweetInferred.innerHTML = "&#129302;";
        
            let boxes = document.createElement("td")
            boxes.setAttribute("class", "inputBox_wrapper"); 
        
            var checkboxes = getCheckBoxes(key, all_data[key]);
            boxes.appendChild(checkboxes);
        
            row.appendChild(tweetKey);
            row.appendChild(tweetDate);
            row.appendChild(tweetText);
            row.appendChild(tweetInferred);
            row.appendChild(boxes);
            table.appendChild(row); 
        }
    }
    loadImgs();

    console.log(range)
}


var results;
function get_tweet_class_callback(data) {
    var tweets = JSON.parse(data);
    //console.log(tweets); 
    var table = document.getElementById("TweetTable"); 


    for (var key in tweets) { 
        var row = document.createElement("tr"); 
        row.setAttribute('id', tweets[key] ); 

        var tweet_id = document.createElement("td"); 
        tweet_id.setAttribute("id", "classified_tweet_id"); 
        tweet_id.innerHTML = key;

        var date = document.createElement("td"); 
        date.setAttribute("id", "classified_tweet_date");
        date.innerHTML = tweets[key]['date'];

        var text = document.createElement("td"); 
        text.setAttribute("id", "classified_tweet_text"); 
        text.innerHTML = tweets[key]['text']; 

        var class_img = document.createElement("td");
        class_img.setAttribute("id", "classified_img");

        var clazz = tweets[key]['class'] === "bugs/glitches" ? "bugs" : tweets[key]['class'];
        class_img.innerHTML =  
        "<img class=\"" + clazz + "-color\" src=\"../img/svgs/" + clazz + "-color.svg\" alt=\"check\" title=\"" + clazz.toUpperCase() + "\"/>";


        row.appendChild(tweet_id);
        row.appendChild(date);
        row.appendChild(text);
        row.appendChild(class_img);
        table.appendChild(row); 
    }
    showPage();
    results = tweets;
}


function filter_json(data){
    //console.log(data); 
    var active_sliders = []
    var headers = ['Tweet ID', 'Date', 'Tweet', 'Class']; 
    var table_header = get_table_headers(headers); 

    for (var i of document.getElementsByTagName("input")) { 
        if (i.type != "checkbox") {
            continue; 
        }
        if(i.checked == true) { 
            if(i.id == 'bugs') { 
                active_sliders.push('bugs/glitches'); 
            }
            else { 
                active_sliders.push(i.id); 
            }
        }
    }
    //console.log(active_sliders); 

    var table = document.createElement('table'); 
    table.setAttribute('id', 'TweetTable');
    table.appendChild(table_header); 
    for (var key in results) { 
        if (active_sliders.includes(results[key]['class']) == false && active_sliders.length != 0) { 
            continue; 
        } 
        var row = document.createElement("tr"); 
        row.setAttribute('id', results[key] ); 

        var tweet_id = document.createElement("td"); 
        tweet_id.setAttribute("id", "classified_tweet_id"); 
        tweet_id.innerHTML = key;

        var date = document.createElement("td"); 
        date.setAttribute("id", "classified_tweet_date");
        date.innerHTML = results[key]['date'];

        var text = document.createElement("td"); 
        text.setAttribute("id", "classified_tweet_text"); 
        text.innerHTML = results[key]['text']; 

        var class_img = document.createElement("td");
        class_img.setAttribute("id", "classified_img");

        var clazz = results[key]['class'] === "bugs/glitches" ? "bugs" : results[key]['class'];
        class_img.innerHTML =  
        "<img class=\"" + clazz + "-color\" src=\"../img/svgs/" + clazz + "-color.svg\" alt=\"check\" title=\"" + clazz.toUpperCase() + "\"/>";

        row.appendChild(tweet_id);
        row.appendChild(date);
        row.appendChild(text);
        row.appendChild(class_img);
        table.appendChild(row); 

        // console.log(id);
        // console.log(results[id]);
    }
    var tweetbox = document.getElementById('TweetBox')
    tweetbox.innerHTML = ''; 
    table.setAttribute('border', '1');
    tweetbox.appendChild(table);
}

let already_training = false;

function retrain() {
    if(!already_training) {
        //we are not training the model, so start
        already_training = true;

        httpPostAsync("http://127.0.0.1:5000/retrain", "", function(result) {
            already_training = false;

            let v = JSON.parse(result)
            if(!v['training']) {
                //remove loading ui and notify of successful train
                alert("The model was trained successfully!");
            } else {
                //say unsuccessful train, its already training (someone else must be training it)
                //remove the ui thing
                alert("The model is still being trained!");
            }
        });

        //pop up fancy loading ui for training in progress
        alert("Model is training!");
    } else {
        //we are training the model
        alert("We're already training the model!");
    }
}

function get_table_headers(ar) { 
    var header = document.createElement('tbody');
    var sub_header = document.createElement('tr'); 

    for(var i of ar) { 
        var text = document.createElement('th'); 

        text.innerHTML = i; 
        sub_header.appendChild(text); 
    }
    header.appendChild(sub_header); 
    return header; 
}

function put_tweets_json () {
        let checkboxes = document.getElementsByTagName('input');
        var m = new Map(); 
        
        for(let i in checkboxes) { 
            if (checkboxes[i].type != 'checkbox') { 
                continue; 
            }
            var tweet_id = parseInt(checkboxes[i].className);

            if(!m.has(tweet_id)) { 
                m.set(tweet_id, []);
            }

            if (checkboxes[i].checked == true) {  
                    m.get(tweet_id).push(checkboxes[i].name); 
            }
        }
        for( arr of m.values()) { 
            if(arr.length == 0) { 
                alert("All tweets not classified!!");
                return;
            }
        }
    
        console.log(JSON.stringify(Object.fromEntries(m)));

        //console.log(m);     
       // httpPutAsync("http://127.0.0.1:5000/unclassified/20", data, get_tweet_callback);
    
}