jQuery(function($){
    $.I18N = function (msgid, mapping = {}) {
        var i18n = new I18N();
        i18n.loadCatalog("onlyoffice.plone");
        _t = i18n.MessageFactory("onlyoffice.plone");
        return _t(msgid, mapping = mapping);
    }

    $.showMessage = function(message, type, modal = false) {
        var global_message = modal ? $(".modal-dialog #global_statusmessage") : $("#global_statusmessage");
        global_message.empty();

        var svgError = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="plone-icon statusmessage-icon mb-1 me-2 bi bi-exclamation-octagon-fill" viewBox="0 0 16 16" aria-labelledby="title"><path d="M11.46.146A.5.5 0 0 0 11.107 0H4.893a.5.5 0 0 0-.353.146L.146 4.54A.5.5 0 0 0 0 4.893v6.214a.5.5 0 0 0 .146.353l4.394 4.394a.5.5 0 0 0 .353.146h6.214a.5.5 0 0 0 .353-.146l4.394-4.394a.5.5 0 0 0 .146-.353V4.893a.5.5 0 0 0-.146-.353L11.46.146zM8 4c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 4.995A.905.905 0 0 1 8 4zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"></path><title>Error</title></svg>';

        var typeAlert = type == "error" ? "danger" : type;

        global_message.html(
            "<div class='portalMessage statusmessage statusmessage-" + type + " alert alert-" + typeAlert + "'>" +
                "<strong>" + svgError + $("#" + type).text()  + "</strong> " +
                message +
            "</div>"
        );

    };

    const I18N = function () {
        var self = this;
        self.baseUrl = $("body").attr("data-i18ncatalogurl");
        self.currentLanguage = $("html").attr("lang") || "en";

        // Fix for country specific languages
        if (self.currentLanguage.split("-").length > 1) {
            self.currentLanguage =
                self.currentLanguage.split("-")[0] +
                "_" +
                self.currentLanguage.split("-")[1].toUpperCase();
        }

        self.storage = null;
        self.catalogs = {};
        self.ttl = 24 * 3600 * 1000;

        // Internet Explorer 8 does not know Date.now() which is used in e.g. loadCatalog, so we "define" it
        if (!Date.now) {
            Date.now = function () {
                return new Date().valueOf();
            };
        }

        try {
            if (
                "localStorage" in window &&
                window.localStorage !== null &&
                "JSON" in window &&
                window.JSON !== null
            ) {
                self.storage = window.localStorage;
            }
        } catch (e) {}

        self.configure = function (config) {
            for (var key in config) {
                self[key] = config[key];
            }
        };

        self._setCatalog = function (domain, language, catalog) {
            if (domain in self.catalogs) {
                self.catalogs[domain][language] = catalog;
            } else {
                self.catalogs[domain] = {};
                self.catalogs[domain][language] = catalog;
            }
        };

        self._storeCatalog = function (domain, language, catalog) {
            var key = domain + "-" + language;
            if (self.storage !== null && catalog !== null) {
                self.storage.setItem(key, JSON.stringify(catalog));
                self.storage.setItem(key + "-updated", Date.now());
            }
        };

        self.getUrl = function (domain, language) {
            return self.baseUrl + "?domain=" + domain + "&language=" + language;
        };

        self.loadCatalog = function (domain, language) {
            if (language === undefined) {
                language = self.currentLanguage;
            }
            if (self.storage !== null) {
                var key = domain + "-" + language;
                if (key in self.storage) {
                    if (
                        Date.now() - parseInt(self.storage.getItem(key + "-updated"), 10) <
                        self.ttl
                    ) {
                        var catalog = JSON.parse(self.storage.getItem(key));
                        self._setCatalog(domain, language, catalog);
                        return;
                    }
                }
            }
            if (!self.baseUrl) {
                return;
            }
            $.getJSON(self.getUrl(domain, language), function (catalog) {
                if (catalog === null) {
                    return;
                }
                self._setCatalog(domain, language, catalog);
                self._storeCatalog(domain, language, catalog);
            });
        };

        self.MessageFactory = function (domain, language) {
            language = language || self.currentLanguage;
            return function translate(msgid, keywords) {
                var msgstr;
                if (
                    domain in self.catalogs &&
                    language in self.catalogs[domain] &&
                    msgid in self.catalogs[domain][language]
                ) {
                    msgstr = self.catalogs[domain][language][msgid];
                } else {
                    msgstr = msgid;
                }
                if (keywords) {
                    var regexp, keyword;
                    for (keyword in keywords) {
                        if (keywords.hasOwnProperty(keyword)) {
                            regexp = new RegExp("\\$\\{" + keyword + "\\}", "g");
                            msgstr = msgstr.replace(regexp, keywords[keyword]);
                        }
                    }
                }
                return msgstr;
            };
        };
    };
});