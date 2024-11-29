const getElement = (id) => document.getElementById(id);

const setupModal = (modalId, openBtnId, closeSelector) => {
    const modal = getElement(modalId);
    const openBtn = getElement(openBtnId);
    const closeBtn = modal?.querySelector(closeSelector);

    if (!modal || !openBtn || !closeBtn) {
        console.error(`Missing modal setup for: ${modalId}`);
        return;
    }

    openBtn.onclick = () => (modal.style.display = "flex");
    closeBtn.onclick = () => (modal.style.display = "none");
    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
};

const handleFormSubmit = (formId, callback) => {
    const form = getElement(formId);
    if (!form) return;
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        callback(new FormData(form));
    });
};

const fetchData = async (url, method, body) => {
    try {
        const response = await fetch(url, {
            method,
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('input[name="csrf_token"]').value,
            },
            body: JSON.stringify(body),
        });
        return await response.json();
    } catch (error) {
        console.error("Fetch error:", error);
    }
};

const handleAttendanceSubmit = async (formData) => {
    const courseId = formData.get("course-id");
    const bypassCode = formData.get("bypass-code");
    const data = await fetchData(`/mark_attendance/${courseId}`, "POST", { bypass_code: bypassCode });

    if (data?.success) {
        alert("Attendance marked successfully");
    } else {
        alert("Failed to mark attendance");
    }
};

const handleDeleteSession = async (sessionId) => {
    if (confirm('Are you sure you want to delete this session?')) {
        const response = await fetch(`/delete_session/${sessionId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
            }
        });
        const data = await response.json();
        if (data.success) {
            alert('Session deleted successfully');
            location.reload();
        } else {
            alert('Error deleting session: ' + data.message);
        }
    }
};

const handleDeleteCourse = async (courseId) => {
    if (confirm('Are you sure you want to delete this course?')) {
        const response = await fetch(`/delete_class/${courseId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
            }
        });
        const data = await response.json();
        if (data.success) {
            alert('Course deleted successfully');
            location.reload();
        } else {
            alert('Error deleting course: ' + data.message);
        }
    }
};

const toggleForms = () => {
    const loginForm = getElement('login-form');
    const registerForm = getElement('register-form');
    const toggleLink = getElement('toggle-link');

    if (loginForm.style.display === 'none') {
        loginForm.style.display = 'flex';
        registerForm.style.display = 'none';
        toggleLink.innerHTML = "Don't have an account? <button type='button' onclick='toggleForms()'>Register</button>";
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'flex';
        toggleLink.innerHTML = "Already have an account? <button type='button' onclick='toggleForms()'>Login</button>";
    }
};

const handleViewEnrollment = async (courseId) => {
    const response = await fetch(`/view_enrollment/${courseId}`);
    const data = await response.json();
    const enrollmentList = document.getElementById('enrollment-list');
    enrollmentList.innerHTML = '';
    if (data.success) {
        if (data.students.length > 0) {
            data.students.forEach(student => {
                const listItem = document.createElement('li');
                listItem.textContent = `${student.firstName} ${student.lastName} (${student.email})`;
                enrollmentList.appendChild(listItem);
            });
        } else {
            const listItem = document.createElement('li');
            listItem.textContent = 'No students enrolled in this course.';
            enrollmentList.appendChild(listItem);
        }
        document.getElementById('view-enrollment-modal').style.display = 'flex';
    } else {
        alert('Error fetching enrollment data: ' + data.message);
    }
};

const handleViewAttendance = async (sessionId) => {
    try {
        const response = await fetch(`/view_attendance/${sessionId}`);
        const data = await response.json();
        const attendanceList = document.getElementById('attendance-list');
        
        if (!attendanceList) {
            console.error('attendanceList is null');
            document.getElementById('view-attendance-modal').style.display = 'flex';
            document.getElementById('view-attendance-modal').innerHTML = 'Nobody has registered for your course';
            return;
        }

        attendanceList.innerHTML = '';
        if (data.success) {
            if (data.attendance.length === 0) {
                attendanceList.innerHTML = '<li>Nobody has registered for your course</li>';
            } else {
                data.attendance.forEach(record => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${record.studentName}: ${record.status ? 'Present' : 'Absent'}`;
                    attendanceList.appendChild(listItem);
                });
            }
            document.getElementById('view-attendance-modal').style.display = 'flex';
        } else {
            alert('Error fetching attendance data: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while fetching attendance data.');
    }
};

const handleEditCourse = (button) => {
    const courseId = button.getAttribute('data-course-id');
    const courseName = button.closest('.course-card').querySelector('h2').textContent;
    document.getElementById('course-id').value = courseId;
    document.getElementById('form-course-name').value = courseName;
    document.getElementById('edit-course-modal').style.display = 'flex';
};

const handleEditSession = (button) => {
    const sessionId = button.getAttribute('data-session-id');
    const startDate = button.closest('tr').querySelector('.session-start-date').value;
    const endDate = button.closest('tr').querySelector('.session-end-date').value;

    document.getElementById('edit-session-id').value = sessionId;
    document.getElementById('edit-session-start-date').value = startDate;
    document.getElementById('edit-session-end-date').value = endDate;

    document.getElementById('edit-session-modal').style.display = 'flex';
};

const handleDownloadSession = (sessionId) => {
    window.location.href = `/download_attendance/${sessionId}`;
};

document.addEventListener('DOMContentLoaded', function() {

    const toggleFormsBtn = document.getElementById('toggle-forms-btn');
    if (toggleFormsBtn) {
        toggleFormsBtn.addEventListener('click', toggleForms);
    }

    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const toggleLink = document.getElementById('toggle-link');

    function toggleForms() {
        if (loginForm.classList.contains('hidden')) {
            loginForm.classList.remove('hidden');
            registerForm.classList.add('hidden');
            toggleLink.innerHTML = "Don't have an account? <button type='button' id='toggle-forms-btn'>Register</button>";
        } else {
            loginForm.classList.add('hidden');
            registerForm.classList.remove('hidden');
            toggleLink.innerHTML = "Already have an account? <button type='button' id='toggle-forms-btn'>Login</button>";
        }
        // Re-attach the event listener to the new button
        const newToggleFormsBtn = document.getElementById('toggle-forms-btn');
        if (newToggleFormsBtn) {
            newToggleFormsBtn.addEventListener('click', toggleForms);
        }
    }

    document.querySelectorAll('.view-attendance-btn').forEach(button => {
        button.addEventListener('click', () => handleViewAttendance(button.getAttribute('data-session-id')));
    });

    document.querySelectorAll('.edit-course-btn').forEach(button => {
        button.addEventListener('click', () => handleEditCourse(button));
    });

    document.querySelectorAll('.delete-session-btn').forEach(button => {
        button.addEventListener('click', () => handleDeleteSession(button.getAttribute('data-session-id')));
    });

    document.querySelectorAll('.view-enrollment-btn').forEach(button => {
        button.addEventListener('click', () => handleViewEnrollment(button.getAttribute('data-course-id')));
    });

    document.querySelectorAll('.edit-session-btn').forEach(button => {
        button.addEventListener('click', () => handleEditSession(button));
    });

    document.querySelectorAll('.new-session-btn').forEach(button => {
        button.addEventListener('click', () => {
            const courseId = button.getAttribute('data-course-id');
            document.getElementById('new-session-course-id').value = courseId;
            document.getElementById('create-session-modal').style.display = 'flex';
        });
    });

    document.getElementById('create-course-btn').addEventListener('click', () => {
        document.getElementById('create-course-modal').style.display = 'flex';
    });

    document.querySelectorAll('.delete-course-btn').forEach(button => {
        button.addEventListener('click', () => handleDeleteCourse(button.getAttribute('data-course-id')));
    });

    document.querySelectorAll('.download-session-btn').forEach(button => {
        button.addEventListener('click', () => handleDownloadSession(button.getAttribute('data-session-id')));
    });
    
    document.querySelectorAll('.modal .close').forEach(span => {
        span.addEventListener('click', function() {
            this.closest('.modal').style.display = 'none';
        });
    });
    
    setupModal('enroll-course-modal', 'enroll-course-btn', '.close');
    
    handleFormSubmit('enroll-course-form', async (formData) => {
        try {
            const response = await fetch('/enroll_course', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': formData.get('csrf_token')
                },
                body: new URLSearchParams(formData)
            });
    
            const contentType = response.headers.get('content-type');
            let data;
            if (contentType?.includes('application/json')) {
                data = await response.json();
            } else {
                data = { success: false, message: 'Unexpected response format' };
            }
    
            if (data.success) {
                alert('Enrolled in course successfully');
                location.reload();
            } else {
                alert('Failed to enroll in course: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while enrolling in the course.');
        }
    });

    handleFormSubmit('create-session-form', async (formData) => {
        try {
            const response = await fetch('/create_session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': formData.get('csrf_token')
                },
                body: new URLSearchParams(formData)
            });

            const contentType = response.headers.get('content-type');
            let data;
            if (contentType?.includes('application/json')) {
                data = await response.json();
            } else {
                data = { success: false, message: 'Unexpected response format' };
            }

            if (data.success) {
                alert('Session created successfully');
                location.reload();
            } else {
                alert('Failed to create session: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while creating the session.');
        }
    });

    handleFormSubmit('edit-session-form', async (formData) => {
        const sessionId = formData.get('session_id');
        try {
            const response = await fetch(`/edit_session/${sessionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': formData.get('csrf_token')
                },
                body: new URLSearchParams(formData)
            });

            const data = await response.json();

            if (data.success) {
                alert('Session updated successfully');
                location.reload();
            } else {
                alert('Failed to update session: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while updating the session.');
        }
    });
    
    document.querySelectorAll('.attendance-form').forEach(form => {
        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            const courseId = this.getAttribute('data-course-id');
            const bypassCode = this.querySelector('input[name="bypass_code"]').value;
    
            try {
                const response = await fetch(`/mark_attendance/${courseId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                    },
                    body: JSON.stringify({ bypass_code: bypassCode })
                });
    
                const data = await response.json();
                if (data.success) {
                    alert('Attendance marked successfully');
                    location.reload();
                } else {
                    alert('Failed to mark attendance: ' + data.message);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while marking attendance.');
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Setup modal for enrolling in a course
    setupModal('enroll-course-modal', 'enroll-course-btn', '.close');

    // Handle form submission for enrolling in a course
    handleFormSubmit('enroll-course-form', async (formData) => {
        try {
            const response = await fetch('/enroll_course', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': formData.get('csrf_token')
                },
                body: new URLSearchParams(formData)
            });

            const data = await response.json();

            if (data.success) {
                alert('Enrolled in course successfully');
                location.reload();
            } else {
                alert('Failed to enroll in course: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while enrolling in the course.');
        }
    });

    document.querySelectorAll('.attendance-form').forEach(form => {
        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            const courseId = this.getAttribute('data-course-id');
            const bypassCode = this.querySelector('input[name="bypass_code"]').value;

            try {
                const response = await fetch(`/mark_attendance/${courseId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                    },
                    body: JSON.stringify({ bypass_code: bypassCode })
                });

                const data = await response.json();
                if (data.success) {
                    alert('Attendance marked successfully');
                } else {
                    alert('Failed to mark attendance: ' + data.message);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while marking attendance.');
            }
        });
    });
});