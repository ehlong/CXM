function get_tweet_callback(data) {
  var tweets = JSON.parse(data)
  console.log(tweets)
  var i = 0;
  for(var key in tweets) {
      let elementId = "Tweet#" + (++i).toString();
//      console.log("Attempting to set tweet: " + elementId)
//      console.log("to: " + tweets[key]);
      document.getElementById(elementId).innerHTML =
      "<h2>Tweet ID: " + key + "</h2>\n" +
      "<p>" + tweets[key] + "</p>";
  }
}