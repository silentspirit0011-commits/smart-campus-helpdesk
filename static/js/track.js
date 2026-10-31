const trackingForm = document.getElementById("trackingForm");
const trackingMessage = document.getElementById("trackingMessage");

trackingForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const complaintId = document
        .getElementById("complaintId")
        .value.trim();

    if (!complaintId) {
        trackingMessage.textContent =
            "Please enter your complaint ID.";
        return;
    }

    trackingMessage.textContent =
        "Complaint ID entered: " + complaintId +
        ". Live tracking active via track-api.js.";
});
