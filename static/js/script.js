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
    function setupModal(modalId, buttonId) {
        let modal = document.getElementById(modalId);
        let btn = document.getElementById(buttonId);
        let span = modal.getElementsByClassName('close')[0];

        btn.onclick = function() {
            modal.style.display = 'block';
        }

        span.onclick = function() {
            modal.style.display = 'none';
        }

        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
    }

    setupModal('create-course-modal', 'create-course-btn');

    document.querySelectorAll('.course-card').forEach(card => {
        card.addEventListener('click', function() {
            let courseId = this.getAttribute('data-course-id');
            console.log(`Fetching course info for course ID: ${courseId}`);
            fetch(`/course_info/${courseId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('course-name').textContent = `Information Fori: ${data.name}`;
                    document.getElementById('course-join-code').textContent = `Join Code: ${data.join_code}`;
                    document.getElementById('course-enrollment').textContent = `Enrollment: ${data.enrollment}`;
                    document.getElementById('course-info-modal').style.display = 'block';
                })
                .catch(error => console.error('Error fetching course info:', error));
        });
    });

    setupModal('course-info-modal', 'course-info-btn');
});