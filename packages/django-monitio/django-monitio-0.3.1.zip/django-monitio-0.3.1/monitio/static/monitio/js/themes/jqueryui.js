monitio.themes.jqueryui = {
    getHTML: function (message) {
        // TODO jezeli message nei ma PK, to nie wypisuj linku do zamkniecia go
        var subject = message.subject;
        if (subject)
            subject = subject + ": ";

        return $("<div/>")
            .addClass("ui-widget")
            .append([
                $("<div/>")
                    .addClass("ui-corner-all " + monitio.theme.getCSSClasses(message.level))
                    .css("padding", "0 .7em")
                    .css("margin-top", "5px")
                    .css("overflow", "auto")
                    .attr("id", "message-" + message.pk)
                    .append([
                                $("<span/>")
                                    .addClass("ui-icon " + monitio.theme.getCSSIcons(message.level))
                                    .css("float", "left")
                                    .css("margin-right", ".3em"),
                                $("<div/>")
                                    .css("float", "left")
                                    .css("width", "80%")
                                    .append([
                                        $("<strong/>").text(subject),
                                        message.message
                                    ]),
                                $("<div/>")
                                    .css("float", "right")
                                    .append([
                                        $(gettext("<a>close</a>"))
                                            .addClass("message-close icon")
                                            .attr("href", " /messages/mark_read/" + message.pk + "/")
                                            .click(monitio.theme.closeMessageClicked)
                                    ])
                    ])
            ]);


    },

    getCloseAllHTML: function () {
        return $("<div/>")
            .addClass("ui-widget message-close-all")
            .append([
                $("<div/>")
                    .addClass("ui-corner-all ui-state-highlight")
                    .css("margin-top", "5px")
                    .css("padding", "0 .8em")
                    .append([
                        $("<span/>")
                            .addClass("ui-icon ui-icon-circle-close")
                            .css("float", "left")
                            .css("margin-right", ".3em")
                            .css("margin-top", ".15em"),

                        $("<a/>")
                            .attr("href", "/messages/mark_read/all/")
                            .click(function(){
                                $(monitio.widget).MessagesPlaceholder("closeAllMessages");
                                return false;
                            })
                            .addClass("message-close-all")
                            .append(gettext("close all messages"))
                    ])
            ]);
    },

    getCSSClasses: function (level) {
        switch (monitio.levels[level]) {
            case "debug":
            case "success":
            case "info":
                return "ui-state-highlight";
            case "warning":
            case "error":
                return "ui-state-error";
        }
    },

    getCSSIcons: function (level) {
        switch (monitio.levels[level]) {
            case "debug":
                return "ui-icon-script";
            case "success":
            case "info":
                return "ui-icon-info";
            case "warning":
                return "ui-icon-alert";
            case "error":
                return "ui-icon-circle-close";
        }
        return "ui-icon-info";
    },

    closeMessageClicked: function(evt){
        /* This is in theme, because this function needs to get to the
        "toplevel" message DIV, which may be theme-dependent
         */
        var elem = $(evt.currentTarget);

        $(monitio.widget).MessagesPlaceholder(
            "closeMessage",
            elem.parent().parent().parent().parent(),
            elem.attr("href"));

        return false;
    }
};