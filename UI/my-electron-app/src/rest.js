// https://stackoverflow.com/questions/247483/http-get-request-in-javascript

// asynchronous get request to endpoint (theUrl), invoked on callback
function httpGetAsync(theUrl, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous
    xmlHttp.send(null);
}

function httpPutAsync(theUrl, data, callback) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          callback(xmlHttp.responseText);
    }
    xmlHttp.open("PUT", theUrl, true); // true for asynchronous
    xmlHttp.setRequestHeader('content-type', 'application/json')
    xmlHttp.send(data);
}

function httpPostAsync(theUrl, data, callback) {
    var xmlHttp = new XMLHttpRequest();
        xmlHttp.onreadystatechange = function() {
      if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
          callback(xmlHttp.responseText);
    }
    xmlHttp.open("POST", theUrl, true); // true for asynchronous
    xmlHttp.setRequestHeader('content-type', 'application/json')
    xmlHttp.send(data);
}