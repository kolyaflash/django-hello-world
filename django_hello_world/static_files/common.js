function ajaxForm(formSelector) {
    var defaultSelector = ".ajax-form";
    if (!formSelector) {
        formSelector = defaultSelector;
    }
    var form = jQuery(formSelector);
    var stateHolder = jQuery(".form-state", form);

    jQuery(document).on("change", '.ajax-form input, .ajax-form select, .ajax-form textarea', function (e) {
        stateHolder.text("Changes not saved yet");
    });

    jQuery(formSelector).on("submit", function (e) {


        var options = {
            target: jQuery("fieldset", jQuery(this)),
            beforeSubmit: function (formData, jqForm, options) {
                jQuery("fieldset", jqForm).prop("disabled", true);
                stateHolder.text("Submiting...");
            },
            success: function (responseText, statusText, xhr, $form) {
                if (jQuery("fieldset.has-errors", $form).length > 0) {
                    stateHolder.text("Form contains errors.");
                } else {
                    stateHolder.text("Changes saved!");
                }

                jQuery("fieldset", $form).prop("disabled", false);
            },
            error: function (responseText, statusText, xhr, $form) {
                stateHolder.text("Changes was not saved!");
                jQuery("fieldset", $form).prop("disabled", false);
            },
        };
        jQuery(this).ajaxSubmit(options);
        return false;
    });
}
