/**
 * Provides a way to trigger notifications in the UI.
 *
 * Example:
 *   // Show a success notification
 *   this.sandbox.publish("ap:notify", "Operation completed successfully");
 *
 *   // Show an error notification
 *   this.sandbox.publish("ap:notify", "An error occurred", "error");
 */
ckan.module("ap-notify", function ($) {
    return {
        initialize: function () {
            $.proxyAll(this, /_on/);

            this.sandbox.subscribe("ap:notify", this._onShowNotification);

            $(".flash-messages .ap-notification").each((_, el) => {
                this._onShowNotification(el.dataset.message, el.dataset.category);
                el.remove();
            })
        },

        _onShowNotification: function (msg, msgType) {
            if (msgType === "alert-danger") {
                msgType = "error";
            }

            const icon = msgType === "error"
                ? '<i class="me-2 fa fa-times-circle"></i>'
                : '<i class="me-2 fa fa-check-circle"></i>';

            ckan.apToast({
                type: msgType === "error" ? "danger" : "success",
                title: msgType === "error" ? ckan.i18n._("Error") : ckan.i18n._("Success"),
                message: msg,
                icon: icon,
                delay: 5000,
                position: "bottom-right",
                showProgress: true,
                stacking: true
            });
        }
    };
});
