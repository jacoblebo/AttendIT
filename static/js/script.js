console.log("Script loaded");

// Utility functions
const getElement = (id) => document.getElementById(id);
const setupModal = (modalId, openBtnId, closeSelector) => {
    const modal = getElement(modalId);
    const openBtn = getElement(openBtnId);
    const closeBtn = modal?.querySelector(closeSelector);

    if (!modal || !openBtn || !closeBtn) {
        console.error(`Missing modal setup for: ${modalId}`);
        return;
    }

    openBtn.onclick = () => (modal.style.display = "block");
    closeBtn.onclick = () => (modal.style.display = "none");
    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
};

// Form handlers
const handleFormSubmit = (formId, callback) => {
    const form = getElement(formId);
    if (!form) return;
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        callback(new FormData(form));
    });
};

// Fetch utility
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

// Specific handlers
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

// Initialization
document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM fully loaded and parsed");

    // Modal setups
    setupModal("create-course-modal", "create-course-btn", ".close");
    setupModal("enroll-course-modal", "enroll-course-btn", ".close");
    setupModal("create-session-modal", "open-create-session-modal-btn", ".close");
    setupModal("edit-session-modal", "open-edit-session-modal-btn", ".close");

    // Form setups
    handleFormSubmit("im-here-form", handleAttendanceSubmit);

    // New session buttons
    document.querySelectorAll(".new-session-btn").forEach((button) => {
        button.addEventListener("click", () => {
            const courseId = button.closest(".course-card").getAttribute("data-course-id");
            // Open the create session modal and set the course ID
            const modal = getElement("create-session-modal");
            modal.style.display = "block";
            getElement("course-id").value = courseId;
        });
    });

    // Edit course buttons
    document.querySelectorAll(".edit-course-btn").forEach((button) => {
        button.addEventListener("click", () => {
            const container = button.closest(".course-card");
            const form = container.querySelector(".edit-course-form");
            const closeButton = container.querySelector(".close-edit-course-btn");
            form.style.display = "flex";
            button.style.display = "none";
            closeButton.style.display = "inline";
        });
    });

    // Close edit course buttons
    document.querySelectorAll(".close-edit-course-btn").forEach((button) => {
        button.addEventListener("click", () => {
            const container = button.closest(".course-card");
            const form = container.querySelector(".edit-course-form");
            const editButton = container.querySelector(".edit-course-btn");
            form.style.display = "none";
            button.style.display = "none";
            editButton.style.display = "inline";
        });
    });

    // Toggle sessions buttons
    document.querySelectorAll(".toggle-sessions-btn").forEach((button) => {
        button.addEventListener("click", () => {
            const courseId = button.getAttribute("data-course-id");
            const courseCard = document.querySelector(`.course-card[data-course-id="${courseId}"]`);
            const allSessions = courseCard.querySelector(".all-sessions");
            if (allSessions.style.display === "none") {
                allSessions.style.display = "block";
                button.textContent = "Show Less";
            } else {
                allSessions.style.display = "none";
                button.textContent = "Show All Sessions";
            }
        });
    });

    document.querySelectorAll(".delete-course-btn").forEach((button) => {
        button.addEventListener("click", async () => {
            const courseId = button.closest(".course-card").getAttribute("data-course-id");
            if (confirm("Are you sure you want to delete this course and all its associated records?")) {
                try {
                    const response = await fetch(`/delete_class/${courseId}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value,
                        },
                    });
                    const result = await response.json();
                    if (result.success) {
                        location.reload();
                    } else {
                        alert("Failed to delete course: " + result.message);
                    }
                } catch (error) {
                    console.error("Error deleting course:", error);
                    alert("An error occurred while deleting the course.");
                }
            }
        });
    });

    document.querySelectorAll(".edit-session-btn").forEach((button) => {
        button.addEventListener("click", () => {
            const sessionId = button.closest("tr").getAttribute("data-session-id");
            const sessionStartDate = button.closest("tr").querySelector(".session-start-date").textContent;
            const sessionEndDate = button.closest("tr").querySelector(".session-end-date").textContent;
    
            // Populate the modal with session details
            document.getElementById("edit-session-id").value = sessionId;
            document.getElementById("edit-session-start-date").value = sessionStartDate;
            document.getElementById("edit-session-end-date").value = sessionEndDate;
    
            // Open the modal
            const modal = document.getElementById("edit-session-modal");
            modal.style.display = "block";
        });
    });
    
    // Close the modal when the user clicks on <span> (x)
    document.querySelector("#edit-session-modal .close").addEventListener("click", () => {
        document.getElementById("edit-session-modal").style.display = "none";
    });
    
    // Close the modal when the user clicks anywhere outside of the modal
    window.addEventListener("click", (event) => {
        const modal = document.getElementById("edit-session-modal");
        if (event.target == modal) {
            modal.style.display = "none";
        }
    });

    document.getElementById("edit-session-form").addEventListener("submit", async (event) => {
        event.preventDefault();
    
        const formData = new FormData(event.target);
        const sessionId = formData.get("session_id");
        const startDate = formData.get("start_date");
        const endDate = formData.get("end_date");
    
        try {
            const response = await fetch(`/edit_session/${String(sessionId)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value,
                },
                body: JSON.stringify({
                    start_date: startDate,
                    end_date: endDate
                }),
            });
    
            const result = await response.json();
            if (result.success) {
                location.reload();
            } else {
                alert("Failed to update session: " + result.message);
            }
        } catch (error) {
            console.error("Error updating session:", error);
            alert("An error occurred while updating the session.");
        }
    });

    document.querySelectorAll(".download-session-btn").forEach((button) => {
        button.addEventListener("click", () => {
            const sessionId = button.closest("tr").getAttribute("data-session-id");
            window.location.href = `/download_attendance/${sessionId}`;
        });
    });
    
    document.querySelectorAll(".download-session-btn").forEach((button) => {
        button.addEventListener("click", () => {
            const sessionId = button.getAttribute("data-session-id");
            console.log("Download Session ID:", sessionId); // Debugging line
            window.location.href = `/download_attendance/${sessionId}`;
        });
    });
    
    document.querySelectorAll(".edit-session-btn").forEach((button) => {
        button.addEventListener("click", () => {
            const sessionId = button.getAttribute("data-session-id");
            console.log("Edit Session ID:", sessionId); // Debugging line
            const sessionStartDate = button.closest("tr").querySelector(".session-start-date").textContent;
            const sessionEndDate = button.closest("tr").querySelector(".session-end-date").textContent;
    
            // Populate the modal with session details
            document.getElementById("edit-session-id").value = sessionId;
            document.getElementById("edit-session-start-date").value = sessionStartDate;
            document.getElementById("edit-session-end-date").value = sessionEndDate;
    
            // Open the modal
            const modal = document.getElementById("edit-session-modal");
            modal.style.display = "block";
        });
    });
    
    document.querySelectorAll(".delete-session-btn").forEach((button) => {
        button.addEventListener("click", async () => {
            const sessionId = button.getAttribute("data-session-id");
            console.log("Delete Session ID:", sessionId); // Debugging line
            if (confirm("Are you sure you want to delete this session and all its associated records?")) {
                try {
                    const response = await fetch(`/delete_session/${sessionId}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value,
                        },
                    });
                    const result = await response.json();
                    if (result.success) {
                        location.reload();
                    } else {
                        alert("Failed to delete session: " + result.message);
                    }
                } catch (error) {
                    console.error("Error deleting session:", error);
                    alert("An error occurred while deleting the session.");
                }
            }
        });
    });
});