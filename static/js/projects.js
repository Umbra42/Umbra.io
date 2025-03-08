socket.emit("request_projects"); // Request projects on load

socket.on("projects_list", function(files) {
    const projectList = document.getElementById("project-list");
    projectList.innerHTML = ""; // Clear previous list
    files.forEach(file => {
        let button = document.createElement("button");
        button.innerText = file;
        button.onclick = () => showProject(file);
        projectList.appendChild(button);
    });
});

function showProject(fileName) {
    const projectViewer = document.getElementById("project-viewer");
    projectViewer.innerHTML = "";

    const fileUrl = `/projects/${fileName}`;
    if (fileName.endsWith(".txt") || fileName.endsWith(".md")) {
        fetch(fileUrl).then(response => response.text()).then(text => {
            let pre = document.createElement("pre");
            pre.innerText = text;
            projectViewer.appendChild(pre);
        });
    } else if (fileName.endsWith(".jpg") || fileName.endsWith(".png")) {
        let img = document.createElement("img");
        img.src = fileUrl;
        projectViewer.appendChild(img);
    } else if (fileName.endsWith(".mp4")) {
        let video = document.createElement("video");
        video.src = fileUrl;
        video.controls = true;
        projectViewer.appendChild(video);
    }
}