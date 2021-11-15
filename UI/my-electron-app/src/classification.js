function get_tweet_callback(data) {
  var tweets = JSON.parse(data)
  console.log(tweets)
  for(var i = 0; i != 9; ++i) {
      let elementId = "Tweet#" + (i+1).toString();
      console.log("Attempting to set tweet: " + elementId)
      console.log("to: " + tweets[i]);
      document.getElementById(elementId).innerHTML = tweets[i];
  }
}