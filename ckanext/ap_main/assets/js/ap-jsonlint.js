ckan.module("ap-jsonlint", function ($, _) {
    "use strict";

    return {
        options: {
            input: null,
            result: null
        },

        initialize: function () {
            const inputField = $(this.options.input);
            const resultContainer = $(this.options.result);

            if (!inputField.length || !resultContainer.length) {
                console.error("Missing input and result container for a jsonlint.")
                return;
            }

            inputField.on("input", () => {
                const jsonData = inputField.val();

                try {
                    jsonlint.parse(jsonData);
                    resultContainer.text("Valid JSON");
                    resultContainer.css('color', 'green');
                } catch (error) {
                    resultContainer.text(`Invalid JSON: ${error.message}`);
                    resultContainer.css('color', 'red');
                }
            });
        }
    };
});
