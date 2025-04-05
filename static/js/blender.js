import {init as initSocket} from "./sockets.js";

export function init() {
    const socket = initSocket();

    socket.emit("request_models");

    socket.on("models_list", function(models) {
        const modelList = document.getElementById("model-list");
        modelList.innerHTML = "";
        models.forEach(model => {
            let button = document.createElement("button");
            button.innerText = model;
            button.onclick = () => loadModel(model);
            modelList.appendChild(button);
        });
    });

    function loadModel(modelName) {
        const modelUrl = `/models/${modelName}`;
        const loader = new THREE.GLTFLoader();
        loader.load(modelUrl, gltf => {
            scene.add(gltf.scene);
        }, undefined, error => console.error("Error loading model:", error));
    }
}

export function startCheckBlender() {
    fetch('/blender/check')
    .then(res => res.json())
    .then(data => {
        if (data.blender) {
            fetch("blender/start", { 
                method: "POST", 
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ task_id: data.task_id })
            });
    } else {
        alert("Blender not found. installing now...");
    }
});
}

export function stopBlender() {
    fetch("blender/stop", { method: "POST" });
}