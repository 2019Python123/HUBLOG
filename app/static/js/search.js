$(document).ready(
    function () {
        var searchinp = document.getElementById('search');
        var listbox = document.getElementById('listbox');
        var timer = null;
        searchinp.oninput = function () {
            clearTimeout(timer);
            var tar = $("#tar").val();

            var data = $('#search').val();
            if (data.trim().length == 0){
                listbox.style.display = "none";
                return;
            }
            timer = setTimeout(
                function () {
                    $.ajax({
                            url : "/search_tips",
                            data : JSON.stringify({'data': data, 'tar': tar}),
                            type:'post',
                            success:function (result) {
                                var html = result;
                                listbox.innerHTML = html;
                                listbox.style.display = 'block';
                                listbox.style.listStyle = 'none';
                            },
                            error:function (res) {
                              console.log('请求失败');
                            }
                        }
                    )
                },200
            )
        }
    }
)