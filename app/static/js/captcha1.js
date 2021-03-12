$(document).ready(function () {
$("#btn").click(
            function () {
                $.post(
                    '/auth/get_captcha',
                    $("#captcha")[0].src.toString(),
                    function (data) {
                        $('#captcha').attr('src', data['url'].toString());
                        $('#captcha').attr('alt', data['alt'].toString());
                    }
                )
            }
        )
})
