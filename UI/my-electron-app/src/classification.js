// parses the data from a get request for unclassified tweets

var unclassified_results = [];

function showPage() {
    document.getElementById("loader").style.display = "none";
    document.getElementById("divForFetch").style.display = "block";
    document.getElementById("loader-container").style.display = "none"; 
}

function get_tweet_callback(data) {
  let element;
  var n_tweets = document.getElementsByClassName("tweet_wrapper").length;
  for(let j = 1; j<n_tweets; j++){
      element = document.getElementsByName("classification" + j);
      for(let k = 0; k<element.length; k++){
          element[k].checked = false;
      }
  }

  let tweets = JSON.parse(data)
  console.log(tweets)
  var i = 1;
  unclassified_results = [];
  let classRadioButton;

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
  }
  loadImgs();
  showPage();
}


var results;
function get_tweet_class_callback(data) {
    var tweets = JSON.parse(data);
    console.log(tweets); 
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
    let filteredResults = [];
    if($(data).is(":checked")){
        filteredResults = Object.values(results)
            .filter(
                function(result){
                    return result.class === data.value;
                }
            );
        var i = 0;
        for(var key in filteredResults) {
            let elementId = "Tweet#" + (++i).toString();
            if(i === 26){
                break;
            }
            document.getElementById(elementId).innerHTML =
                  "<h2>Tweet: " + "</h2>\n" +
                  "<p>Date: " + filteredResults[key]['date'] + "</p>\n" +
                  "<p>" + filteredResults[key]['text'] + "</p>\n" +
                  "<p>class: " + filteredResults[key]['class'] + "</p>";

        }

    }
    if(!$(data).is(":checked")){
        var i = 0;
        for(var key in results) {
            let elementId = "Tweet#" + (++i).toString();
            if(i === 26){
                break;
            }
            document.getElementById(elementId).innerHTML =
                "<h2>Tweet ID: " + key + "</h2>\n" +
                "<p>Date: " + results[key]['date'] + "</p>\n" +
                "<p>" + results[key]['text'] + "</p>\n" +
                "<p>class: " + results[key]['class'] + "</p>";
        }
    }
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