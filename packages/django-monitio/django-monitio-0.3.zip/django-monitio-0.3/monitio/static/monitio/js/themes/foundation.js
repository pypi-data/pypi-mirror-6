monitio.themes.foundation = {
    getHTML: function (message) {
        // TODO jezeli message nei ma PK, to nie wypisuj linku do zamkniecia go
        var subject = message.subject;
        if (subject)
            subject = subject + ": ";

        return $("<div data-alert></div>")
            .addClass("alert-box")
            .addClass(monitio.theme.getCSSClasses(message.level))
            .append([
                $("<strong/>").text(subject),
                message.message,
                $("<a>&times;</a>")
                    .addClass("close")
                    .attr("href", " /messages/mark_read/" + message.pk + "/")
                    .click(monitio.theme.closeMessageClicked)
            ]);
    },

    getCloseAllHTML: function () {
        return $("<div data-alert></div>")
            .addClass("alert-box info")
            .append([
                $("<a/>")
                    .attr("href", "/messages/mark_read/all")
                    .click(function () {
                        $(monitio.widget).MessagesPlaceholder("closeAllMessages");
                        return false;
                    })
                    .append([
                        $("<strong/>").text(gettext("Close all: ")),
                        gettext("close all messages")]),
            ]);
    },

    getCSSClasses: function (level) {
        switch (monitio.levels[level]) {
            case "success":
                return "success";
            case "debug":
            case "info":
                return "info";
            case "warning":
            case "error":
                return "warning";
        }
    },

    closeMessageClicked: function (evt) {
        /* This is in theme, because this function needs to get to the
         "toplevel" message DIV, which may be theme-dependent
         */
        var elem = $(evt.currentTarget);

        $(monitio.widget).MessagesPlaceholder(
            "closeMessage",
            elem.parent().parent(),
            elem.attr("href"));

        return false;
    }
};