jQuery(function () {
    // CalendarWidget
    jQuery.each(jQuery("[data-widget=calendar]"), function (i, element) {
        var format = jQuery(element).attr("data-format");

        // Parse format for Datepicker
        format = format.replace(/%/g, "");
        format = format.replace(/y/gi, "yyyy").replace(/d/gi, "dd").replace(/m/gi, "mm");
        console.log(format);

        jQuery(element).datepicker({format: format});
    });
});
