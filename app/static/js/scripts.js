$(document).ready(function () {
    var email = $(".email").val();
    var name = $(".name").val();
    var data = {
        'email':email,
        'name' : name,
    }
    $("input[type=password]").blur(function(){
        data['password'] = $(this).val();
    });

    $(":password").css("background-color","#ccc")

    $("#btn").click(function () {
        $.ajax(
            {
                url: "/auth/ajax_logon_",
                type:'POST',
                async:true,
                data:JSON.stringify(data),
                dataType:'json',
                success:function (res) {
                    alert("success"+res['message']);
                },
                error:function (res) {
                    alert("error"+res['message'])
                }
            }
        )
})
});
