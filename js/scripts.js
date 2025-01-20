const socket = io.connect('http://localhost:5000');

document.addEventListener('DOMContentLoaded', () => {
  const navTogglerBtn = document.getElementById('navTogglerBtn');
  const uploadNavBtn = document.getElementById('uploadNavBtn');

  const uploadModalBtn = document.getElementById('uploadModalBtn');
  const fileInput = document.getElementById('fileInput');
  const overallProgress = document.getElementById('overallProgress');
  const progressContainer = document.getElementById('progressContainer');
  const uploadForm = document.getElementById('uploadForm');

  const openCanvasBtn = document.getElementById('openCanvasBtn');
  const fileCanvas = document.getElementById('fileCanvas');
  const closeCanvasBtn = document.getElementById('closeCanvasBtn');
  
  
  // togggle navbar small screens
  navTogglerBtn.addEventListener('click', () => {
    const navbar = document.getElementById('navbar');
    navbar.classList.toggle('active');
  });

  // open modal
  uploadNavBtn.addEventListener('click', () => {
    console.log('Nav Upload button clicked');
    uploadModal.classList.add('active');
  });
  // close modal
  closeModal.addEventListener('click', () => {
    console.log('Close button clicked');
    uploadModal.classList.remove('active');
  });

  //#TODO:
  // if more than one files are uploaded the overall progress bar should appear.
  // the dail should display the current progress of the file being uploaded
  uploadModalBtn.addEventListener('click', () => {
    if (!fileInput.files.length) {
        alert('Please select a file');
        return;
    }

    const file = fileInput.files[0];
    socket.emit('start_upload', { filename: file.name, size: file.size });

    const chunkSize = 1024 * 64;  // 64KB chunks
    let offset = 0;
    let task_id = null;

    function checkProgress() {
        fetch(`/progress/${task_id}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('uploadProgress').value = data.progress;
                console.log(`Upload Progress: ${data.progress}%`);

                if (data.progress >= 100) {
                    clearInterval(progressInterval);
                    alert('Upload completed successfully!');
                }
            })
            .catch(error => console.error('Progress check failed', error));
    }

    function sendChunk() {
        if (offset < file.size) {
            const chunk = file.slice(offset, offset + chunkSize);
            const reader = new FileReader();

            reader.onload = (e) => {
                socket.emit('upload_chunk', {
                    filename: file.name,
                    chunk: e.target.result
                });

                offset += chunkSize;
                sendChunk();
            };

            reader.readAsArrayBuffer(chunk);
        } else {
            socket.emit('upload_complete', { filename: file.name });

            // Start progress polling every 2 seconds
            progressInterval = setInterval(checkProgress, 2000);
        }
    }

    socket.on('upload_started', (data) => {
        task_id = data.task_id;
        console.log(`Upload started with task ID: ${task_id}`);
        sendChunk();
    });

    socket.on('upload_error', (data) => {
        console.error('Upload error:', data);
    });
  });

  // Handle upload completion
  socket.on('upload_done', (data) => {
    alert(`Upload completed: ${data.filename}`);
  });

  socket.on('upload_cancelled', (data) => {
    alert(`Upload cancelled: ${data.filename}`);
  });




  // tab swithcing logic
  document.querySelectorAll('.tab-btn').forEach(button => {
    button.addEventListener('click', () => {
        console.log('Clicked:', button);
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
            console.log('Hiding panel:', panel.id);
        });
        const tabPanelId = button.getAttribute('data-tab');
        const tabPanel = document.getElementById(tabPanelId);
        if (tabPanel) {
          tabPanel.classList.add('active');
          console.log('Showing panel:', tabPanelId);
        } else {
          console.error(`Tab panel with id "${tabPanelId}" not found.`);
        }
    });
  });

  // Open map offcanvas
  openCanvasBtn.addEventListener('click', () => {
    fileCanvas.classList.add('active');
  });
  // Close map offcanvas
  closeCanvasBtn.addEventListener('click', () => {
    fileCanvas.classList.remove('active');
  });
});


