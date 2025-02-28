export function init(openCanvasBtn, mapCanvas, closeCanvasBtn) {
  // Open map offcanvas
  if (openCanvasBtn) {
    openCanvasBtn.addEventListener('click', () => {
      mapCanvas.classList.add('active');
    });
  } else {
    console.warn('Open canvas button not found');
  }

  // Close map offcanvas
  if (closeCanvasBtn) {
        closeCanvasBtn.addEventListener('click', () => {
            mapCanvas.classList.remove('active');
        });
    }
}