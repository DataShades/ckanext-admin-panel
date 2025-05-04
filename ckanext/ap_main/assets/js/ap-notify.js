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

            const icon = msgType === "error" ? "error" : "success";

            Swal.fire({
                icon: icon,
                text: msg,
                toast: true,
                position: 'bottom-end',
                showConfirmButton: false,
                timer: 5000,
                timerProgressBar: true,
                didOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer)
                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                }
            });
        }
    };
});
