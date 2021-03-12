 $("#myTab li").each(function (index) {
            $(this).click(function () {
                $("#myTab li.active").removeClass("active");
                $(this).addClass("active");
                if (index == 0) {
                    $('#myTab a[href="#home"]').tab('show');
                } else if (index == 1) {
                    $('#myTab a[href="#collect"]').tab('show');
                } else if (index == 2) {
                    $('#myTab a[href="#follow"]').tab('show');
                }
            })
 })
