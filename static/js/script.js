$(document).ready(function () {

    $("form").on("click", "button", create);

    function create(event) {
        event.preventDefault();

        var allData = $("form").serialize();

        $.ajax({
            url: "accounts/register_behvarz.html",
            method: "post",
            data: allData,
            success: function (response) {
                console.log(response)
                if (response == 1) {
                    $("input").val("");
                    read();
                } else {
                    alert("تما فیلد ها باید پر شوند.")
                }
            }
        })
    }


    function read() {
        $.ajax({
            url: "php/read.php",
            method: "get",
            success: function (response) {
                var data = JSON.parse(response);

                console.log(data)
                var items = "";
                if (data.length > 0) {
                    for (var i in data) {
                        items += '<tr>\n' +
                            '    <td>' + data[i].id + '</td>\n' +
                            '    <td class="editable fname">' + data[i].fname + '</td>\n' +
                            '    <td class="editable lname">' + data[i].lname + '</td>\n' +
                            '    <td class="editable skill">' + data[i].skill + '</td>\n' +
                            '    <td><button id="' + data[i].id + '" class="btn btn-info update">ویرایش</button></td>\n ' +
                            '    <td><button id="' + data[i].id + '" class="btn btn-danger delete">حذف</button></td>\n ' +
                            '</tr>'
                    }
                } else {
                    items += '<tr><td colspan="6">هنوز هیچ داده ای وارد نشده</td></tr>'
                }

                $("table tbody").html("").append(items)
            }
        })
    }

    read();


    $("table").on("click", ".update", update);

    function update() {

        if (!$(this).hasClass("active")) {
            $(this).parent().siblings(".editable").each(function () {
                var val = $(this).html();
                $(this).html("<input type='text' value='" + val + "'>")

            })
            $(this).addClass("active");
        } else {

            var id = $(this).attr("id");
            var fname = $(this).parent().siblings(".fname").children("input").val();
            var lname = $(this).parent().siblings(".lname").children("input").val();
            var skill = $(this).parent().siblings(".skill").children("input").val();


            $.ajax({
                url: "php/update.php",
                method: "post",
                data: {
                    id: id,
                    fname: fname,
                    lname: lname,
                    skill: skill
                },
                success: function (response) {
                    read();
                }
            })
        }

    }


    $("table").on("click", ".delete", deleteUser);

    function deleteUser() {
        var id = $(this).attr("id");

        $.ajax({
            url: "php/delete.php",
            method: "post",
            data: {id: id},
            success: function (response) {
                read();
            }
        })
    }
})

// مدیریت خطا در هنگام تکمیل کردن فیلد ها
// انتخاب المان‌های DOM مورد نیاز
var typeSelect = document.getElementById('id_type');
var errorMessage = document.getElementById('type-error');

// تابع بررسی و نمایش پیغام خطا
function displayError() {
    if (typeSelect.value === '') {
        typeSelect.classList.add('error');
        errorMessage.classList.add('show');
    } else {
        typeSelect.classList.remove('error');
        errorMessage.classList.remove('show');
    }
}

// بررسی و نمایش پیغام خطا هنگام تغییر مقدار فیلد
typeSelect.addEventListener('change', displayError);

// بررسی و نمایش پیغام خطا هنگام ارسال فرم
document.querySelector('form').addEventListener('submit', function (event) {
    displayError();

    if (typeSelect.value === '') {
        event.preventDefault(); // متوقف کردن ارسال فرم
    }
});