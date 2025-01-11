document.getElementById('uploadBtn').addEventListener('click', function() {
    const uploadForm = document.getElementById('uploadForm');
    const formData = new FormData(uploadForm);

    console.log("Preparing files for upload...");
    fetch('/files/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        const taskId = data.task_id;
        console.log("Started upload with task ID:", taskId);
        sessionStorage.setItem('task_id', taskId);
        const modal = new bootstrap.Modal(document.getElementById('uploadModal'));
        modal.show();
        updateProgress(taskId);
    })
    .catch(error => {
        console.error("Upload failed:", error);
        const errorMsg = document.getElementById('errorMsg');
        errorMsg.innerText = `Upload failed: ${error.message || 'Unknown error'}`;
        errorMsg.style.display = 'block';
        resetModal();
    });
});


   

function updateProgress(taskId) {
    fetch(`/upload-progress/${taskId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const overallProgress = (data.current / data.total) * 100;
            updateProgressBar(overallProgress);

            if (data.status) {
                document.getElementById('currentTask').innerText = `Current Task: ${data.status}`;
            }

            if (data.blenderInstallation && data.blenderInstallation.required) {
                const blenderSection = document.getElementById('blenderInstallationSection');
                blenderSection.style.display = 'block';
                const blenderProgress = document.getElementById('blenderProgress');
                blenderProgress.style.width = `${data.blenderInstallation.progress}%`;
                blenderProgress.innerText = `${data.blenderInstallation.progress}%`;
            }

            if (data.current >= data.total) {
                document.getElementById('successMsg').innerText = "Upload and processing complete!";
                document.getElementById('successMsg').style.display = 'block';
                resetModal();
            } else {
                setTimeout(() => updateProgress(taskId), 1000);
            }
        })
        .catch(error => {
            console.error("Error fetching progress data:", error);
            const errorMsg = document.getElementById('errorMsg');
            errorMsg.innerText = "Unable to fetch progress updates. Please try again later.";
            errorMsg.style.display = 'block';
            resetModal();
        });
}
