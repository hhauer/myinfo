$(document).ready(function() {
	
	window.lengthValid = false;
	window.numberValid = false;
    window.characterValid = false;
	window.passwordSame = false;
	
	$('#id_newPassword').keyup(function() {
		window.passwordSame = false;
		var password = $(this).val();
		
		if( (password.length < 8) || (password.length > 30) ) {
			$('#totalcount').removeClass('valid').addClass('invalid');
			window.lengthValid = false;
		} else {
			$('#totalcount').removeClass('invalid').addClass('valid');
			window.lengthValid = true;
		}
		
		if( (password.match(/\d/g) || [] ).length < 1) {
			$('#numbercount').removeClass('valid').addClass('invalid');
			window.numberValid = false;
		} else {
			$('#numbercount').removeClass('invalid').addClass('valid');
			window.numberValid = true;
		}

        if( (password.match(/[a-zA-Z]/g) || [] ).length < 1) {
			$('#charactercount').removeClass('valid').addClass('invalid');
			window.numberValid = false;
		} else {
			$('#charactercount').removeClass('invalid').addClass('valid');
			window.numberValid = true;
		}
		
		var result = zxcvbn(password, []);

        var passwordColor = '#D2492A';
		if (result.score <= 2) {
			$(".password-ttc").text("Weak");
		} else if (result.score == 3) {
			$(".password-ttc").text("Moderate");
		} else {
			$(".password-ttc").text("Strong");
            passwordColor = '#6A7F10';
		}

        var passwordBar = $("#passwordbar");
		passwordBar.progressbar("option", {value: (result.score * 25)});
        passwordBar.find( ".ui-progressbar-value").css({
            "background": passwordColor
        });
		
		$('#id_confirmPassword').keyup();
	});
	
	$('#id_confirmPassword').keyup(function() {
		if ($("#id_newPassword").val() != $("#id_confirmPassword").val()) {
			$("#password-same").removeClass('valid').addClass('invalid');
			window.passwordSame = false;
		} else {
			$("#password-same").removeClass('invalid').addClass('valid');
			window.passwordSame = true;
		}
		
		if (window.lengthValid && window.numberValid && window.passwordSame) {
			$("#password-button").removeAttr("disabled");
		} else {
			$("#password-button").attr("disabled", "disabled");
		}
	});
	
	$('#passwordForm').submit(function() {
		if (window.lengthValid && window.numberValid && window.characterValid && window.passwordSame) {
			return true;
		} else {
			return false;
		}
	});
});