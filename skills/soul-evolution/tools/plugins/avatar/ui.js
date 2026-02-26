/**
 * Avatar Plugin UI Module (v6.0.0)
 * Handles Three.js Rendering and VRM Embodiment.
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';

let vrmModel = null;
let scene, camera, renderer;
let animationId = null;
let currentPose = 'idle';
let currentEmote = 'neutral';

// State for smooth transitions
let currentBlendShapes = { joy: 0, angry: 0, sad: 0, fear: 0, surprise: 0, neutral: 1, relaxed: 0 };
let targetBlendShapes = { ...currentBlendShapes };
const LERP_SPEED = 0.05;

async function initAvatar() {
  const root = document.getElementById('plugin-root-avatar');
  if (!root) return;

  // 1. Build UI Structure
  root.innerHTML = `
    <div class="avatar-container">
      <div id="avatar-viewer" class="avatar-viewer">
        <canvas id="vrm-canvas-plugin"></canvas>
        <div id="avatar-overlay" class="avatar-overlay">Initializing Neural Interface...</div>
      </div>
      <div class="avatar-sidebar">
        <div class="panel-card">
          <h3>Expression</h3>
          <div class="control-grid">
            <button onclick="window.AvatarPlugin.setEmote('joy')">Joy</button>
            <button onclick="window.AvatarPlugin.setEmote('angry')">Angry</button>
            <button onclick="window.AvatarPlugin.setEmote('sad')">Sad</button>
            <button onclick="window.AvatarPlugin.setEmote('neutral')">Neutral</button>
          </div>
        </div>
        <div class="panel-card" style="margin-top:1rem;">
          <h3>Pose</h3>
          <div class="control-grid">
            <button onclick="window.AvatarPlugin.setPose('idle')">Idle</button>
            <button onclick="window.AvatarPlugin.setPose('sitting')">Sitting</button>
          </div>
        </div>
        <div id="avatar-status" style="margin-top:1rem; font-size:0.8rem; color:var(--text-dim);"></div>
      </div>
    </div>
  `;

  const canvas = document.getElementById('vrm-canvas-plugin');
  const overlay = document.getElementById('avatar-overlay');

  try {
    const configRes = await fetch('/api/plugins/avatar/config');
    const config = await configRes.json();
    const modelPath = config.vrm_path.replace('/home/leo/Schreibtisch', '');

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a12);
    
    camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
    camera.position.set(0, 1.2, 3);

    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(5, 5, 5);
    scene.add(dirLight);

    overlay.textContent = "Loading 3D Model...";
    const loader = new GLTFLoader();
    const gltf = await new Promise((res, rej) => loader.load(modelPath, res, null, rej));
    vrmModel = gltf.scene;
    scene.add(vrmModel);

    overlay.style.display = 'none';
    animate();
    startPolling();

  } catch (e) {
    overlay.textContent = "Neural Link Error: " + e.message;
    overlay.style.color = "var(--core)";
  }
}

function animate() {
  animationId = requestAnimationFrame(animate);
  if (vrmModel) {
    vrmModel.position.y = Math.sin(Date.now() * 0.001) * 0.02;
    updateBlendShapes();
  }
  renderer.render(scene, camera);
}

function updateBlendShapes() {
  for (const k of Object.keys(targetBlendShapes)) {
    if (Math.abs(targetBlendShapes[k] - currentBlendShapes[k]) > 0.001) {
      currentBlendShapes[k] += (targetBlendShapes[k] - currentBlendShapes[k]) * LERP_SPEED;
    }
  }
  applyToMesh(currentBlendShapes);
}

function applyToMesh(bs) {
  const r = bs.joy * 0.2 + bs.angry * 0.8, g = bs.joy * 0.5, b = bs.sad * 0.5;
  const intensity = Math.max(bs.joy, bs.angry, bs.sad) * 0.4;
  vrmModel.traverse(c => {
    if (childIsFace(c)) {
      c.material.emissive = new THREE.Color(r, g, b);
      c.material.emissiveIntensity = intensity;
    }
  });
}

const childIsFace = (c) => c.isMesh && c.material && (c.name.toLowerCase().includes('face') || c.name.toLowerCase().includes('head'));

function startPolling() {
  setInterval(async () => {
    try {
      const res = await fetch('/api/plugins/avatar/state');
      const state = await res.json();
      if (state.action === 'expression') targetBlendShapes = { ...currentBlendShapes, ...state.blendShapes };
      if (state.action === 'pose') applyPoseLocal(state.value);
    } catch(e) {}
  }, 1000);
}

function applyPoseLocal(pose) {
  if (!vrmModel) return;
  vrmModel.position.y = (pose === 'sitting') ? -0.3 : 0;
}

// Global API for the plugin
window.AvatarPlugin = {
  init: initAvatar,
  setEmote: (e) => fetch('/api/plugins/avatar/update', { method: 'POST', body: JSON.stringify({action: 'emote', value: e}) }),
  setPose: (p) => fetch('/api/plugins/avatar/update', { method: 'POST', body: JSON.stringify({action: 'pose', value: p}) })
};

// Start if tab is already active
if (document.getElementById('tab-avatar')) initAvatar();
