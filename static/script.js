// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    
    // 获取页面上的元素
    const roleSelector = document.getElementById('role-selector');
    const coordinatorView = document.getElementById('coordinator-view');
    const lecturerView = document.getElementById('lecturer-view');
    const studentView = document.getElementById('student-view');

    const generateBtn = document.getElementById('generate-btn');
    const downloadBtn = document.getElementById('download-btn');

    // 默认显示协调员视图
    coordinatorView.classList.remove('hidden');

    // 监听角色选择器的变化
    roleSelector.addEventListener('change', function() {
        // 先隐藏所有视图
        coordinatorView.classList.add('hidden');
        lecturerView.classList.add('hidden');
        studentView.classList.add('hidden');

        // 根据选择的值，显示对应的视图
        const selectedRole = roleSelector.value;
        if (selectedRole === 'coordinator') {
            coordinatorView.classList.remove('hidden');
        } else if (selectedRole === 'lecturer') {
            lecturerView.classList.remove('hidden');
        } else if (selectedRole === 'student') {
            studentView.classList.remove('hidden');
        }
    });

    // --- 模拟按钮功能 ---
    // 为“自动生成时间表”按钮添加点击事件
    generateBtn.addEventListener('click', function() {
        // 在真实项目中，这里会向后端发送一个请求
        alert('正在连接后端生成时间表... (这是一个模拟操作)');
        // 模拟成功后的提示
        alert('时间表草稿已生成！');
    });

    // 为“下载Excel”按钮添加点击事件
    downloadBtn.addEventListener('click', function() {
        // 在真实项目中，这里会请求后端的下载API
        alert('正在准备下载Excel文件... (这是一个模拟操作)');
    });
});