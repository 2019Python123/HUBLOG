$(document).ready(
    $(".btn").click(function () {
            var data = {
                'email': $("#email").val(),
                'username': $("#username").val(),
                'password': $("#password").val(),
                'captcha': $("#captcha_in").val(),
                're_me': $("#remember_me").val(),
                'imag': $("#captcha").attr("alt")
            }
            $.ajax(
                {
                    url: '/auth/ajax_login',
                    data: JSON.stringify(data),
                    type: 'post',
                    success: function (res) {
                        if (res['msg']) {
                            alert(res['msg']);
                            window.location.replace(res['url'])
                        }
                        else {
                            alert('登录成功');
                            window.location.replace(res['url']);
                        }
                    },
                    error: function (res) {
                        alert(res['msg'])
                    }
                }
            )
        }
    )
)