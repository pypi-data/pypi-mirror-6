jQuery(function () {
    // Check for viewlet
    if (jQuery('#zoomit-marker').length) {
        var base_path = jQuery('base').attr('href') || window.location.pathname;
        if (base_path[base_path.length-1] != '/') { base_path = base_path + '/'; }
        jQuery.getJSON(base_path + 'zoomit-json', function (data) {
            var image = jQuery('#content a > img:first-child:first');
            if (data.ready && image.length) {
                var script = jQuery(data.embed).attr('src');
                window.backupwrite = document.write;
                var writer_div = jQuery('<div></div>');
                writer_div.insertBefore(image.parent());
                document.write = function (str) {
                    writer_div.append(str);
                }
                jQuery.getScript(script, function () {
                    // Hide the original linked image
                    image.parent().hide();
                    document.write = window.backupwrite;
                });
            }
        });
    }
});
