function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getToken() {
    return getCookie('csrftoken');
}


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


jQuery(document).on("change", "select#requests_priority", function (e) {
    jQuery(this).parents("form").submit();
});


jQuery(document).on("click", ".remove-request-button", function (e) {
    e.preventDefault();
    var target = e.currentTarget;

    var url = jQuery(this).attr("href");

    jQuery.ajax({
      url: url,
      type: 'POST',
      dataType: 'json',
      data: {
        "csrfmiddlewaretoken": getToken(),
      },
      success: function(data, textStatus, xhr) {
        if (data.status == "success") {
            jQuery(target).parents("tr").fadeOut();
        } else {
            alert("Sorry, something went wrong");
        }
      },
      error: function(xhr, textStatus, errorThrown) {
        alert("Sorry, internal error occured");
      }
    });

});
