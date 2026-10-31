const trackingForm = document.getElementById("trackingForm");
const trackingMessage = document.getElementById("trackingMessage");
const trackingDetails = document.getElementById("trackingDetails");

async function checkComplaintStatus(complaintId) {
    if (!complaintId) {
        trackingMessage.style.color = "#92400e";
        trackingMessage.textContent = "Please enter your complaint ID.";
        return;
    }

    trackingMessage.style.color = "#2563eb";
    trackingMessage.textContent = "Checking complaint status...";

    const submitButton = trackingForm.querySelector('button[type="submit"]');
    if (submitButton) submitButton.disabled = true;

    try {
        const response = await fetch(
            "/api/complaints/" + encodeURIComponent(complaintId),
            { method: "GET" }
        );

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(
                result.message || "Unable to find complaint with ID: " + complaintId
            );
        }

        const complaint = result.complaint || result;

        const allowedStatuses = [
            "Pending",
            "In Progress",
            "Resolved"
        ];

        if (!allowedStatuses.includes(complaint.status)) {
            throw new Error("Unexpected complaint status received.");
        }

        const statusColors = {
            "Pending": "#92400e",
            "In Progress": "#1d4ed8",
            "Resolved": "#166534"
        };

        trackingMessage.style.color = statusColors[complaint.status] || "#2563eb";
        trackingMessage.innerHTML =
            "<strong>Complaint: " + complaintId + "</strong><br>" +
            "Current Status: <span class='status-badge status-" + 
            (complaint.status === "In Progress" ? "progress" : complaint.status.toLowerCase()) + 
            "'>" + complaint.status + "</span>";

        if (trackingDetails && complaint.title) {
            trackingDetails.style.display = "block";
            trackingDetails.innerHTML = `
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: left; margin-top: 15px;">
                    <h3 style="margin: 0 0 10px; font-size: 17px; color: #101f3b;">${complaint.title}</h3>
                    <p style="margin: 5px 0; font-size: 13px; color: #64748b;"><strong>Category:</strong> ${complaint.category} &nbsp;|&nbsp; <strong>Location:</strong> ${complaint.location}</p>
                    <p style="margin: 5px 0; font-size: 13px; color: #64748b;"><strong>Priority:</strong> ${complaint.priority} &nbsp;|&nbsp; <strong>Submitted on:</strong> ${complaint.created_at || 'Recently'}</p>
                </div>
            `;
        }

    } catch (error) {
        trackingMessage.style.color = "#b91c1c";
        trackingMessage.textContent = "Tracking failed: " + error.message;
        if (trackingDetails) trackingDetails.style.display = "none";
    } finally {
        if (submitButton) submitButton.disabled = false;
    }
}

trackingForm.addEventListener("submit", function (event) {
    event.preventDefault();
    const complaintId = document.getElementById("complaintId").value.trim();
    checkComplaintStatus(complaintId);
});

// Auto-track if ID is provided in query string: /track?id=CMP-XXXXXX
window.addEventListener("DOMContentLoaded", function () {
    const params = new URLSearchParams(window.location.search);
    const queryId = params.get("id");
    if (queryId) {
        const input = document.getElementById("complaintId");
        if (input) {
            input.value = queryId;
            checkComplaintStatus(queryId);
        }
    }
});
