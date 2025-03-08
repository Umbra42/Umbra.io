const socket = io();

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