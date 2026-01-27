/**
 * CKAN module to copy text to clipboard.
 *
 * Options:
 * - content: (string) Text content to copy. Optional if targetElement is provided.
 * - targetElement: (string) Selector of the element to fetch text from. Optional if content is provided.
 *
 * Example usage:
 * <button class="btn btn-success" data-module="ap-copy-to-clipboard"
 *     data-module-content="Text to copy">
 *     Copy Text
 * </button>
*/
ckan.module("ap-copy-to-clipboard", function ($, _) {
    "use strict";

    return {
        options: {
            content: null,
            targetElement: null,
        },

        initialize: function () {
            $.proxyAll(this, /_on/);

            this.el.click(this._onClick)
        },

        /**
         * Get a text for copy. Could work with provided content or fetch it
         * from a target element.
         *
         * @returns {string|null}
         */
        _getTextToCopy: function () {
            if (!this.options.targetElement) {
                return this.options.content
            }

            let targetEl = $(this.options.targetElement);

            if (!targetEl) {
                return;
            }

            return targetEl.text().trim();
        },

        _onClick: function (e) {
            e.preventDefault();

            const text = this._getTextToCopy();

            if (!text) {
                return;
            }

            // Create a temporary input element
            var tempEl = document.createElement('textarea');
            tempEl.value = text;

            // Append the temp input element to the document
            document.body.appendChild(tempEl);

            // Select the text in the input element
            tempEl.select();
            tempEl.setSelectionRange(0, 99999);

            // Copy the selected text to the clipboard
            document.execCommand('copy');

            // Remove the temporary input element
            document.body.removeChild(tempEl);

            this.sandbox.publish("ap:notify", this._("The text is copied to the clipboard"));
        }
    };
});
