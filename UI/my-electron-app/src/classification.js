// parses the data from a get request for unclassified tweets

var unclassified_results = [];

function showPage() {
    document.getElementById("loader").style.display = "none";
    document.getElementById("divForFetch").style.display = "block";
    document.getElementById("loader-container").style.display = "none";
}



function get_tweet_callback(data) {
  let element;
  for(let j = 1; j<10; j++){
      element = document.getElementsByName("classification" + j);
      //console.log(element);
      for(let k = 0; k<element.length; k++){
          //console.log(element[k]);
          element[k].checked = false;
      }
    }

  let tweets = JSON.parse(data)
  //console.log(tweets)
  var i = 1;
  unclassified_results = [];
  let classRadioButton;

  for(var key in tweets) {
      let elementId = "Tweet#" + (i).toString();

//      console.log("Attempting to set tweet: " + elementId)
//      console.log("to: " + tweets[key]);
      document.getElementById(elementId).innerHTML =
      "<h2>Tweet ID: " + key + "</h2>\n" +
      "<p>Date: " + tweets[key]['date'] + "</p>\n" +
      "<p>" + tweets[key]['text'] + "</p>";
      unclassified_results.push(key);
      let clazz = tweets[key]['class'];
      let classRadioButtonId = clazz + (i).toString();
      console.log("Class: " + classRadioButtonId);
      classRadioButton = document.getElementById(classRadioButtonId);
      //classRadioButton.checked = true;
      ++i;
  }
  showPage();
}

var results;
function get_tweet_class_callback(data) {
  var tweets = JSON.parse(data)
  //console.log(tweets)
  var i = 0;
  for(var key in tweets) {
      let elementId = "Tweet#" + (++i).toString();
      if(i === 26){
          break;
      }
      document.getElementById(elementId).innerHTML =
      "<h2>Tweet ID: " + key + "</h2>\n" +
      "<p>Date: " + tweets[key]['date'] + "</p>\n" +
      "<p>" + tweets[key]['text'] + "</p>\n" +
      "<p>class: " + tweets[key]['class'] + "</p>";
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
    var big_class = {} 
    var ids = []
    var values = []
    var checked = document.getElementsByTagName('input');

    //Grab ids that are presented to user.
    for(var i =0; i < unclassified_results.length;i++) { 
        ids.push(unclassified_results[i]);
    }

    //Grab each of the  checked radio values (classifications)
    for(var i =0; i < checked.length;i++) {
        var user_class = checked[i]
        if(user_class.checked == true) { 
        values.push(user_class.value); 
        }
    }

    //If user didn't check all the boxes then error.
    if(ids.length != values.length) { 
        alert("Please input all values before committing");
    }
    else { 
        for (var i =0; i< ids.length;i++ ) {
            // var data = JSON.stringify({
            //     'id': ids[i], 
            //     'class': values[i]
            //     });

            // httpPutAsync("http://127.0.0.1:5000/unclassified/", data);
            // Use this setup for one at a time.
            big_class[ids[i]] = values[i];
        }
        var data = JSON.stringify(big_class);
        console.log(data);
        httpPutAsync("http://127.0.0.1:5000/unclassified/9", data, get_tweet_callback);
    }
}