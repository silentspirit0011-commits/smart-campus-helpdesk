const complaintForm = document.getElementById("complaintForm");
const formMessage = document.getElementById("formMessage");

complaintForm.addEventListener("submit", function (event) {
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

    formMessage.textContent =
        "Form validated! Live complaint submission is active via complaint-api.js.";
});
