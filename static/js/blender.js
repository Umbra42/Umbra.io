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
/*
 depricated
export async function ensureBlender() {
    const response = await fetch("/blender/start", { method: "POST" });
    const { status , message } = await response.json();
    console.log("Blender Start Status:", status, "\n", "Message:", message);
}

export async function stopBlender() {
    const response = await fetch("/blender/stop", { method: "POST" });
    const { status , message } = await response.json();
    console.log("Blender Stop Status:", status, "\n", "Message:", message);
}

document.addEventListener("DOMContentLoaded", () => {
    ensureBlender();
  });
*/