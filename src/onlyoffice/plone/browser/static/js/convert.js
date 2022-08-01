require([
    "jquery"
], function ($) {
    $(document).ready(function () {
        var form = $("form[class*='view-name-onlyoffice-convert']");
        var titleInput = $("#form-widgets-title");
        var currentType = $("#form-widgets-current_type");
        var targetType = $("#form-widgets-target_type");
        var buttonBlock = $("form .formControls");
        var progressBar = $("#progressBar");


        function onResponseSuccess(data) {
            $("div.progress-bar").width(data.percent + "%")
            if (data.endConvert === true) {
                $.showMessage($.I18N("Item converted"), "info")
                $("#messageProgress").text($.I18N("Converting is finished"));
                setTimeout(function () {
                    document.location.href = data.fileURL;
                }, 2000);
            } else {
                setTimeout(requestConvert, 1000);
            }
        };

        function onResponseError(message){
            $.showMessage(message, "error")
            titleInput.removeAttr("disabled");
            buttonBlock.show();
            progressBar.addClass("hide");
        }

        function requestConvert () {
            titleInput.attr("disabled", "disabled");
            buttonBlock.hide();
            progressBar.removeClass("hide");
            $("#messageProgress").text(
                $.I18N("Converting ${currentType} to ${targetType} in progress..", {
                    "currentType": currentType.text(),
                    "targetType": targetType.text()
                })
            );

            form.ajaxSubmit({
                type: "POST",
                url: form.attr('action') + "-action",
                data: {
                    "title": titleInput.val()
                },
                success: function(data) {
                    if (!data.hasOwnProperty("error")) {
                        onResponseSuccess(data);
                    } else {
                        onResponseError(data.error);
                    }
                },
                error: function(state, value, xhr) {
                    if (state.status == 403) {
                        onResponseError($.I18N("You are not authorized to add content to this folder"));
                    } else{
                        onResponseError(xhr);
                    }
                }
            });
        };

        $("#form-buttons-Convert").on("click", function (event) {
            $(window).off('beforeunload');
            event.preventDefault();

            if ($("#form div.error").length == 0) {
                requestConvert();
            }
        });
    });
});
