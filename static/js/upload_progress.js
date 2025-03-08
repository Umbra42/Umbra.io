export function init(socket, state, status, consoleOutput, totalProgressDail, uploadProgressBar, progressText) {
  if (!socket) {
    console.error('Socket not found in upload_progress.js');
    return;
  }

  socket.on('progress_update', (data) => {
    console.log('progress_update:', data);
    
    if (!data || typeof data !== 'object') {
      console.error('Invalid overall progress data');
      return;
    }

    // 25 place holder value
    let percentage = Math.round(data.step_n / 25)* 100;

    if (uploadProgressBar) {
      uploadProgressBar.style.transition = 'width 0.3s ease-in-out';
      uploadProgressBar.value = percentage;
    }

    if (progressText) {
      progressText.innerText = `${percentage}%`;
    }

    if (state) {
      state.innerText = data.state;
    }

    if (status) {
      status.innerText = data.status;
    }

    if (consoleOutput) {
      const newLog = document.createElement('div');
      newLog.innerText = `[${new Date().toLocaleTimeString()}] ${data.status}`;
      consoleOutput.appendChild(newLog)
      
      while (consoleOutput.children.length > 60 ) {
        consoleOutput.removeChild(consoleOutput.firstChild);
      }

      const isScrolledToBottom = consoleOutput.scrollHeight - consoleOutput.clientHeight <= consoleOutput.scrollTop + 6;
      if(isScrolledToBottom) {
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
      }
      consoleOutput.scrollTo({
        top: consoleOutput.scrollHeight,
        behavior: 'smooth'
      });
    }

    if (data.total > 1 && totalProgressDail) {
      let totalPercentage = Math.round(((data.current_n +1)/ data.total) * 100);
      totalProgressDail.innerText = `${totalPercentage}%`;
      totalProgressDail.style.width = `${totalPercentage}%`;
      totalProgressDail.setAttribute('aria-valuenow', totalPercentage);
    }

    if (data.state === "Completed") {
      console.log('Upload completed');
      consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }

    if (data.state === "ERROR") {
      state.style.color = 'red !important';
      console.log(`Error: ${data.status}`);
      consoleOutput.innerHTML += `\n[${new Date().toLocaleTimeString()}] ❌ Error: ${data.status}`;
    }
  });
}
