var timeout;
var sayings = [
    "Begging Jack Dorsey for content...",
    "Making things awesome...",
    "Fetching Epic tweets...",
    "Ratio'd...",
    "Dispatching carrier pigeons...",
    "Losing sleep..."
];

var randomNumber = Math.floor(Math.random()*sayings.length);
function randomMsg() {
    document.getElementById("msg").innerHTML = sayings[randomNumber];
}
function showPage() {
    document.getElementById("loader").style.display = "none";
    document.getElementById("divForFetch").style.display = "block";
    document.getElementById("loader-container").style.display = "none";
}