document.addEventListener("DOMContentLoaded", function () {
    // 初始化 SimpleMDE 编辑器
    const simplemde = new SimpleMDE({
        element: document.getElementById("editor-container"),
        spellChecker: false, // 是否启用拼写检查
        placeholder: "在此输入内容...",
        autosave: {
            enabled: true, // 自动保存
            uniqueId: "blog-content", // 自动保存的唯一标识
            delay: 1000, // 保存间隔（毫秒）
        },
        toolbar: [
            "bold", "italic", "heading", "|",
            "quote", "unordered-list", "ordered-list", "|",
            "link", "image", "table", "|",
            "preview", "side-by-side", "fullscreen", "|",
            "guide"
        ],
    });

    // 提交时保存编辑器内容到隐藏输入框
    document.getElementById("submit-btn").addEventListener("click", function (event) {
        event.preventDefault();  // 防止表单的默认提交行为

        // 获取 Markdown 内容
        const markdownContent = simplemde.value();
        console.log("Markdown 内容:", markdownContent); // 调试输出

        // 将编辑器内容保存到隐藏的 content 输入框
        document.getElementById("content-input").value = markdownContent;

        // 获取表单并提交
        const form = document.getElementById("blog-form");
        form.submit(); // 提交表单
    });
});
