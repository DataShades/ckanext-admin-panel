/**
 * This module is responsible for rendering the table data with the Tabulator library.
 *
 */
ckan.module("ap-tabulator", function ($, _) {
    "use strict";
    return {
        options: {
            tableName: null,
            tableTitle: null,
            columns: null,
            tabulatorOptions: null,
            dataUrl: null,
            globalActions: null,
        },

        initialize: function () {
            $.proxyAll(this, /_on/);

            this.filterField = document.getElementById("filter-field");
            this.filterOperator = document.getElementById("filter-operator");
            this.filterValue = document.getElementById("filter-value");
            this.filterClear = document.getElementById("filter-clear");

            // Update filters on change
            this.filterField.addEventListener("change", this._onUpdateFilter);
            this.filterOperator.addEventListener("change", this._onUpdateFilter);
            this.filterValue.addEventListener("keyup", this._onUpdateFilter);
            this.filterClear.addEventListener("click", this._onClearFilter);

            // Fetch the data from the server and render the table
            fetch(this.sandbox.client.url(this.options.dataUrl))
                .then(resp => resp.json())
                .then(resp => {
                    const self = this;

                    this.options.tabulatorOptions.data = resp.data;

                    this.table = new Tabulator(this.el[0], this.options.tabulatorOptions);

                    self._onUpdateFilter();

                    this.table.on("renderComplete", function () {
                        htmx.process(this.element);
                    });
                });
        },

        /**
         * Update the filter based on the selected field, operator and value
         */
        _onUpdateFilter: function () {
            var filterVal = this.filterField.options[this.filterField.selectedIndex].value;
            var typeVal = this.filterOperator.options[this.filterOperator.selectedIndex].value;

            if (filterVal) {
                this.table.setFilter(filterVal, typeVal, this.filterValue.value);
            } else {
                this.table.clearFilter();
            }

            this._updateUrl();
        },

        /**
         * Clear the filter
         */
        _onClearFilter: function () {
            this.filterField.value = "";
            this.filterOperator.value = "=";
            this.filterValue.value = "";

            this.table.clearFilter();
        },

        /**
         * Update the URL with the current filter values
         */
        _updateUrl: function () {
            const url = new URL(window.location.href);
            url.searchParams.set("field", this.filterField.value);
            url.searchParams.set("operator", this.filterOperator.value);
            url.searchParams.set("q", this.filterValue.value);
            window.history.replaceState({}, "", url);
        },
    };
});
