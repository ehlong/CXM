// parses the data from a get request for unclassified tweets

function get_tweet_callback(data) {
    let tweets = JSON.parse(data)
  console.log(tweets)
  var i = 0;
  for(var key in tweets) {
      let elementId = "Tweet#" + (++i).toString();
//      console.log("Attempting to set tweet: " + elementId)
//      console.log("to: " + tweets[key]);
      document.getElementById(elementId).innerHTML =
      "<h2>Tweet ID: " + key + "</h2>\n" +
      "<p>Date: " + tweets[key]['date'] + "</p>\n" +
      "<p>" + tweets[key]['text'] + "</p>";
  }
}

var results;
function get_tweet_class_callback(data) {
  var tweets = JSON.parse(data)
  console.log(tweets)
  var i = 0;
  for(var key in tweets) {
      let elementId = "Tweet#" + (++i).toString();
      if(i === 10){
          break;
      }
      document.getElementById(elementId).innerHTML =
      "<h2>Tweet ID: " + key + "</h2>\n" +
      "<p>Date: " + tweets[key]['date'] + "</p>\n" +
      "<p>" + tweets[key]['text'] + "</p>\n" +
      "<p>class: " + tweets[key]['class'] + "</p>";
  }
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
            if(i === 10){
                break;
            }
            document.getElementById(elementId).innerHTML =
                  "<h2>Tweet ID: " + key + "</h2>\n" +
                  "<p>Date: " + filteredResults[key]['date'] + "</p>\n" +
                  "<p>" + filteredResults[key]['text'] + "</p>\n" +
                  "<p>class: " + filteredResults[key]['class'] + "</p>";
        }

    }
    if(!$(data).is(":checked")){
        var i = 0;
        for(var key in results) {
            let elementId = "Tweet#" + (++i).toString();
            if(i === 10){
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