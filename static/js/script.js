$(document).ready(function () {

    // Auto-hide flash messages after 3 seconds
    setTimeout(function () {
        $('.flash-msg').fadeOut('slow');
    }, 3000);

    // Delete confirmation
    $('.delete-btn').on('click', function (e) {
        if (!confirm('Are you sure you want to delete this document? This cannot be undone.')) {
            e.preventDefault();
            return false;
        }
    });

    // Register form validation
    $('#registerForm').on('submit', function (e) {
        var valid = true;

        var name = $('#regName').val().trim();
        if (name === '') {
            $('#regName').addClass('is-invalid');
            valid = false;
        } else {
            $('#regName').removeClass('is-invalid').addClass('is-valid');
        }
    
        var email = $('#regEmail').val().trim();
        if (!email.includes('@') || email.length < 5) {
            $('#regEmail').addClass('is-invalid');
            valid = false;
        } else {
            $('#regEmail').removeClass('is-invalid').addClass('is-valid');
        }

        var password = $('#regPassword').val();
        if (password.length < 6) {
            $('#regPassword').addClass('is-invalid');
            valid = false;
        } else {
            $('#regPassword').removeClass('is-invalid').addClass('is-valid');
        }

        if (!valid) e.preventDefault();
    });

    // Login form validation
    $('#loginForm').on('submit', function (e) {
        var valid = true;

        var email = $('#loginEmail').val().trim();
        if (!email.includes('@') || email.length < 5) {
            $('#loginEmail').addClass('is-invalid');
            valid = false;
        } else {
            $('#loginEmail').removeClass('is-invalid').addClass('is-valid');
        }

        var password = $('#loginPassword').val();
        if (password === '') {
            $('#loginPassword').addClass('is-invalid');
            valid = false;
        } else {
            $('#loginPassword').removeClass('is-invalid').addClass('is-valid');
        }

        if (!valid) e.preventDefault();
    });

    // Upload form validation
    $('#uploadForm').on('submit', function (e) {
        var valid = true;

        var title = $('#docTitle').val().trim();
        if (title === '') {
            $('#docTitle').addClass('is-invalid');
            valid = false;
        } else {
            $('#docTitle').removeClass('is-invalid').addClass('is-valid');
        }

        var file = $('#docFile').val();
        if (file === '') {
            $('#docFile').addClass('is-invalid');
            valid = false;
        } else {
            $('#docFile').removeClass('is-invalid').addClass('is-valid');
        }

        if (!valid) e.preventDefault();
    });

});
