ckan.module("ap-htmx", function ($) {
    return {
        initialize: function () {
            $.proxyAll(this, /_on/);

            // initialize CKAN modules for HTMX loaded pages
            htmx.on("htmx:afterSettle", function (event) {
                var elements = event.target.querySelectorAll("[data-module]");

                for (let node of elements) {
                    if (node.getAttribute("dm-initialized")) {
                        continue;
                    }

                    ckan.module.initializeElement(node);
                    node.setAttribute("dm-initialized", true)
                }
            });
        },
    };
});
