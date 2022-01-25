require([
    "jquery"
], function ($) {

    $.testDocServiceApi = function () {
        var testApiResult = function () {
            var docUrlPublicValidation = $("#form-widgets-docUrlPublicValidation-0");

            var result = typeof DocsAPI != "undefined";

            docUrlPublicValidation.addClass("verified");
            docUrlPublicValidation.prop("checked", result);

            $("#form-buttons-save").click();
        };

        delete DocsAPI;

        $("#scripDocServiceAddress").remove();

        var js = document.createElement("script");
        js.setAttribute("type", "text/javascript");
        js.setAttribute("id", "scripDocServiceAddress");
        document.getElementsByTagName("head")[0].appendChild(js);

        var scriptAddress = $("#scripDocServiceAddress");

        scriptAddress.on("load", testApiResult).on("error", testApiResult);

        var docServiceUrlApi = $("#form-widgets-docUrl").val();

        if (!docServiceUrlApi.endsWith("/")) {
            docServiceUrlApi += "/";
        }

        scriptAddress.attr("src", docServiceUrlApi + "web-apps/apps/api/documents/api.js");
    };

    $("#form-widgets-docUrlPublicValidation").hide();

    $(document).ready(function () {
        $("#form-buttons-save").on("click", function(e) {
            if (!$("#form-widgets-docUrlPublicValidation-0").hasClass("verified")) {
                e.preventDefault();
                $.testDocServiceApi();
            }
        });
    });
});