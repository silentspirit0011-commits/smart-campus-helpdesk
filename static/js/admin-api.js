let complaints = [];

const tableBody = document.getElementById("complaintsTableBody");
const searchInput = document.getElementById("searchComplaints");
const statusFilter = document.getElementById("statusFilter");
const tableMessage = document.getElementById("tableMessage");

async function fetchLiveComplaints() {
    try {
        tableMessage.textContent = "Loading complaints from database...";
        const response = await fetch("/api/complaints");

        if (response.status === 401 || response.status === 403) {
            window.location.href = "/admin/login";
            return;
        }

        const result = await response.json();

        if (!Array.isArray(result.complaints)) {
            throw new Error("Invalid complaints response format.");
        }

        complaints = result.complaints;
        tableMessage.textContent = "";
        updateStatistics();
        renderComplaints();
    } catch (err) {
        tableMessage.textContent = "Failed to load complaints: " + err.message;
    }
}

function updateStatistics() {
    document.getElementById("totalCount").textContent =
        complaints.length;

    document.getElementById("pendingCount").textContent =
        complaints.filter(c => c.status === "Pending").length;

    document.getElementById("progressCount").textContent =
        complaints.filter(c => c.status === "In Progress").length;

    document.getElementById("resolvedCount").textContent =
        complaints.filter(c => c.status === "Resolved").length;
}

function makeCell(row, value) {
    const cell = document.createElement("td");
    cell.textContent = value || "—";
    row.appendChild(cell);
    return cell;
}

function renderComplaints() {
    const query = searchInput.value.trim().toLowerCase();
    const selectedStatus = statusFilter.value;

    const filtered = complaints.filter(complaint => {
        const searchableText = [
            complaint.id,
            complaint.title,
            complaint.category,
            complaint.location,
            complaint.student_name || ""
        ].join(" ").toLowerCase();

        return searchableText.includes(query) &&
            (selectedStatus === "All" ||
             complaint.status === selectedStatus);
    });

    tableBody.replaceChildren();

    filtered.forEach(complaint => {
        const row = document.createElement("tr");

        makeCell(row, complaint.id);
        makeCell(row, complaint.title);
        makeCell(row, complaint.category);
        makeCell(row, complaint.location);

        const priorityCell = document.createElement("td");
        const priorityBadge = document.createElement("span");

        const priorityKey = (complaint.priority || "Medium").toLowerCase();
        priorityBadge.className = "priority-badge priority-" + priorityKey;
        priorityBadge.textContent = complaint.priority;
        priorityCell.appendChild(priorityBadge);
        row.appendChild(priorityCell);

        const statusCell = document.createElement("td");
        const statusBadge = document.createElement("span");

        const statusClass = {
            "Pending": "status-pending",
            "In Progress": "status-progress",
            "Resolved": "status-resolved"
        };

        statusBadge.className =
            "status-badge " + (statusClass[complaint.status] || "status-pending");

        statusBadge.textContent = complaint.status;
        statusCell.appendChild(statusBadge);
        row.appendChild(statusCell);

        const actionCell = document.createElement("td");
        const select = document.createElement("select");

        select.className = "status-select";
        select.setAttribute("aria-label", "Update status for " + complaint.id);

        ["Pending", "In Progress", "Resolved"].forEach(status => {
            const option = document.createElement("option");
            option.value = status;
            option.textContent = status;
            option.selected = complaint.status === status;
            select.appendChild(option);
        });

        select.addEventListener("change", async function () {
            const previousStatus = complaint.status;
            const chosenStatus = select.value;
            select.disabled = true;

            try {
                tableMessage.textContent = "Updating " + complaint.id + "...";
                const response = await fetch("/api/complaints/" + encodeURIComponent(complaint.id) + "/status", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        status: chosenStatus,
                        remarks: "Status updated by admin via dashboard"
                    })
                });

                const res = await response.json();
                if (!response.ok || !res.success) {
                    throw new Error(res.message || "Failed to update status.");
                }

                complaint.status = chosenStatus;
                updateStatistics();
                renderComplaints();

                tableMessage.style.color = "#166534";
                tableMessage.textContent = "✓ " + complaint.id + " status successfully updated to " + chosenStatus;
            } catch (err) {
                select.value = previousStatus;
                tableMessage.style.color = "#b91c1c";
                tableMessage.textContent = "Update error: " + err.message;
            } finally {
                select.disabled = false;
            }
        });

        actionCell.appendChild(select);
        row.appendChild(actionCell);
        tableBody.appendChild(row);
    });

    if (filtered.length === 0) {
        tableMessage.textContent = complaints.length === 0 
            ? "No complaints registered in the database yet." 
            : "No matching complaints found.";
    }
}

searchInput.addEventListener("input", function () {
    tableMessage.textContent = "";
    renderComplaints();
});

statusFilter.addEventListener("change", function () {
    tableMessage.textContent = "";
    renderComplaints();
});

// Initial load from live backend
fetchLiveComplaints();
