// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

/*
  Grays out or [whatever the opposite of graying out is called] the option
  field.
*/
function ghost(isDeactivated) {
    options.style.color = isDeactivated ? 'graytext' : 'black';
                                              // The label color.
    // options.pingInterval.disabled = isDeactivated; // The control manipulability.
}

window.addEventListener('load', function() {
    // Initialize the option controls.
    if (localStorage["notificationDuration"] === undefined) { localStorage["notificationDuration"] = 3000; }
    if (localStorage["pingInterval"] === undefined) { localStorage["pingInterval"] = 10000; }

    if (localStorage["websocketPort"] === undefined) { localStorage["websocketPort"] = 9999; }
    if (localStorage["websocketHost"] === undefined) { localStorage["websocketHost"] = 'localhost'; }

    options.notificationDuration.value = localStorage["notificationDuration"]/1000;
                                         // how long a notification is shown for
    options.pingInterval.value =         localStorage["pingInterval"]/1000;
                                         // how long the app waits between sending a ping to the server
    options.websocketPort.value =        localStorage["websocketPort"];
                                         // the websocket server host
    options.websocketHost.value =        localStorage["websocketHost"];

    // Set the notificationDuration and pingInterval.
    options.notificationDuration.onchange = function() { localStorage["notificationDuration"] = options.notificationDuration.value*1000; };
    options.pingInterval.onchange =  function() { localStorage["pingInterval"] = options.pingInterval.value*1000; };

    options.websocketHost.onchange = function() { localStorage["websocketHost"] = options.websocketHost.value; };
    options.websocketPort.onchange = function() { localStorage["websocketPort"] = options.websocketPort.value; };
});
