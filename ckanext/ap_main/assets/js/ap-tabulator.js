ckan.module("ap-tabulator", function ($, _) {
    "use strict";
    return {
        options: {
            config: null
        },

        initialize: function () {
            $.proxyAll(this, /_on/);

            if (!this.options.config) {
                console.error("No config provided for tabulator");
                return;
            }

            this.filterField = document.getElementById("filter-field");
            this.filterOperator = document.getElementById("filter-operator");
            this.filterValue = document.getElementById("filter-value");
            this.filterClear = document.getElementById("filter-clear");
            this.globalAction = document.getElementById("global-action");
            this.applyGlobalAction = document.getElementById("apply-global-action");

            // Update filters on change
            this.filterField.addEventListener("change", this._onUpdateFilter);
            this.filterOperator.addEventListener("change", this._onUpdateFilter);
            this.filterValue.addEventListener("keyup", this._onUpdateFilter);
            this.filterClear.addEventListener("click", this._onClearFilter);
            this.applyGlobalAction.addEventListener("click", this._onApplyGlobalAction);

            this.table = new Tabulator(this.el[0], this.options.config);

            this.table.on("tableBuilt", () => {
                this._onUpdateFilter();
            });

            this.table.on("renderComplete", function () {
                htmx.process(this.element);

                const pageSizeSelect = document.querySelector(".tabulator-page-size");

                if (pageSizeSelect) {
                    pageSizeSelect.classList.add("form-select");
                }
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
            this._updateUrl();
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

        /**
         * Apply the global action to the selected rows
         */
        _onApplyGlobalAction: function () {
            const globalAction = this.globalAction.options[this.globalAction.selectedIndex].value;

            if (!globalAction) {
                return;
            }

            const selectedData = this.table.getSelectedData();

            if (!selectedData.length) {
                return;
            }

            const form = new FormData();

            form.append("global_action", globalAction);
            form.append("rows", JSON.stringify(selectedData));

            fetch(this.sandbox.client.url(this.options.config.ajaxURL), {
                method: "POST",
                body: form,
            })
                .then(resp => resp.json())
                .then(resp => {
                    if (!resp.success) {
                        this.sandbox.publish("ap:notify", resp.errors[0], "error");

                        if (resp.errors.length > 1) {
                            this.sandbox.publish("ap:notify", "Multiple errors occurred and were suppressed", "error");
                        }
                    }

                    this.table.replaceData();
                    this.sandbox.publish("ap:notify", "Operation completed", "success");
                }).catch(error => {
                    console.error("Error:", error);
                });
        },
    };
});
