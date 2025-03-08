socket.emit("request_code");

socket.on("code_list", function(codeFiles) {
    const codeList = document.getElementById("code-list");
    codeList.innerHTML = "";
    codeFiles.forEach(file => {
        let button = document.createElement("button");
        button.innerText = file;
        button.onclick = () => fetchCode(file);
        codeList.appendChild(button);
    });
});

function fetchCode(fileName) {
    fetch(`/code/${fileName}`)
    .then(response => response.text())
    .then(code => {
        document.querySelector("#code-display code").textContent = code;
    })
    .catch(error => console.error("Error loading code:", error));
}