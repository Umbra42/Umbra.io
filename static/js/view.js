let scene, camera, renderer, model;

function init() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 5;

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('viewer').appendChild(renderer.domElement);

    const light = new THREE.AmbientLight(0x404040);
    scene.add(light);
}

function loadModel() {
    const modelName = document.getElementById("model-name").value;
    if (!modelName) {
        alert("Please enter a model filename!");
        return;
    }
    
    const modelUrl = `/3D_objects/${modelName}`;
    const loader = new THREE.GLTFLoader();

    loader.load(modelUrl, (gltf) => {
        if (model) scene.remove(model);
        model = gltf.scene;
        scene.add(model);
    }, undefined, (error) => {
        console.error("Error loading model:", error);
    });
}

function animate() {
    requestAnimationFrame(animate);
    if (model) model.rotation.y += 0.01;
    renderer.render(scene, camera);
}
animate();