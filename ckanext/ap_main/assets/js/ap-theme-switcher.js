/**
 * Theme switcher module
 *
 * This module is responsible for switching between light and dark themes.
 *
 * The module uses the localStorage to store the user's preferred theme.
 */
ckan.module("ap-theme-switcher", function ($, _) {
    "use strict";
    return {
        options: {},

        initialize: function () {
            this.light = "light";
            this.dark = "dark";

            this.defaultSchema = this.light;
            this.localStorageKey = "apPreferredColorScheme";

            this.scheme = this.getSchemeFromLS();

            this.el.on("click", this._onSwitch.bind(this));
            this.applyScheme();
        },

        getSchemeFromLS: function () {
            let currentSchema = window.localStorage.getItem(this.localStorageKey);
            return currentSchema ? currentSchema : this.defaultSchema
        },

        saveSchemeToLS: function () {
            window.localStorage.setItem(this.localStorageKey, this.scheme)
        },

        applyScheme: function () {
            document.querySelector("body").setAttribute("admin-panel-theme", this.scheme);
            document.querySelector("#admin-panel").setAttribute("admin-panel-theme", this.scheme);
        },

        _onSwitch: function () {
            this.scheme = this.scheme == this.light ? this.dark : this.light;
            this.applyScheme();
            this.saveSchemeToLS();
        }
    };
});
