require([
    "jquery",
    "mockup-i18n"
], function ($, I18N) {

    $.I18N = function (msgid, mapping = {}) {
        var i18n = new I18N();
        i18n.loadCatalog("onlyoffice.connector");
        _t = i18n.MessageFactory("onlyoffice.connector");
        return _t(msgid, mapping = mapping);
    }

    $.showMessage = function(message, type, modal = false) {
        var global_message = modal ? $(".plone-modal-dialog #global_statusmessage") : $("#global_statusmessage");

        global_message.empty();

        global_message.html(
            "<div class='portalMessage " + type + "'>" +
                "<strong>" + $("#" + type).text()  + "</strong>" +
                message +
            "</div>"
        );

    };
});
