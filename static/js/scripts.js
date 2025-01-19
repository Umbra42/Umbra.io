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
  uploadModalBtn.addEventListener('click', async () => {
    const files = fileInput.files;

    if (!files.length) {
      alert('Please select a file to upload');
      return;
    }

    const formData = new FormData();
    Array.from(files).forEach(file => {
      formData.append('file', file);
    });
    
    try {
      const res = await fetch('/upload', {
          method: 'POST',
          body: formData,
        });
      
      if (res.ok) {
        let progress = 0;

        // Simulate progress for example purposes
        const interval = setInterval(() => {
          if (progress >= 100) {
            clearInterval(interval);
            progressText.textContent = 'Upload Complete!';
          } else {
            progress += 10;
            uploadProgress.value = progress;
            progressText.textContent = `${progress}%`;
          }
        }, 200);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Error during upload:', error);
      alert('An error occurred. Please try again.');
    }
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


