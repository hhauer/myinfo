$(document).ready(function() {
	
	window.lengthValid = false;
	window.numberValid = false;
	window.letterValid = false;
	window.specialValid = false;
	window.passwordSame = false;
	
	$('#id_newPassword').keyup(function() {
		window.passwordSame = false;
		var password = $(this).val();
		
		if( (password.length < {{ password_rules.minimum_count }}) || (password.length > {{ password_rules.maximum_count }}) ) {
			$('#totalcount').removeClass('valid').addClass('invalid');
			window.lengthValid = false;
		} else {
			$('#totalcount').removeClass('invalid').addClass('valid');
			window.lengthValid = true;
		}
		
		if( (password.match(/\d/g) || [] ).length < {{ password_rules.number_count }} ) {
			$('#numbercount').removeClass('valid').addClass('invalid');
			window.numberValid = false;
		} else {
			$('#numbercount').removeClass('invalid').addClass('valid');
			window.numberValid = true;
		}
		
		if( (password.match(/[a-zA-Z]/g) || [] ).length < {{ password_rules.letter_count }} ) {
			$('#lettercount').removeClass('valid').addClass('invalid');
			window.letterValid = false;
		} else {
			$('#lettercount').removeClass('invalid').addClass('valid');
			window.letterValid = true;
		}
		
		if( (password.match(/[\\\^\]\-~`!@#$%&*()[{};:'",.<>/?_=+|]/g) || [] ).length < {{ password_rules.special_count }} ) {
			$('#specialcount').removeClass('valid').addClass('invalid');
			window.specialValid = false;
		} else {
			$('#specialcount').removeClass('invalid').addClass('valid');
			window.specialValid = true;
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
		
		if (window.lengthValid && window.numberValid && window.letterValid && window.specialValid && window.passwordSame) {
			$("#password-button").button('enable');
		} else {
			$("#password-button").button('disable');
		}
	});
	
	$('#passwordForm').submit(function() {
		if (window.lengthValid && window.numberValid && window.letterValid && window.specialValid && window.passwordSame) {
			return true;
		} else {
			return false;
		}
	});
});