const { Swal } = require("../../../ap_main/assets/js/vendor/sweetalert2.min");

/**
 * A script to manage AJAX actions on the cron list page
 */
ckan.module("ap-cron-htmx", function ($) {
    return {
        options: {
            formId: null,
        },
        initialize: function () {
            $.proxyAll(this, /_on/);

            document.addEventListener('htmx:confirm', this._onHTMXconfirm);
            document.addEventListener('htmx:afterRequest', this._onAfterRequest)
        },

        _onHTMXbeforeRequest: function (e) {
            $(e.detail.target).find("[data-module]").unbind()

            for (const [key, _] of Object.entries(ckan.module.instances)) {
                ckan.module.instances[key] = null;
            }
        },

        _onHTMXafterSettle: function (e) {
            const doNotInitialize = ["ap-hyperscript"]

            $(e.detail.target).find("[data-module]").each(function (_, element) {
                const moduleName = $(element).attr("data-module");

                if (!doNotInitialize.includes(moduleName)) {
                    ckan.module.initializeElement(element);
                }
            })
        },

        _onHTMXconfirm: function (evt) {
            if (evt.detail.path.includes("/cron/delete")) {
                evt.preventDefault();

                Swal.fire({
                    text: this._("Are you sure you wish to delete a cron job?"),
                    icon: "warning",
                    buttons: true,
                    dangerMode: true,
                }).then((confirmed) => {
                    if (confirmed) {
                        evt.detail.issueRequest();
                        this.sandbox.publish("ap:notify", this._("A cron job has been removed"));
                    }
                });
            }
        },

        _onAfterRequest: function (evt) {
            if (evt.detail.pathInfo.requestPath.includes("/cron/delete/")) {
                htmx.trigger(`#${this.options.formId}`, "change");
            }
        }
    };
});
