const form = document.getElementById("issue-form");
const formMessage = document.getElementById("form-message");
const filterStatus = document.getElementById("filter-status");
const filterCategory = document.getElementById("filter-category");
const sortBy = document.getElementById("sort-by");
const cardTemplate = document.getElementById("card-template");

const lists = {
  "Open": document.getElementById("list-open"),
  "In Progress": document.getElementById("list-inprogress"),
  "Fixed": document.getElementById("list-fixed"),
};
const counts = {
  "Open": document.getElementById("count-open"),
  "In Progress": document.getElementById("count-inprogress"),
  "Fixed": document.getElementById("count-fixed"),
};

function timeAgo(isoString) {
  const then = new Date(isoString + "Z");
  const diffMs = Date.now() - then.getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

async function fetchIssues() {
  const params = new URLSearchParams({
    status: filterStatus.value,
    category: filterCategory.value,
    sort: sortBy.value,
  });
  const res = await fetch(`/api/issues?${params.toString()}`);
  const issues = await res.json();
  renderBoard(issues);
}

function renderBoard(issues) {
  Object.values(lists).forEach(el => (el.innerHTML = ""));
  const groupCounts = { "Open": 0, "In Progress": 0, "Fixed": 0 };

  issues.forEach(issue => {
    groupCounts[issue.status] = (groupCounts[issue.status] || 0) + 1;
    const node = cardTemplate.content.cloneNode(true);

    node.querySelector(".category-chip").textContent = issue.category;
    node.querySelector(".issue-title").textContent = issue.title;
    node.querySelector(".issue-location").textContent = `📍 ${issue.location}`;
    const descEl = node.querySelector(".issue-description");
    if (issue.description) {
      descEl.textContent = issue.description;
    } else {
      descEl.remove();
    }
    node.querySelector(".issue-time").textContent = timeAgo(issue.created_at);
    node.querySelector(".upvote-count").textContent = issue.upvotes;

    const statusSelect = node.querySelector(".status-select");
    statusSelect.value = issue.status;
    statusSelect.addEventListener("change", async (e) => {
      await updateStatus(issue.id, e.target.value);
      fetchIssues();
    });

    const upvoteBtn = node.querySelector(".upvote-btn");
    upvoteBtn.addEventListener("click", async () => {
      await upvoteIssue(issue.id);
      fetchIssues();
    });

    const targetList = lists[issue.status] || lists["Open"];
    targetList.appendChild(node);
  });

  Object.keys(counts).forEach(status => {
    counts[status].textContent = groupCounts[status] || 0;
    if (!groupCounts[status]) {
      const hint = document.createElement("div");
      hint.className = "empty-hint";
      hint.textContent = "No issues here";
      lists[status].appendChild(hint);
    }
  });
}

async function updateStatus(id, status) {
  await fetch(`/api/issues/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
}

async function upvoteIssue(id) {
  await fetch(`/api/issues/${id}/upvote`, { method: "POST" });
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  formMessage.textContent = "";
  formMessage.className = "form-message";

  const payload = {
    title: document.getElementById("title").value.trim(),
    category: document.getElementById("category").value,
    location: document.getElementById("location").value.trim(),
    description: document.getElementById("description").value.trim(),
  };

  const res = await fetch("/api/issues", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (res.ok) {
    form.reset();
    formMessage.textContent = "Reported! Thanks.";
    formMessage.classList.add("success");
    fetchIssues();
  } else {
    const err = await res.json();
    formMessage.textContent = err.error || "Something went wrong.";
    formMessage.classList.add("error");
  }
});

filterStatus.addEventListener("change", fetchIssues);
filterCategory.addEventListener("change", fetchIssues);
sortBy.addEventListener("change", fetchIssues);

fetchIssues();
setInterval(fetchIssues, 15000);
