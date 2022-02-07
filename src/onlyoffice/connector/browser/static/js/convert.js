require([
    "jquery",
], function ($) {
    $(document).ready(function () {

         $.showMessage = function(message, type) {
            var global_message = $("#global_statusmessage");
            global_message.empty();

            global_message.html(
                "<div class='portalMessage " + type + "'>" +
                    "<strong>" + $("#" + type).text()  + "</strong>" +
                    message +
                "</div>"
            );

        };

        $("#form-buttons-Convert").on("click", function (event) {
            event.preventDefault();

            function requestConvert () {
                url = "http://192.168.0.169:8080/Plone/spreadsheet.ods/onlyoffice-convert-action"

                $("form.view-name-onlyoffice-convert").ajaxSubmit({
                    type: "POST",
                    url: url,
                    success: function(value, state, xhr) {
                       if (!value.hasOwnProperty("error")) {
                            $("div.progress-bar").width(value.percent + "%")
                            if (value.endConvert === true) {
                                $("#form-buttons-Convert").addClass("hide")
                                $("#form-buttons-Open").removeClass("hide")
                                $.showMessage("Success", "info")
                                $("form.view-name-onlyoffice-convert").append($("<input>", {
                                    type: "hidden",
                                    name: "_file_uid",
                                    val: value.fileUID
                                  }));
                            } else {
                                setTimeout(requestConvert, 1000);
                            }
                        } else {
                            $.showMessage(value.error, "error")
                        }
                    }
                });
            };

            requestConvert();
        });
    });
});
