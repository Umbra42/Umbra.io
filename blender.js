let scene, camera, renderer, loader, model;
init();     
animate();      

function init() {         
    // Set up the scene         
    scene = new THREE.Scene();

    // Set up the camera         
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 5;
    
    // Set up the renderer         
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);          
    
    // Add lighting         
    const ambientLight = new THREE.AmbientLight(0xcccccc, 0.4);
    scene.add(ambientLight);
    const pointLight = new THREE.PointLight(0xffffff, 0.8);
    camera.add(pointLight);
    scene.add(camera);          
    
    // Load the GLTF model         
    loader = new THREE.GLTFLoader();
    loader.load('path_to_your_model.gltf', function (gltf) {
        model = gltf.scene;
        scene.add(model);
    });          
    
    // Handle window resize        
    window.addEventListener('resize', onWindowResize, false);
}      


function animate() {         
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
    if (model) model.rotation.y += 0.005;  
    }

    // Rotate the model for demonstration          
    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
        } 