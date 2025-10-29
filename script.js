// -----------------------------
// CHAT-LOGIK
// -----------------------------
console.log("Canvas:", document.getElementById('three-canvas'));
document.getElementById('chat-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (!message) return;

    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML += `<p><strong>Du:</strong> ${message}</p>`;
    input.value = '';

    try {
        const res = await fetch('pages/chat_api.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'message=' + encodeURIComponent(message)
        });

        const data = await res.json();
        const reply = data.reply;

        chatBox.innerHTML += `<p><strong>KI:</strong> ${reply}</p>`;
        chatBox.scrollTop = chatBox.scrollHeight;

        // Sprachausgabe
        speakText(reply);
    } catch (error) {
        chatBox.innerHTML += `<p><strong>Fehler:</strong> ${error.message}</p>`;
    }
});

const container = document.getElementById('3d-face-container');
const canvas = document.getElementById('three-canvas');

if (container && canvas) {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
  45,
  400 / 400,  // oder 400 / 953 wenn dein Canvas so groß ist
  0.1,
  1000
);
const ambient = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambient);

camera.position.set(0, 0, 3);
camera.lookAt(0, 0, 0);
// -----------------------------
// THREE.JS chat_bot
// -----------------------------
	const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('three-canvas'), alpha: true });
renderer.setSize(400, 400); // Muss zur CSS-Größe passen


    renderer.setClearColor(0x000000, 0); // Transparent

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(0, 5, 5).normalize();
    scene.add(light);

    let model;

    const loader = new THREE.GLTFLoader();
loader.load('assets/models/chat_bot.glb', function (gltf) {
    model = gltf.scene;
    scene.add(model);
}, undefined, function (error) {
    console.error('Fehler beim Laden des Modells:', error);
});
    camera.position.z = 5;

    let speaking = false;

    function animate() {
        requestAnimationFrame(animate);

        if (model) {
            model.rotation.y += 0.005;
            if (speaking) {
                const scale = 1.5 + 0.05 * Math.sin(Date.now() * 0.02);
                model.scale.set(scale, scale, scale);
            }
        }

        renderer.render(scene, camera);
    }

    animate();

    // Start/Stop Lippenbewegung während Sprachausgabe
    function speakText(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.onstart = () => speaking = true;
            utterance.onend = () => speaking = false;
            speechSynthesis.speak(utterance);
        } else {
            console.warn('Sprachausgabe wird nicht unterstützt.');
        }
    }

    window.speakText = speakText; // global verfügbar machen
}
