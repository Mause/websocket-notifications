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

    options.notificationDuration.value = localStorage["notificationDuration"];
                                         // how long a notification is shown for
    options.pingInterval.value = localStorage["pingInterval"];
                                         // how long the app waits between sending a ping to the server

    // if (!options.notificationDuration.checked) { ghost(true); }

    // Set the notificationDuration and pingInterval.
    options.notificationDuration.onchange = function() {
        localStorage["notificationDuration"] = options.notificationDuration.value;
        // ghost(!options.notificationDuration.checked);
    };

    options.pingInterval.onchange = function() {
        localStorage["pingInterval"] = options.pingInterval.value;
    };
});
