document.addEventListener('DOMContentLoaded', () => {
    const uploadNavBtn = document.getElementById('uploadNavBtn');
    const uploadModalBtn = document.getElementById('uploadModalBtn');
    const fileInput = document.getElementById('fileInput');
    const overallProgress = document.getElementById('overallProgress');
    const progressContainer = document.getElementById('progressContainer');
    const uploadForm = document.getElementById('uploadForm');
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
});
// if more than one files are uploaded the overall progress bar should appear.
// the dail should display the current progress of the file being uploaded

