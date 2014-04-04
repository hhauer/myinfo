$(document).ready(function() {
	
	window.lengthValid = false;
	window.numberValid = false;
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
		
		var result = zxcvbn(password, []);
		
		if (result.score <= 2) {
			$(".password-ttc").text("Weak");
		} else if (result.score == 3) {
			$(".password-ttc").text("Moderate");
		} else {
			$(".password-ttc").text("Strong");
		}
		
		$("#passwordbar").progressbar("option", {value: (result.score * 25)});
		
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
		if (window.lengthValid && window.numberValid && window.passwordSame) {
			return true;
		} else {
			return false;
		}
	});
});