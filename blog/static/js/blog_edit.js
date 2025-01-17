document.addEventListener('DOMContentLoaded', function () {
    const { createEditor, createToolbar } = window.wangEditor;

    // 获取编辑器容器
    const editorContainer = document.querySelector('#editor-container');

    // 获取从 HTML 页面中传递的动态数据
    const existingContent = document.querySelector('#blog-content').getAttribute('data-content');
    const blogTitle = document.querySelector('#title-input').getAttribute('data-title');

    // 检查是否已有编辑器实例
    if (editorContainer.__editor__) {
        // 销毁现有编辑器实例
        editorContainer.__editor__.destroy();
    }

    // 初始化编辑器
    const editor = createEditor({
        selector: '#editor-container',
        html: existingContent || '<p><br></p>',  // 如果没有内容，使用默认空内容
    });

    // 标记该容器已初始化编辑器，防止重复创建
    editorContainer.__editor__ = editor;

    // 初始化工具栏
    createToolbar({
        editor,
        selector: '#toolbar-container',
        config: {}, // 配置工具栏
    });

    // 打印内容确认
    console.log('编辑器内容:', editor.getHtml());

    // Optional: 填充标题
    document.querySelector('#title-input').value = blogTitle || '默认标题';
});
