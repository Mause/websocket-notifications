/**
 *
 * File: logic_and_communication.js
 *
 * Project: Websocket webkit notification pusher
 * Component: client end application logic
 *
 * Authors: Dominic May;
 *          Lord_DeathMatch;
 *          Mause
 *
 * Description: a simple javascript and websocket notification push service
 *
**/



if (window.webkitNotifications && window.webkitNotifications.checkPermission() === 0) { // 0 is PERMISSION_ALLOWED


    $('.debug_checkbox').click(function () {
        if ($('#debugCheckbox').is(":checked")){
            $('.debug_output').show();
        } else {
            $('.debug_output').hide();
        }
    });

    // some preferences
    ping_interval = 10000;
    notification_duration = 3000;

    debug_divs = 0;
    append_debug_div = function(message){
        debug_divs += 1;
        $('.debug_output').append(
            '<div id="debug_output_div_'+(debug_divs)+'">'+message+'</div>');
        $('#debug_output_div_' + debug_divs)[0].scrollIntoView( true );
    };

    // console.log('We have permission from the user to display notifications');

    if (typeof(host) === undefined){
        host = 'localhost';
    }
    if (typeof(port) === undefined){
        port = 9999;
    }
    ws = new WebSocket("ws://"+host+":"+port+"/");
    append_debug_div('Connecting...');

    ws.onopen = function() {
        append_debug_div('Port opened...!');
        ws.send("port_thoroughput_test;"+uuid.v4());
        $('.status_blob').css('background-color', 'green');
    };
    
    ws.onmessage = function (e) {
        if (e.data === 'pong') {
            $('.status_blob').css('background-color', 'green');
        } else if (e.data.substring(0,34) === "port_thoroughput_test_confirmation"){
            guid = e.data.substring(35,e.data.length);
            console.log('thoroughput test completed; '+guid);
            notif_instance = createNotificationInstance({
                'notificationType':'simple',
                'icon':'',
                'title':'Connection Obtained',
                'content':''});
            show_notification_in_time(notif_instance);

        } else {
            console.log('notification '+e.data);
            data = $.parseJSON(e.data);
            // icon = (if data['icon'] != '' data.icon);
            notification_test = createNotificationInstance({
                notificationType: 'simple',
                // icon: e.data.split('~')[0],
                // title: e.data.split('~')[1],
                // content: e.data.split('~')[2]
                icon: data.icon,
                title: data.title,
                content: data.content
            });
            show_notification_in_time(notification_test);
        }
    };
    
    ws.onclose = function() {
        append_debug_div('Connection closed');
    };

    ws.onerror = function() {
        append_debug_div('Connection failed');
        ws.close();
    };

    notifications = [];

    show_notification_in_time = function(notif_instance){
        notifications.push([notif_instance, Date.now()]);

        notifications[notifications.length-1][0].ondisplay = function() {
            setTimeout(function (){
                notifications[0][0].close();
                if (notifications.length !== 0){
                    notifications.splice(0,1);
                }
                console.log('closing notification');
            }, notification_duration);
        };
        notifications[notifications.length-1][0].show();
    };

    createNotificationInstance = function(options) {
        if (options.notificationType == 'simple') {
            return window.webkitNotifications.createNotification(
                options.icon, options.title, options.content);
        } else if (options.notificationType == 'html') {
            return window.webkitNotifications.createHTMLNotification(options.url);
        }
    };
    ping = function () {
        ws.send('ping');
        console.log("Pinging...");
        $('.status_blob').css('background-color', 'red');
    };
    setInterval(function(){ping();}, ping_interval);


    $('#ping_button').click(function (){ping();});

} else {
    console.log('We don\'t have permission from the user, requesting it now');
    $('#requestPermissionButton').click(function () {window.webkitNotifications.requestPermission();});
    $('#requestPermissionButton').show();
}
