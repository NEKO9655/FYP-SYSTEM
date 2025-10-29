document.addEventListener('DOMContentLoaded', function() {
  
    const roleSelector = document.getElementById('role-selector');
    const coordinatorView = document.getElementById('coordinator-view');
    const lecturerView = document.getElementById('lecturer-view');
    const studentView = document.getElementById('student-view');

    const generateBtn = document.getElementById('generate-btn');
    const downloadBtn = document.getElementById('download-btn');

    coordinatorView.classList.remove('hidden');

    roleSelector.addEventListener('change', function() {
        coordinatorView.classList.add('hidden');
        lecturerView.classList.add('hidden');
        studentView.classList.add('hidden');

        const selectedRole = roleSelector.value;
        if (selectedRole === 'coordinator') {
            coordinatorView.classList.remove('hidden');
        } else if (selectedRole === 'lecturer') {
            lecturerView.classList.remove('hidden');
        } else if (selectedRole === 'student') {
            studentView.classList.remove('hidden');
        }
    });

    generateBtn.addEventListener('click', function() {
        alert('Connecting to backend to generate schedule... (This is a simulation operation)');
        alert('Draft timetable generated!');
    });

    downloadBtn.addEventListener('click', function() {
        alert('Preparing to download Excel file... (This is a simulation operation)');
    });
});