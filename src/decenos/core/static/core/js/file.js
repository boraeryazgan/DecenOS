function navigateTo(directoryId) {
  window.location.href = `/process/explorer/${directoryId}/`;
}

function openFile(fileId) {
  fetch(`/process/api/file/${fileId}/`)
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to fetch file content");
      }
      return response.json();
    })
    .then((data) => {
      console.log("File data received:", data); // Debug log

      // Get the modal elements
      const fileNameElement = document
        .getElementById("fileViewerModal")
        .querySelector("#fileName");
      const fileSizeElement = document
        .getElementById("fileViewerModal")
        .querySelector("#fileSize");
      const fileEncryptedElement = document
        .getElementById("fileViewerModal")
        .querySelector("#fileEncrypted");
      const fileContentElement = document
        .getElementById("fileViewerModal")
        .querySelector("#fileContent");

      // Update the modal content
      fileNameElement.textContent = data.name || "Unnamed File";
      fileSizeElement.textContent = data.size || 0;
      fileEncryptedElement.textContent = data.is_encrypted ? "Yes" : "No";
      fileContentElement.textContent = data.content || "No content available";

      // Show the modal
      const modal = new bootstrap.Modal(
        document.getElementById("fileViewerModal")
      );
      modal.show();
    })
    .catch((error) => {
      console.error("Error opening file:", error);
      alert("Failed to open file. Please try again.");
    });
}

function createFile() {
  const modal = new bootstrap.Modal(document.getElementById("createFileModal"));
  modal.show();
}

function submitFile() {
  const name = document.getElementById("fileName").value;
  const content = document.getElementById("fileContent").value;
  const isEncrypted = document.getElementById("isEncrypted").checked;
  const currentDirId =
    document.querySelector("[data-current-dir]")?.dataset.currentDir || null;

  fetch("/process/api/file/create/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({
      name: name,
      content: content,
      is_encrypted: isEncrypted,
      directory_id: currentDirId,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((data) => {
          throw new Error(data.message || "Failed to create file");
        });
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        bootstrap.Modal.getInstance(
          document.getElementById("createFileModal")
        ).hide();
        window.location.reload();
        alert(data.message || "File created successfully");
      } else {
        throw new Error(data.message || "Failed to create file");
      }
    })
    .catch((error) => {
      console.error("Error creating file:", error);
      alert(error.message || "Failed to create file. Please try again.");
    });
}

function createDirectory() {
  const modal = new bootstrap.Modal(
    document.getElementById("createDirectoryModal")
  );
  modal.show();
}

function submitDirectory() {
  const name = document.getElementById("directoryName").value;
  const currentDirId =
    document.querySelector("[data-current-dir]")?.dataset.currentDir || null;

  fetch("/process/api/directory/create/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({
      name: name,
      parent_id: currentDirId,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((data) => {
          throw new Error(data.message || "Failed to create directory");
        });
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        bootstrap.Modal.getInstance(
          document.getElementById("createDirectoryModal")
        ).hide();
        window.location.reload();
        alert(data.message || "Directory created successfully");
      } else {
        throw new Error(data.message || "Failed to create directory");
      }
    })
    .catch((error) => {
      console.error("Error creating directory:", error);
      alert(error.message || "Failed to create directory. Please try again.");
    });
}
