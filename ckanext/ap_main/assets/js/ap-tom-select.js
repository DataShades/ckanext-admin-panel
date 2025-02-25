ckan.module("ap-tom-select", function ($) {
    return {
        options: {
            valueField: "value",
            labelField: "text",
            plugins: {
                remove_button: {
                    title: 'Remove this item',
                },
                dropdown_input: {},
                clear_button: {
                    title: 'Remove all selected options',
                }
            },
            loadUrl: null,
            create: true,
            delimiter: ",",
        },

        initialize() {
            $.proxyAll(this, /_/);

            if (typeof TomSelect === "undefined") {
                console.error("[bulk-tom-select] TomSelect library is not loaded");
                return
            }

            if (this.options.loadUrl) {
                this.options.load = this._loadOptions;
            }

            const options = this.sandbox["ap"].nestedOptions(this.options);

            if (this.el.get(0, {}).tomselect) {
                return;
            }

            this.widget = new TomSelect(this.el, options);
        },

        _loadOptions: function (query, callback) {
            var self = this;

            if (self.loading > 1) {
                callback();
                return;
            }

            fetch(this.options.loadUrl)
                .then(response => response.json())
                .then(json => {
                    callback(json.result);
                    self.settings.load = null;
                }).catch(() => {
                    callback();
                });

        },
    };
});
