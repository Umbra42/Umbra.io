export function init(uploadNavBtn, closeModal, uploadModal, fileInput, overallProgressDiv) {
  // open modal
  if (uploadNavBtn) {
    uploadNavBtn.addEventListener('click', () => {
      console.log('Nav Upload button clicked');
      uploadModal.classList.add('active');
    });
  } else {
    console.warn('Upload button not found');
  }

  // selective rendering
  if (fileInput) {
    fileInput.addEventListener('change', () => {
      const fileCount = fileInput.files.length;
      if (fileCount > 1) {
        overallProgressDiv.style.display = 'flex';
      } else {
        overallProgressDiv.style.display = 'none';
      }
    });
  } else {
    console.warn('File input not found');
  }

  // close modal
  if (closeModal) {
      closeModal.addEventListener('click', () => {
      console.log('Close button clicked');
      uploadModal.classList.remove('active');
  });
  } else {
      console.warn('Close button not found');
  }
}