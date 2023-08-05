if (window.monitio == undefined) window.monitio = {};

monitio = {
    messages: [],
    widget: null,
    theme: null,
    themes: {},
    levels: {
        // messages -> django.contrib.messages.constants
        10: "debug",
        20: "info",
        25: "success",
        30: "warning",
        40: "error",

        // persistent messages -> monitio.constants
        110: "debug",
        120: "info",
        125: "success",
        130: "warning",
        140: "error"
    }
};

$.widget("monitio.FlashMessage", {

    _create: function () {
        // TODO tutaj tworzenie komunikatu w jquery
        // LUB foundation, w zlaeżności od parametru 'theme'
        // OPCJE to message_text, message_class, message_url też może być
        var element = monitio.theme.getHTML(this.options.message);
        this.element.append(element);
    },

    _setOption: function (key, value) {

    }
});

$.widget("monitio.MessagesPlaceholder", {
    options: {
        "theme": "jqueryui"
    },

    _create: function () {

        if (this.options.theme)
            monitio.theme = eval("monitio.themes." + this.options.theme);

        var source = new EventSource(this.options.url);
        var self = this;

        source.addEventListener('message', function (e) {
            self.addMessage($.parseJSON(e.data));
        });

        this.element.append("<div/>");
        monitio.widget = this.element;
        monitio.placeholder = this.element.children().last();

        $.ajax({
            dataType: 'json',
            url: "/messages/json/",
            success: function (data, status, obj) {
                data.forEach(function (msg) {
                    self.addMessage(msg);
                });
            },
            error: function(err) {
                console.log(err);
                self.addMessage({
                    'level': 40, // error
                    'subject': "Error",
                    'message': "Server error - unable to load messages<br/>(" + err.status + " " + err.statusText + ")",
                    'pk': null
                })
            }
        });
    },

    addMessage: function (msg) {
        monitio.placeholder.append("<div/>");
        monitio.placeholder.children().last().FlashMessage({'message': msg});
        if (monitio.placeholder.children().length == 2) {
            monitio.placeholder.parent().append(
                monitio.theme.getCloseAllHTML());
        };
    },

    closeMessage: function(msgDiv, url){
        $.ajax({
            url: url,
            method: "GET",
            success: function(){
                msgDiv.remove();
                if (monitio.placeholder.children().length==1)
                    monitio.placeholder.parent().children().last().remove();
            }
        });
    },

    closeAllMessages: function(){
        $.ajax({
            url: '/messages/mark_read/all/',
            method: "GET",
            success: function(){
                monitio.placeholder.children().remove();
                monitio.placeholder.parent().children().last().remove();
            }
        });

    }

});
