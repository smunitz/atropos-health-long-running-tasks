const tasksContainer = document.getElementById("tasksContainer");
const createTaskBtn = document.getElementById("createTaskBtn");
const filterContainer = document.getElementById("filterContainer");

let currentFilter = ""; // empty = no filter

// Create filter dropdown dynamically once first task is added
function maybeAddFilter() {
  if (!filterContainer.innerHTML) {
    const label = document.createElement("label");
    label.textContent = "Filter by status:";
    const select = document.createElement("select");
    select.id = "statusFilter";

    ["", "PENDING", "RUNNING", "SUCCESS", "FAILURE", "CANCELLED"].forEach(status => {
      const opt = document.createElement("option");
      opt.value = status;
      opt.textContent = status || "All";
      select.appendChild(opt);
    });

    select.addEventListener("change", () => {
      currentFilter = select.value;
      updateAllTasksVisibility();
    });

    filterContainer.appendChild(label);
    filterContainer.appendChild(select);
  }
  filterContainer.style.display = "block"; // show filter
}

// Show/hide tasks based on filter
function updateAllTasksVisibility() {
  const tasks = document.querySelectorAll(".task");
  tasks.forEach(div => {
    const status = div.dataset.status;
    div.style.display = !currentFilter || currentFilter === status ? "block" : "none";
  });

  // Hide filter if no tasks
  if (tasks.length === 0) filterContainer.style.display = "none";
}

// Create new task
createTaskBtn.addEventListener("click", async () => {
  const res = await fetch("/tasks", { method: "POST" });
  const data = await res.json();
  maybeAddFilter();
  addTaskToDOM(data.task_id);
});

// Add task to DOM
async function addTaskToDOM(taskId) {
  const div = document.createElement("div");
  div.className = "task";
  div.id = `task-${taskId}`;
  div.dataset.status = "PENDING";

  const infoDiv = document.createElement("div");
  infoDiv.className = "task-info";
  infoDiv.textContent = `Task ${taskId}: Pending...`;
  div.appendChild(infoDiv);

  const resultDiv = document.createElement("div");
  resultDiv.className = "task-result";
  div.appendChild(resultDiv);

  const cancelBtn = document.createElement("button");
  cancelBtn.textContent = "Cancel";
  cancelBtn.onclick = async () => {
    await fetch(`/tasks/${taskId}/status`, { method: "PATCH" });
    updateTaskStatus(taskId);
  };

  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "Delete";
  deleteBtn.onclick = async () => {
    await fetch(`/tasks/${taskId}`, { method: "DELETE" });
    div.remove();
    updateAllTasksVisibility(); // hide filter if no tasks
  };

  div.appendChild(cancelBtn);
  div.appendChild(deleteBtn);
  tasksContainer.appendChild(div);

  pollTaskStatus(taskId);
}

// Poll task status until finished
async function pollTaskStatus(taskId) {
  const div = document.getElementById(`task-${taskId}`);
  if (!div) return;

  const infoDiv = div.querySelector(".task-info");
  const resultDiv = div.querySelector(".task-result");
  const cancelBtn = div.querySelector("button");

  const res = await fetch(`/tasks/${taskId}/status`);
  const data = await res.json();

  div.dataset.status = data.status;
  infoDiv.textContent = `Task ${taskId}: ${data.status}`;

  updateAllTasksVisibility();

  if (data.status === "PENDING" || data.status === "RUNNING") {
    if (cancelBtn) cancelBtn.style.display = "inline";
    setTimeout(() => pollTaskStatus(taskId), 1000);
  } else {
    if (cancelBtn) cancelBtn.style.display = "none";

    const resultRes = await fetch(`/tasks/${taskId}/result`);
    const resultData = await resultRes.json();
    resultDiv.textContent = resultData.result || resultData.error || "";
  }
}

// Manual update after cancel
async function updateTaskStatus(taskId) {
  const div = document.getElementById(`task-${taskId}`);
  if (!div) return;

  const infoDiv = div.querySelector(".task-info");
  const cancelBtn = div.querySelector("button");

  const res = await fetch(`/tasks/${taskId}/status`);
  const data = await res.json();

  div.dataset.status = data.status;
  infoDiv.textContent = `Task ${taskId}: ${data.status}`;
  updateAllTasksVisibility();

  if (data.status !== "PENDING" && data.status !== "RUNNING") {
    if (cancelBtn) cancelBtn.style.display = "none";
  }
}