$(document).ready(function () {

    window.lengthValid = false;
    window.numberValid = false;
    window.letterValid = false;
    window.passwordSame = false;
    window.illegalSymbol = false;

    $('#id_new_password1').keyup(function () {
        window.passwordSame = false;
        var password = $(this).val();

        if ((password.length < 8) || (password.length > 30)) {
            $('#totalcount').removeClass('valid').addClass('invalid');
            window.lengthValid = false;
        } else {
            $('#totalcount').removeClass('invalid').addClass('valid');
            window.lengthValid = true;
        }

        if ((password.match(/\d/g) || [] ).length < 1) {
            $('#numbercount').removeClass('valid').addClass('invalid');
            window.numberValid = false;
        } else {
            $('#numbercount').removeClass('invalid').addClass('valid');
            window.numberValid = true;
        }

        if ((password.match(/[a-zA-Z]/g) || [] ).length < 1) {
            $('#lettercount').removeClass('valid').addClass('invalid');
            window.letterValid = false;
        } else {
            $('#lettercount').removeClass('invalid').addClass('valid');
            window.letterValid = true;
        }

        if (password.search('@') > 0) {
            $('#invalidsymbol').removeClass('valid').addClass('invalid');
            window.illegalSymbol = true;
        } else {
            $('#invalidsymbol').removeClass('invalid').addClass('valid');
            window.illegalSymbol = false;
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
        passwordBar.find(".ui-progressbar-value").css({
            "background": passwordColor
        });

        $('#id_new_password2').keyup();
    });

    $('#id_new_password2').keyup(function () {
        if ($("#id_new_password1").val() != $("#id_new_password2").val()) {
            $("#password-same").removeClass('valid').addClass('invalid');
            window.passwordSame = false;
        } else {
            $("#password-same").removeClass('invalid').addClass('valid');
            window.passwordSame = true;
        }

        if (window.lengthValid && window.numberValid && window.letterValid && window.passwordSame && !window.illegalSymbol) {
            $("#password-button").removeAttr("disabled");
        } else {
            $("#password-button").attr("disabled", "disabled");
        }
    });

    $('#passwordForm').submit(function () {
        return window.lengthValid && window.numberValid && window.letterValid && window.passwordSame && !window.illegalSymbol;
    });
});