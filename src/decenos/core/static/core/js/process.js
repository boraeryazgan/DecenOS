// Function to get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Function to get CSRF token for AJAX requests
function getCSRFToken() {
  return getCookie("csrftoken");
}

function createProcess() {
  const modal = new bootstrap.Modal(
    document.getElementById("createProcessModal")
  );
  modal.show();
}

function submitProcess() {
  const name = document.getElementById("processName").value;
  const processType = document.getElementById("processType").value;
  const memoryRequired = document.getElementById("memoryRequired").value;

  fetch("/process/api/process/create/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({
      name: name,
      process_type: processType,
      memory_required: memoryRequired,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((data) => {
          throw new Error(data.message || "Failed to create process");
        });
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        bootstrap.Modal.getInstance(
          document.getElementById("createProcessModal")
        ).hide();
        refreshProcesses();
        alert(data.message || "Process created successfully");
      } else {
        throw new Error(data.message || "Failed to create process");
      }
    })
    .catch((error) => {
      console.error("Error creating process:", error);
      alert(error.message || "Failed to create process. Please try again.");
    });
}

function terminateProcess(pid) {
  fetch(`/process/api/process/${pid}/terminate/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((data) => {
          throw new Error(data.message || "Failed to terminate process");
        });
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        document.querySelector(`[data-pid="${pid}"]`).remove();
        alert(data.message || "Process terminated successfully");
      } else {
        throw new Error(data.message || "Failed to terminate process");
      }
    })
    .catch((error) => {
      console.error("Error terminating process:", error);
      alert(error.message || "Failed to terminate process. Please try again.");
    });
}

function refreshProcesses() {
  fetch("/process/api/processes/")
    .then((response) => response.json())
    .then((data) => {
      const processList = document.getElementById("process-list");
      processList.innerHTML = data.processes
        .map(
          (process) => `
                        <div class="process-item" data-pid="${process.pid}">
                            <div class="process-header">
                                <span class="process-name">${process.name}</span>
                                <span class="process-type badge bg-secondary">${process.process_type}</span>
                            </div>
                            <div class="process-details">
                                <div>PID: ${process.pid}</div>
                                <div>Owner: ${process.owner.username}</div>
                                <div>State: <span class="process-state">${process.state}</span></div>
                                <div>Memory: ${process.memory_required}MB</div>
                            </div>
                            <div class="process-actions">
                                <button class="console-button" onclick="terminateProcess(${process.pid})">Terminate</button>
                            </div>
                        </div>
                    `
        )
        .join("");
    });
}

// Auto-refresh system status
function refreshSystemStatus() {
  fetch("/process/api/system/status/")
    .then((response) => response.json())
    .then((data) => {
      // Update memory usage
      const memoryBar = document.querySelector(
        ".metric:nth-child(1) .progress-bar"
      );
      memoryBar.style.width = `${data.memory_usage}%`;
      memoryBar.textContent = `${data.memory_usage}%`;

      // Update process count
      document.querySelector(".metric:nth-child(2) .metric-value").textContent =
        data.process_count;

      // Update ready queue size
      document.querySelector(".metric:nth-child(3) .metric-value").textContent =
        data.ready_queue_size;

      // Update current process
      document.querySelector(".metric:nth-child(4) .metric-value").textContent =
        data.current_process || "None";

      // Update file system status
      const fileSystemStatus = document.querySelector(
        ".metric:nth-child(5) .metric-value"
      );
      fileSystemStatus.innerHTML = `
                Files: ${data.file_system_status.total_files}<br>
                Directories: ${data.file_system_status.total_directories}
            `;
    });
}

// Refresh system status every 5 seconds
setInterval(refreshSystemStatus, 5000);



async function fetchTamagotchi() {
  const res = await fetch('/api/processes/status/');
  const data = await res.json();
  data.forEach(p => {
    const el = document.querySelector(`[data-pid="${p.pid}"] .tamagotchi-status`);
    if (el) {
      el.innerHTML = `
        <div>😊 Happiness: ${p.happiness}%</div>
        <div>🍖 Hunger: ${p.hunger}%</div>
        ${!p.alive ? '<div class="badge bg-danger">💀 Dead</div>' : ''}
      `;
    }
  });
}

fetchTamagotchi();
setInterval(fetchTamagotchi, 10000);