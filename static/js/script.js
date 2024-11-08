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
                let courseId = this.getAttribute('data-course-id');
                let userRole = document.getElementById('user-role').value; // Assuming you have a hidden input or some element with the user's role
    
                if (userRole == 1) { // 1 for professor
                    fetch(`/course_info/${courseId}`)
                        .then(response => response.json())
                        .then(data => {
                            // Update the modal content
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
                            // Update the modal content
                            document.getElementById('student-course-name').textContent = `Course Name: ${data.name}`;
                            document.getElementById('next-session-info').textContent = `Next Session: ${data.next_session}`;
                            document.getElementById('im-here-btn').setAttribute('data-course-id', courseId);
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
        let createSessionForm = document.getElementById('create-session-form');
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
            console.log('open-create-session-modal-btn button clicked'); // Print to console
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

        createSessionForm.onsubmit = function(event) {
            event.preventDefault();
            let courseId = document.getElementById('course-info-modal').getAttribute('data-course-id');
            let sessionStartDate = document.getElementById('session-start-date').value;
            let sessionStartTime = document.getElementById('session-start-time').value;
            let sessionEndTime = document.getElementById('session-end-time').value;

            fetch('/create_session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                },
                body: JSON.stringify({
                    class_id: courseId,
                    session_start_date: sessionStartDate,
                    session_start_time: sessionStartTime,
                    session_end_time: sessionEndTime
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Session created successfully');
                    createSessionModal.style.display = 'none';
                    // Refresh the course info modal to show the new session
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
                        })
                        .catch(error => console.error('Error fetching course info:', error));
                } else {
                    alert('Error creating session');
                }
            })
            .catch(error => console.error('Error creating session:', error));
        };
    }

    function setupImHereButton() {
        let imHereBtn = document.getElementById('im-here-btn');
        if (imHereBtn) {
            imHereBtn.addEventListener('click', function() {
                let courseId = this.getAttribute('data-course-id');
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
            });
        }
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

    // Call the functions to set up the modals and buttons
    setupCreateCourseModal();
    setupEnrollCourseModal();
    setupCourseInfoModal();
    setupStudentCourseInfoModal();
    setupCreateSessionModal();
    setupImHereButton();
    setupDownloadAttendanceButton();
});