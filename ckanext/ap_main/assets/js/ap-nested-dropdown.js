// NAVBAR NESTED DROPDOWN
// adjust mobile logic, to allow tapping on the nested dropdown level 1
ckan.module("ap-nested-dropdown", function ($, _) {
    "use strict";

    return {
        options: {},

        initialize: function () {
            this.apID = "#admin-panel";
            let self = this;

            $(`${self.apID} .dropdown-item.with-subitems`).click(function (e) {
                if (!self.isMobileDevice()) {
                    return;
                }

                e.preventDefault();
                e.stopPropagation();

                $(this).siblings().toggleClass("show");
            });

            $(`${self.apID} .nav-link.ap-dropdown-toggle`).click(function (e) {
                if (!self.isMobileDevice()) {
                    return;
                }

                $(`${self.apID} .submenu.dropdown-menu`).removeClass("show");
            })
        },
        isMobileDevice: function () {
            return window.innerWidth <= 992;
        }
    };
});
