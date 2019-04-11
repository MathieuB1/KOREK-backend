/*** Display Notification ***/
var link = document.createElement('link');
link.rel="stylesheet"
link.type = "text/css";
link.href = window.location.protocol + '//' + window.location.hostname + '/static/ws/toastify.min.css';
document.head.appendChild(link);


var script = document.createElement('script');
script.type = "text/javascript";
script.src = window.location.protocol + '//' + window.location.hostname + '/static/ws/toastify.js';

// Then bind the event to the callback function.
// There are several events for cross browser compatibility.
script.onreadystatechange = notify_js;
script.onload = notify_js;

// Fire the loading
document.head.appendChild(script);

function notify_js(message)
{
    Toastify({
        text: (typeof message === 'string') ? message : 'Welcome to Korek!',
        duration: 5000,
        newWindow: true,
        close: false,
        gravity: 'bottom', // `top` or `bottom`
        positionLeft: false, // `true` or `false`
        backgroundColor: '#0074D9',
    }).showToast();

}
/*** Display Notification ***/



var username = {{ user_json }};
var token = {{ token }};

var wsStart = window.location.protocol == "https:" ? 'wss://' : 'ws://';

var eventSocket = new WebSocket(
    wsStart + window.location.hostname +
    '/ws/event/' + username + '/', token);
 
eventSocket.onmessage = function(e) {
    var data = JSON.parse(e.data);
    var message = data['message'];
    //console.log(message);
    notify_js(message);
};

eventSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};