const complaints = [
    {
        id: "CMP-000101",
        title: "Projector not working",
        category: "Classroom Equipment",
        location: "Room 204",
        priority: "High",
        status: "Pending"
    },
    {
        id: "CMP-000102",
        title: "Wi-Fi connection issue",
        category: "Wi-Fi / Internet",
        location: "Library",
        priority: "Medium",
        status: "In Progress"
    },
    {
        id: "CMP-000103",
        title: "Water leakage",
        category: "Plumbing",
        location: "Hostel Block A",
        priority: "High",
        status: "Pending"
    },
    {
        id: "CMP-000104",
        title: "Classroom cleaning",
        category: "Cleanliness",
        location: "Block B",
        priority: "Low",
        status: "Resolved"
    },
    {
        id: "CMP-000105",
        title: "Broken ceiling fan",
        category: "Electrical",
        location: "Room 108",
        priority: "Medium",
        status: "In Progress"
    }
];

const tableBody = document.getElementById("complaintsTableBody");
const searchInput = document.getElementById("searchComplaints");
const statusFilter = document.getElementById("statusFilter");
const tableMessage = document.getElementById("tableMessage");

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
    cell.textContent = value;
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
            complaint.location
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

        priorityBadge.className =
            "priority-badge priority-" + complaint.priority.toLowerCase();

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
            "status-badge " + statusClass[complaint.status];

        statusBadge.textContent = complaint.status;
        statusCell.appendChild(statusBadge);
        row.appendChild(statusCell);

        const actionCell = document.createElement("td");
        const select = document.createElement("select");

        select.className = "status-select";
        select.setAttribute("aria-label",
            "Update status for " + complaint.id);

        ["Pending", "In Progress", "Resolved"].forEach(status => {
            const option = document.createElement("option");
            option.value = status;
            option.textContent = status;
            option.selected = complaint.status === status;
            select.appendChild(option);
        });

        select.addEventListener("change", function () {
            complaint.status = select.value;
            updateStatistics();
            renderComplaints();

            tableMessage.textContent =
                complaint.id + " updated to " + complaint.status +
                " (demo only — not saved).";
        });

        actionCell.appendChild(select);
        row.appendChild(actionCell);
        tableBody.appendChild(row);
    });

    if (filtered.length === 0) {
        tableMessage.textContent = "No matching complaints found.";
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

updateStatistics();
renderComplaints();
