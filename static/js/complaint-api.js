const complaintForm = document.getElementById("complaintForm");
const formMessage = document.getElementById("formMessage");

complaintForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const image = document.getElementById("image").files[0];

    if (image) {
        const allowedTypes = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ];

        if (!allowedTypes.includes(image.type)) {
            formMessage.textContent =
                "Please select a JPG, PNG, or WebP image.";
            return;
        }

        if (image.size > 5 * 1024 * 1024) {
            formMessage.textContent =
                "Image must be smaller than 5 MB.";
            return;
        }
    }

    formMessage.textContent = "Submitting complaint...";
    formMessage.style.color = "#2563eb";

    const submitButton = complaintForm.querySelector(
        'button[type="submit"]'
    );

    submitButton.disabled = true;

    try {
        const formData = new FormData(complaintForm);

        const response = await fetch("/api/complaints", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(
                result.message || "Complaint submission failed."
            );
        }

        formMessage.style.color = "#047857";
        formMessage.innerHTML =
            "<strong>✓ Complaint submitted successfully!</strong><br>Your tracking ID is: " +
            "<strong><a href='/track?id=" + encodeURIComponent(result.complaint_id) + "' style='color:#047857;text-decoration:underline;'>" +
            result.complaint_id + "</a></strong><br><small>Save this tracking ID to check the status of your issue.</small>";

        complaintForm.reset();

    } catch (error) {
        formMessage.style.color = "#b91c1c";
        formMessage.textContent =
            "Unable to submit complaint: " + error.message;
    } finally {
        submitButton.disabled = false;
    }
});
