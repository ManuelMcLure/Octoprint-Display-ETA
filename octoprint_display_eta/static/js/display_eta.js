$(function() {
    function ETAModel(parameters) {
        var self = this;
        self.ETA = ko.observable("-");
		self.settings = parameters[0];
		time24hr : ko.observable();
		displayOnPrinter : ko.observable();
		removeColons : ko.observable();
        self.onBeforeBinding = function() {
            var element = $("#state").find(".accordion-inner .progress");
            if (element.length) {
                // console.log("Found required elements");
                var text = gettext("ETA");
                // console.log(text);
                element.before(text + ": <strong id='ETA_string' data-bind=\"html: ETA\"></strong><br>");
            }
        };
        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "display_eta") {
                // console.log("wrong plugin");
                return;
            }
            self.ETA(data.eta_string);
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: ETAModel,
        dependencies: ["printerStateViewModel", "settingsViewModel"],
        elements: ["#navbar_plugin_octoprint_display_eta","#ETA_string","#settings_plugin_display_eta"]
    });
});


