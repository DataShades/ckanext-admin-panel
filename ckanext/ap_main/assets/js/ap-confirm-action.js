/**
 * Extends core confirm-action.js to append a submit button to a form on submit
 *
 * @param {Event} e
 */

var extendedModule = $.extend({}, ckan.module.registry["confirm-action"].prototype);

extendedModule._onConfirmSuccess = function (e) {
    if (this.el.attr("type") === "submit") {
        this.el.hide();
        this.el.closest("form").append(
            $('<input>').attr({
                type: 'hidden',
                id: this.el.attr("id"),
                name: this.el.attr("name"),
                value: this.el.val()
            })
        )
    }

    this.performAction();
}

ckan.module("ap-confirm-action", function ($, _) {
    "use strict";

    return extendedModule;
});
