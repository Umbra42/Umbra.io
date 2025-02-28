export function init(fileInput, fileName, fileInputBtn, fileList, uploadModalBtn, uploadForm) {
    setTimeout(() => {
        if (!fileInput || !fileName || !fileInputBtn || !fileList || !uploadModal) {
            console.warn("One or more required elements are missing.");
            return;
        }
        
        fileInputBtn.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', () => {
            console.log("📂 fileList before appending items:", fileList.childNodes);
            fileList.innerHTML = "";
            console.log("📂 fileList before appending items:", fileList.childNodes);
            fileName.innerText = 'No file selected';
        
            if (fileInput.files.length === 1) {
                fileName.innerText = fileInput.files[0].name;
                console.log(`Selected file: ${fileInput.files[0].name}`);
                fileList.classList.add("file-hidden");
                console.log('list hidden')
            } else if (fileInput.files.length > 1) {
                fileName.innerText = `${fileInput.files.length} files selected`;
                fileList.classList.remove("file-hidden");
                console.log('list unhidden')

                for (let i = 0; i < fileInput.files.length; i++) {
                    console.log(`Selected file ${i+1}: ${fileInput.files[i].name}`);
                    let listItem = document.createElement('li');
                    listItem.innerText = fileInput.files[i].name;
                    console.log("✅ Created <li> element:", listItem);
                    fileList.appendChild(listItem);
                    console.log(`list item ${i} created as ${fileInput.files[i].name}`)
                    console.log("📃 Current fileList childNodes:", fileList.childNodes);
                }
                console.log("📃 Final File List Content:", fileList.innerHTML);
            } else {
                fileName.innerText = 'No file selected';
                fileList.classList.add("file-hidden");
                console.log('list hidden')
            }
            fileList.style.display = "none";
            requestAnimationFrame(() => {
                fileList.style.display = "block";
            });
        }, 50);
    });


    // Upload file
    //#TODO:
    // the dail should display the current progress of the file being uploaded
    if (uploadModalBtn && uploadForm) {
        uploadModalBtn.addEventListener('click', (event) => {
        
        if (!fileInput.files.length) {
            console.log('Please select a file');
            event.preventDefault();
            return;
        } 
        
        uploadModalBtn.disabled = true;

        const formData = new FormData(uploadForm);
        
        fetch('/upload/upload', {
            method: 'POST',
            body: formData
        })

        .then(response => response.json())
        .then(data => {
            if (data.state === 'Completed') {
                console.log(`Upload successful: ${data.task_id}`);
            } else {
                console.log(`Upload failed: ${data.status} || "Unknown error"`);
            }
        })

        .catch(error => {
            console.error('Upload failed:', error);
            console.log('Upload failed: Unknown error');
        })

        .finally(() => {
            uploadModalBtn.disabled = false;
            
        });
        });
    } else {
        console.warn('Upload button not found');
    }
}
