var total_inbox = 0;
var unread_inbox = 0;

function insertMail(mail){
    div_id = "mail_" + mail.id;
    css_class = 'mail';
    if (mail.read == false) {
        css_class = css_class + " unread"
        unread_inbox++;
    }
    $("#inbox").prepend("<div class='"+css_class+"' id='"+div_id+"' data-mail-id='"+mail.id+"'><div><span class='subject'>"+mail.subject+"</span><br><span class='date'>"+mail.sent_date+"</span></div></div>");
    total_inbox++;
    update_inbox_count();
}

function update_inbox_count(){
    $("#inbox_count").text(unread_inbox+"/"+total_inbox);
    if(unread_inbox > 0){
        $('title').text("("+unread_inbox+") PyLocalSmtp Inbox")
    }else{
        $('title').text("PyLocalSmtp Inbox");

    }
}

update_inbox_count();

function mark_as_read(mail_id){
    mail_elemt = $("#mail_" + mail_id);
    if(mail_elemt.hasClass("unread")){
        unread_inbox--;
        mail_elemt.removeClass("unread");
    }
    update_inbox_count();
}

function read(mail_id){
    $('.mail').removeClass('read_on');
    mark_as_read(mail_id);
    $("#mail_" + mail_id).removeClass("unread").addClass("read_on");
    $.getJSON('/mail/'+mail_id+"/", function(data) {
        $("#mail_detail").empty();
        $("#mail_detail").append("<h2>" + data.subject + "</h2>");
        $("#mail_detail").append("De: " + data.mail_from + "<br/>");
        $("#mail_detail").append("A: " + data.mail_to + "<br/>");
        $("#mail_detail").append("Date: " + data.sent_date);
        $("#mail_detail").append("<div class='mail_body'>" + data.body_html + "</div>");
    });
}

$(function() {
    var sent = 0;
    var recv = 0;

    /* Initialize INBOX */
    $.getJSON('/mail/', function(data) {
        for (var i = data.object_list.length - 1; i >= 0; i--) {
            insertMail(data.object_list[i]);
        };
    });

    /* Message event handler */
    $("#inbox").on('click', ".mail", function(){
        read($(this).attr('data-mail-id'));
    });

    /* Listen to the smtp server */
    var conn = new SockJS('/inbox');
    conn.onopen = function() {
        conn.send();
    };
    conn.onmessage = function(e) {
        recv += 1;
        insertMail(e.data);
    };

    /* Global INBOX actions */
    $("#id_read_all").on('click', function(){
        $.post('/mail/all/read/', function(data) {
            for (var i = data.read_ids.length - 1; i >= 0; i--) {
                mark_as_read(data.read_ids[i]);
            };
        }, 'json');
    });

    /* Global INBOX actions */
    $("#id_delete_all").on('click', function(){
        if (confirm("Do you really want to delete all messages ?")) {
            $.post('/mail/all/delete/', function(data) {
                if(data.ok == true){
                    $("#inbox").empty();
                    unread_inbox = 0;
                    total_inbox = 0;
                    update_inbox_count();
                }
            }, 'json');
        };
    });

});