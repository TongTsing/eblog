$(function () {
    // 获取 CSRF token
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    // 点击获取验证码按钮
    $('#captcha-btn').click(function (e) {
        e.preventDefault(); // 阻止按钮触发表单提交

        var email = $('#email').val(); // 获取邮箱地址

        if (!email) {
            alert('请先输入有效的邮箱地址');
            return;
        }

        // 发送GET请求到指定的URL
        $.ajax({
            url: '/auth/captcha/',  // 发送验证码请求的 URL
            method: 'GET',
            data: {
                'email': email  // 邮箱作为查询参数
            },
            beforeSend: function(xhr, settings) {
                // 添加 CSRF token 到请求头
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            },
            success: function (response) {
                var countdown = 60;
                var $captchaButton = $('#captcha-btn');

                // 禁用按钮，避免多次点击
                $captchaButton.prop('disabled', true);

                // 开始倒计时
                var timer = setInterval(function () {
                    $captchaButton.text(countdown + '秒后重新获取');
                    countdown--;

                    if (countdown < 0) {
                        clearInterval(timer);
                        $captchaButton.text('获取验证码');
                        $captchaButton.prop('disabled', false); // 启用按钮
                    }
                }, 1000);
            },
            error: function () {
                alert('验证码发送失败，请稍后重试');
            }
        });
    });
});
