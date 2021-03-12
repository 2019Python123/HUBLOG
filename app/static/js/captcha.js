$(document).ready(
    function get_captcha_method() {
        $.get(
            '/auth/get_captcha',
            function (data) {
                $('#captcha').attr('src', data['url'].toString());
                $('#captcha').attr('alt', data['alt'].toString());
            }
        )
    },
)