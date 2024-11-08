console.log("Script loaded");

function toggleForms() {
    console.log("Swapping forms");
    let loginForm = document.getElementById('login-form');
    let registerForm = document.getElementById('register-form');
    let toggleLink = document.getElementById('toggle-link');
    let pageTitle = document.getElementById('page-title');

    if (loginForm.style.display === 'none') {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
        pageTitle.innerHTML = "Login";
        toggleLink.innerHTML = "Don't have an account? <button type='button' onclick='toggleForms()'>Register</button>";
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
        pageTitle.innerHTML = "Register";
        toggleLink.innerHTML = "Already have an account? <button type='button' onclick='toggleForms()'>Login</button>";
    }
}

function handleImHereFormSubmit(event) {
    event.preventDefault();
    let courseId = document.getElementById('course-id').value;
    let bypassCode = document.getElementById('bypass-code').value;
    fetch(`/mark_attendance/${courseId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
        },
        body: JSON.stringify({
            bypass_code: bypassCode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Attendance marked successfully');
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error marking attendance:', error));
}

function setupImHereForm() {
    let imHereForm = document.getElementById('im-here-form');
    if (imHereForm) {
        imHereForm.addEventListener('submit', handleImHereFormSubmit);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed'); // Log when DOM is loaded

    function setupCreateCourseModal() {
        console.log('Setting up create course modal'); // Log when setting up the modal

        let modal = document.getElementById('create-course-modal');
        let btn = document.getElementById('create-course-btn');
        let span = modal ? modal.getElementsByClassName('close')[0] : null;

        if (!modal) {
            console.error('Modal with id create-course-modal not found');
            return;
        }
        if (!btn) {
            console.error('Button with id create-course-btn not found');
            return;
        }
        if (!span) {
            console.error('Close button not found in modal with id create-course-modal');
            return;
        }

        btn.onclick = function() {
            console.log('create-course-btn button clicked'); // Print to console
            modal.style.display = 'block';
        };

        span.onclick = function() {
            modal.style.display = 'none';
        };

        window.onclick = function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        };
    }

    function setupEnrollCourseModal() {
        console.log('Setting up enroll course modal'); // Log when setting up the modal

        let modal = document.getElementById('enroll-course-modal');
        let btn = document.getElementById('enroll-course-btn');
        let span = modal ? modal.getElementsByClassName('close')[0] : null;

        if (!modal) {
            console.error('Modal with id enroll-course-modal not found');
            return;
        }
        if (!btn) {
            console.error('Button with id enroll-course-btn not found');
            return;
        }
        if (!span) {
            console.error('Close button not found in modal with id enroll-course-modal');
            return;
        }

        btn.onclick = function() {
            console.log('enroll-course-btn button clicked'); // Print to console
            modal.style.display = 'block';
        };

        span.onclick = function() {
            modal.style.display = 'none';
        };

        window.onclick = function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        };
    }

    function setupCourseInfoModal() {
        document.querySelectorAll('.course-card').forEach(card => {
            card.addEventListener('click', function() {
                document.querySelectorAll('.course-card').forEach(c => c.classList.remove('selected'));
                this.classList.add('selected');
                let courseId = this.getAttribute('data-course-id');
                let userRole = document.getElementById('user-role').value;
    
                if (userRole == 1) { // 1 for professor
                    fetch(`/course_info/${courseId}`)
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('course-name').textContent = `Course Name: ${data.name}`;
                            document.getElementById('course-join-code').textContent = `Join Code: ${data.join_code}`;
                            document.getElementById('course-enrollment').textContent = `Enrollment: ${data.enrollment}`;
                            if (data.next_session) {
                                document.getElementById('next-session-info').textContent = `Next Session: ${data.next_session.start_date} to ${data.next_session.end_date}, Bypass Code: ${data.next_session.bypass_code}`;
                            } else {
                                document.getElementById('next-session-info').textContent = 'No upcoming sessions';
                            }
                            document.getElementById('course-info-modal').setAttribute('data-course-id', courseId);
                            document.getElementById('course-info-modal').style.display = 'block';
                        })
                        .catch(error => console.error('Error fetching course info:', error));
                } else {
                    fetch(`/student_course_info/${courseId}`)
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('student-course-name').textContent = `Course Name: ${data.name}`;
                            document.getElementById('next-session-info').textContent = `Next Session: ${data.next_session}`;
                            document.getElementById('course-id').value = courseId;
                            document.getElementById('student-course-info-modal').style.display = 'block';
                        })
                        .catch(error => console.error('Error fetching course info:', error));
                }
            });
        });
    
        let courseInfoModal = document.getElementById('course-info-modal');
        let courseInfoClose = courseInfoModal ? courseInfoModal.getElementsByClassName('close')[0] : null;
        if (!courseInfoModal) {
            console.error('Modal with id course-info-modal not found');
            return;
        }
        if (!courseInfoClose) {
            console.error('Close button not found in modal with id course-info-modal');
            return;
        }
        courseInfoClose.onclick = function() {
            courseInfoModal.style.display = 'none';
        };
        window.onclick = function(event) {
            if (event.target === courseInfoModal) {
                courseInfoModal.style.display = 'none';
            }
        };
    }
    
    

    function setupCreateSessionModal() {
        let openCreateSessionModalBtn = document.getElementById('open-create-session-modal-btn');
        let createSessionModal = document.getElementById('create-session-modal');
        let span = createSessionModal ? createSessionModal.getElementsByClassName('close')[0] : null;
    
        if (!createSessionModal) {
            console.error('Modal with id create-session-modal not found');
            return;
        }
        if (!openCreateSessionModalBtn) {
            console.error('Button with id open-create-session-modal-btn not found');
            return;
        }
        if (!span) {
            console.error('Close button not found in modal with id create-session-modal');
            return;
        }
    
        openCreateSessionModalBtn.onclick = function() {
            let courseId = document.querySelector('.course-card.selected').getAttribute('data-course-id');
            document.getElementById('course-id').value = courseId;
            createSessionModal.style.display = 'block';
        };
    
        span.onclick = function() {
            createSessionModal.style.display = 'none';
        };
    
        window.onclick = function(event) {
            if (event.target === createSessionModal) {
                createSessionModal.style.display = 'none';
            }
        };
    }
    function setupDownloadAttendanceButton() {
        let downloadAttendanceBtn = document.getElementById('download-attendance-btn');
        if (downloadAttendanceBtn) {
            downloadAttendanceBtn.addEventListener('click', function() {
                let courseId = document.getElementById('course-info-modal').getAttribute('data-course-id');
                window.location.href = `/download_attendance/${courseId}`;
            });
        }
    }

    function setupStudentCourseInfoModal() {
        let studentCourseInfoModal = document.getElementById('student-course-info-modal');
        let closeBtn = studentCourseInfoModal ? studentCourseInfoModal.getElementsByClassName('close')[0] : null;
    
        if (!studentCourseInfoModal) {
            console.error('Modal with id student-course-info-modal not found');
            return;
        }
        if (!closeBtn) {
            console.error('Close button not found in modal with id student-course-info-modal');
            return;
        }
    
        closeBtn.onclick = function() {
            studentCourseInfoModal.style.display = 'none';
        };
    
        window.onclick = function(event) {
            if (event.target === studentCourseInfoModal) {
                studentCourseInfoModal.style.display = 'none';
            }
        };
    }

    // Call the functions to set up the modals and buttons
    setupCreateCourseModal();
    setupEnrollCourseModal();
    setupCourseInfoModal();
    setupCreateSessionModal();
    setupStudentCourseInfoModal();
    setupImHereForm();
    setupDownloadAttendanceButton();
});