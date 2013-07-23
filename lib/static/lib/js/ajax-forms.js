var csrftoken = $.cookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(function() {
	$('.ajax-wait-dialog').dialog({
		modal: true,
		dialogClass: "no-close",
		autoOpen: false,
		draggable: false,
		resizable: false
	});
	
	$(document).ajaxStart(function() {
		$('.ajax-wait-dialog').dialog('open');
	}).ajaxStop(function() {
		$('.ajax-wait-dialog').dialog('close');
	});
	
	$('.ajaxform').submit(function(event) {
		event.preventDefault();
		$.ajax({
			type: "POST",
			data: $(this).serialize(),
			cache: false,
			url: $(this).attr('action'),
			context: $(this)
		}).done(function(result) {
			var notification = $(this).find('.ajax-message')
			
			if (result.data.status == "Error") {
				notification.html(result.data.message);
				notification.removeClass('valid').addClass('errorlist')
			} else if (result.data.status == "Forward") {
				window.location.replace(result.data.URL);
			} else if (result.data.status == "Success") {
				notification.html(result.data.message);
				notification.removeClass('errorlist').addClass('valid')
			}
		});
		
		return false;
	});
	
	$('#ajax-progressbar').progressbar({
		value: false
	});
});