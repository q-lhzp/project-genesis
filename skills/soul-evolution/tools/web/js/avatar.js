/**
 * Project Genesis Dashboard - VRM Avatar & Expression Logic (v5.7.0)
 */

// Import Three.js and VRM from CDN
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';

// State
let vrmModel = null;
let scene, camera, renderer;
let currentPose = 'idle';
let currentEmote = 'neutral';
let animationId = null;

let currentBlendShapes = {
  joy: 0, angry: 0, sad: 0, fear: 0, surprise: 0,
  neutral: 1, relaxed: 0, blinkLeft: 0, blinkRight: 0, blink: 0
};
let targetBlendShapes = { ...currentBlendShapes };
const LERP_SPEED = 0.05;
const DEFAULT_BLENDSHAPES = {
  joy: 0, angry: 0, sad: 0, fear: 0, surprise: 0,
  neutral: 1, relaxed: 0, blinkLeft: 0, blinkRight: 0, blink: 0
};

// Lights & Particles
let directionalLight = null;
let ambientLight = null;
let rainParticles = null;
let snowParticles = null;

let currentAtmosphere = {
  lightIntensity: 0.8, lightColor: '#ffffff',
  ambientIntensity: 0.6, ambientColor: '#ffffff',
  backgroundColor: '#1a1a2e',
  weather: 'clear', timeOfDay: 'afternoon'
};

let currentInteraction = {
  holding: [], lightIntensity: 0.8, lightColor: '#ffffff',
  furniture: '', prop: ''
};

// Audio / Lip-Sync
let audioContext = null;
let audioElement = null;
let analyserNode = null;
let audioSource = null;
let isPlayingAudio = false;
let lipSyncData = { vowel_a: 0, vowel_i: 0, vowel_u: 0, vowel_e: 0, vowel_o: 0 };
let targetLipSync = { ...lipSyncData };
const LIP_DECAY = 0.1;
const LIP_SENSITIVITY = 2.0;

// Motion
let currentMotion = { idle: 'neutral', breathingRate: 1.0, posture: 0.5, movementIntensity: 0.1, shakeAmplitude: 0, fidgetFrequency: 0 };
let targetMotion = { ...currentMotion };
let isWalking = false;
let walkingTimer = null;
const WALKING_DURATION = 4000;
let breathPhase = 0;

async function loadVRM(url) {
  const loader = new GLTFLoader();
  return new Promise((resolve, reject) => {
    loader.load(url, (gltf) => resolve(gltf.scene), (p) => console.log('Loading:', (p.loaded/p.total*100)+'%'), (e) => reject(e));
  });
}

async function initAvatar() {
  const canvas = document.getElementById('vrm-canvas');
  const loading = document.getElementById('avatar-loading');
  const error = document.getElementById('avatar-error');
  const statusText = document.getElementById('avatar-status-text');
  if (!canvas) return;

  try {
    const configRes = await fetch('/api/avatar/config');
    const config = await configRes.json();
    if (!config.vrm_path) throw new Error('No VRM path configured');

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);
    camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
    camera.position.set(0, 1.2, 3);
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    initAtmosphereLights();
    initWeatherParticles();

    const modelPath = config.vrm_path.replace('/home/leo/Schreibtisch', '');
    statusText.textContent = 'Loading 3D model...';
    vrmModel = await loadVRM(modelPath);
    vrmModel.scale.set(1, 1, 1);
    vrmModel.position.set(0, 0, 0);
    scene.add(vrmModel);

    loading.style.display = 'none';
    statusText.textContent = 'Avatar loaded successfully';
    animate();
    startAvatarPolling();

    // Load initial atmosphere
    try {
      const res = await fetch('/api/avatar/state');
      const state = await res.json();
      if (state.action === 'sync_atmosphere' && state.atmosphere) {
        handleAtmosphereUpdate(state.atmosphere);
      }
    } catch (e) {}

  } catch (err) {
    console.error('Avatar init error:', err);
    if (loading) loading.style.display = 'none';
    if (error) error.style.display = 'block';
    if (statusText) statusText.textContent = 'Error: ' + err.message;
  }
}

function animate() {
  animationId = requestAnimationFrame(animate);
  if (vrmModel) {
    const time = Date.now() * 0.001;
    vrmModel.position.y = Math.sin(time) * 0.02;
    updateBlendShapesLerp();
    updateLipSync();
    updateMotionLerp();
    animateWeatherParticles();
  }
  renderer.render(scene, camera);
}

function updateBlendShapesLerp() {
  let allSettled = true;
  for (const key of Object.keys(targetBlendShapes)) {
    const target = targetBlendShapes[key];
    const current = currentBlendShapes[key];
    if (Math.abs(target - current) > 0.001) {
      currentBlendShapes[key] = current + (target - current) * LERP_SPEED;
      allSettled = false;
    }
  }
  applyBlendShapesToVRM(currentBlendShapes);
  if (!allSettled) {
    const statusText = document.getElementById('avatar-status-text');
    if (statusText) statusText.textContent = `Expression: ${getDominantExpression(currentBlendShapes)}`;
  }
}

function applyBlendShapesToVRM(blendShapes) {
  if (!vrmModel) return;
  const joy = blendShapes.joy || 0, angry = blendShapes.angry || 0, sad = blendShapes.sad || 0, fear = blendShapes.fear || 0;
  let r = joy * 0.2 + angry * 0.8 + fear * 0.3, g = joy * 0.5, b = sad * 0.5 + fear * 0.3;
  const intensity = Math.max(joy, angry, sad, fear) * 0.4;
  vrmModel.traverse((child) => {
    if (child.isMesh && child.material) {
      const name = child.name.toLowerCase();
      if (name.includes('face') || name.includes('head')) {
        child.material.emissive = new THREE.Color(r, g, b);
        child.material.emissiveIntensity = intensity;
      }
    }
  });
}

function getDominantExpression(blendShapes) {
  const { joy, angry, sad, fear, surprise, relaxed, neutral } = blendShapes;
  const max = Math.max(joy, angry, sad, fear, surprise, relaxed, neutral);
  if (max === joy && joy > 0.1) return 'Joy';
  if (max === angry && angry > 0.1) return 'Angry';
  if (max === sad && sad > 0.1) return 'Sad';
  if (max === fear && fear > 0.1) return 'Fear';
  if (max === surprise && surprise > 0.1) return 'Surprise';
  if (max === relaxed && relaxed > 0.1) return 'Relaxed';
  return 'Neutral';
}

function startAvatarPolling() {
  setInterval(async () => {
    try {
      const res = await fetch('/api/avatar/state');
      const state = await res.json();
      if (!state.action) return;
      
      if (state.action === 'expression' && state.blendShapes) {
        targetBlendShapes = { ...DEFAULT_BLENDSHAPES, ...state.blendShapes };
        const bsContainer = document.getElementById('godmode-blendshapes');
        if (bsContainer) {
          bsContainer.innerHTML = Object.entries(state.blendShapes).sort((a,b)=>b[1]-a[1]).map(([k,v]) => `
            <div style="display:flex; justify-content:space-between; border-bottom:1px solid var(--border); padding:2px 0;">
              <span style="color:var(--text-dim);">${k}</span>
              <span style="color:${v > 0.5 ? 'var(--accent)' : 'var(--text)'}; font-weight:bold;">${v.toFixed(3)}</span>
            </div>
          `).join('');
        }
      }
      else if (state.action === 'voice' && state.audioUrl) handleVoicePlayback(state);
      else if (state.action === 'motion' || state.action === 'motion_walking') handleMotionUpdate(state);
      else if (state.action === 'sync_atmosphere' && state.atmosphere) handleAtmosphereUpdate(state.atmosphere);
      else if (state.interaction) handleInteractionUpdate(state.interaction);
      else if (state.action === 'pose' && state.value) applyPose(state.value);
      else if (state.action === 'emote' && state.value) applyEmote(state.value);
      else if (state.action === 'sync_wardrobe') syncWardrobe();
    } catch (e) { console.error('Polling error:', e); }
  }, 500);
}

function applyPose(pose) {
  if (!vrmModel) return;
  currentPose = pose;
  vrmModel.rotation.set(0, 0, 0);
  vrmModel.position.y = (pose === 'sitting') ? -0.3 : 0;
}

function applyEmote(emote) {
  if (!vrmModel) return;
  currentEmote = emote;
  vrmModel.traverse((child) => { if (child.isMesh && child.material) { child.material.emissiveIntensity = 0; } });
  const emoteColors = { 'joy': 0x00ff00, 'angry': 0xff0000, 'sad': 0x0000ff, 'neutral': 0x000000, 'relaxed': 0x00ffff };
  const color = emoteColors[emote];
  if (color) {
    vrmModel.traverse((child) => { if (child.isMesh && child.material) { child.material.emissive = new THREE.Color(color); child.material.emissiveIntensity = 0.3; } });
  }
}

async function syncWardrobe() {
  const container = document.getElementById('avatar-wardrobe');
  try {
    await fetch('/api/avatar/config');
    if (container) container.innerHTML = `<div class="panel-card" style="padding:0.5rem;"><div style="font-weight:bold;">Outfit Synced</div></div>`;
  } catch (e) { if (container) container.innerHTML = `Sync failed: ${e.message}`; }
}

function initAudioSystem() {
  if (audioContext) return;
  try {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 256;
    audioElement = new Audio();
    audioElement.crossOrigin = 'anonymous';
    audioSource = audioContext.createMediaElementSource(audioElement);
    audioSource.connect(analyserNode);
    analyserNode.connect(audioContext.destination);
    audioElement.addEventListener('ended', () => { isPlayingAudio = false; });
  } catch (e) { console.error('Audio init error:', e); }
}

async function playAudioWithLipSync(audioUrl) {
  if (!audioContext) initAudioSystem();
  if (!audioElement || !audioContext) return;
  try {
    if (audioContext.state === 'suspended') await audioContext.resume();
    audioElement.src = audioUrl;
    await audioElement.play();
    isPlayingAudio = true;
  } catch (e) { console.error('Play audio error:', e); }
}

function updateLipSync() {
  if (!isPlayingAudio || !analyserNode) {
    for (const key of Object.keys(lipSyncData)) lipSyncData[key] = Math.max(0, lipSyncData[key] - LIP_DECAY);
    applyLipSyncToVRM(lipSyncData);
    return;
  }
  const dataArray = new Uint8Array(analyserNode.frequencyBinCount);
  analyserNode.getByteFrequencyData(dataArray);
  const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
  const intensity = Math.min(1, (average / 128) * LIP_SENSITIVITY);
  const time = Date.now() * 0.01;
  targetLipSync.vowel_a = intensity * 0.8;
  targetLipSync.vowel_i = intensity * Math.abs(Math.sin(time * 1.5)) * 0.6;
  targetLipSync.vowel_u = intensity * Math.abs(Math.sin(time * 0.8)) * 0.5;
  for (const key of Object.keys(lipSyncData)) lipSyncData[key] += (targetLipSync[key] - lipSyncData[key]) * 0.3;
  applyLipSyncToVRM(lipSyncData);
}

function applyLipSyncToVRM(lipShapes) {
  if (!vrmModel) return;
  const mouthOpen = lipShapes.vowel_a, mouthWide = lipShapes.vowel_i + lipShapes.vowel_e, mouthRound = lipShapes.vowel_u + lipShapes.vowel_o;
  vrmModel.traverse((child) => {
    if (child.isMesh && child.material) {
      const name = child.name.toLowerCase();
      if (name.includes('face') || name.includes('head')) child.material.emissiveIntensity = 0.1 + mouthOpen * 0.15;
      if (name.includes('mouth') || name.includes('lip')) {
        child.material.emissive = new THREE.Color(mouthRound * 0.2, mouthWide * 0.1, mouthOpen * 0.1);
        child.material.emissiveIntensity = mouthOpen * 0.5;
      }
    }
  });
}

function handleVoicePlayback(state) {
  if (state.action === 'voice' && state.audioUrl) playAudioWithLipSync(state.audioUrl);
}

function applyMotionToVRM(motion) {
  if (!vrmModel) return;
  const time = Date.now() * 0.001;
  const { breathingRate, posture, movementIntensity, shakeAmplitude, fidgetFrequency } = motion;
  breathPhase += breathingRate * 0.03;
  const breathAmount = Math.sin(breathPhase) * 0.02 * breathingRate;
  vrmModel.traverse((child) => {
    if (!child.isMesh) return;
    const name = child.name.toLowerCase();
    if (name.includes('spine') || name.includes('chest')) {
      child.position.y = breathAmount;
      if (shakeAmplitude > 0) child.position.x += (Math.random() - 0.5) * shakeAmplitude * 0.01;
    }
    if (name.includes('head')) {
      child.position.y = (posture - 0.5) * 0.05;
      if (fidgetFrequency > 0) {
        child.position.x += Math.sin(time * 10) * fidgetFrequency * 0.01;
        child.rotation.z = Math.sin(time * 8) * fidgetFrequency * 0.05;
      }
    }
    if (movementIntensity > 0.1) child.rotation.y = Math.sin(time * 0.5) * movementIntensity * 0.02;
  });
}

function handleMotionUpdate(state) {
  if (state.motion && state.motion.isSleeping) {
    targetMotion = { idle: 'sleeping', breathingRate: 0.4, posture: 0.1, movementIntensity: 0, shakeAmplitude: 0, fidgetFrequency: 0, isSleeping: true };
    return;
  }
  if (state.motion) {
    const { isSleeping, ...m } = state.motion;
    targetMotion = { ...m, isSleeping: isSleeping || false };
  }
  if (state.isWalking || state.action === 'motion_walking') {
    isWalking = true;
    if (walkingTimer) clearTimeout(walkingTimer);
    targetMotion = { idle: 'walking', breathingRate: 1.5, posture: 0.8, movementIntensity: 0.8, shakeAmplitude: 0, fidgetFrequency: 0, isSleeping: false };
    walkingTimer = setTimeout(() => {
      isWalking = false;
      targetMotion = { idle: 'neutral', breathingRate: 1.0, posture: 0.5, movementIntensity: 0.1, shakeAmplitude: 0, fidgetFrequency: 0, isSleeping: false };
    }, WALKING_DURATION);
  }
}

function updateMotionLerp() {
  for (const key of Object.keys(targetMotion)) {
    const target = targetMotion[key], current = currentMotion[key];
    if (typeof target === 'number' && typeof current === 'number') {
      if (Math.abs(target - current) > 0.001) currentMotion[key] = current + (target - current) * 0.1;
    } else if (target !== current) currentMotion[key] = target;
  }
  applyMotionToVRM(currentMotion);
}

function initWeatherParticles() {
  if (!scene) return;
  const rainGeo = new THREE.BufferGeometry(), count = 1000, rainPos = new Float32Array(count * 3);
  for (let i = 0; i < count * 3; i += 3) { rainPos[i] = (Math.random()-0.5)*10; rainPos[i+1] = Math.random()*10; rainPos[i+2] = (Math.random()-0.5)*10; }
  rainGeo.setAttribute('position', new THREE.BufferAttribute(rainPos, 3));
  rainParticles = new THREE.Points(rainGeo, new THREE.PointsMaterial({ color: 0xaaaaaa, size: 0.02, transparent: true, opacity: 0.6 }));
  rainParticles.visible = false;
  scene.add(rainParticles);

  const snowGeo = new THREE.BufferGeometry(), snowPos = new Float32Array(count * 3);
  for (let i = 0; i < count * 3; i += 3) { snowPos[i] = (Math.random()-0.5)*10; snowPos[i+1] = Math.random()*10; snowPos[i+2] = (Math.random()-0.5)*10; }
  snowGeo.setAttribute('position', new THREE.BufferAttribute(snowPos, 3));
  snowParticles = new THREE.Points(snowGeo, new THREE.PointsMaterial({ color: 0xffffff, size: 0.04, transparent: true, opacity: 0.8 }));
  snowParticles.visible = false;
  scene.add(snowParticles);
}

function initAtmosphereLights() {
  if (!scene) return;
  directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(5, 5, 5);
  scene.add(directionalLight);
  ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);
}

function handleAtmosphereUpdate(atmosphere) {
  currentAtmosphere = { ...currentAtmosphere, ...atmosphere };
  if (directionalLight) { directionalLight.intensity = currentAtmosphere.lightIntensity; directionalLight.color.set(currentAtmosphere.lightColor); }
  if (ambientLight) { ambientLight.intensity = currentAtmosphere.ambientIntensity; ambientLight.color.set(currentAtmosphere.ambientColor); }
  if (scene) scene.background = new THREE.Color(currentAtmosphere.backgroundColor);
  updateWeatherParticles(currentAtmosphere.weather);
  updateAtmosphereUI(currentAtmosphere);
}

function handleInteractionUpdate(interaction) {
  currentInteraction = { ...currentInteraction, ...interaction };
  if (directionalLight) { directionalLight.intensity = currentInteraction.lightIntensity; directionalLight.color.set(currentInteraction.lightColor); }
  if (ambientLight) { ambientLight.intensity = currentInteraction.lightIntensity * 0.75; ambientLight.color.set(currentInteraction.lightColor); }
  if (scene) {
    const b = currentInteraction.lightIntensity;
    scene.background = new THREE.Color(Math.floor(0x1a*b), Math.floor(0x1a*b), Math.floor(0x2e*b));
  }
  updateInteractionUI(currentInteraction);
}

function updateInteractionUI(interaction) {
  const container = document.getElementById('interaction-status');
  if (!container) return;
  let html = '<div style="display:flex;flex-wrap:wrap;gap:0.5rem;align-items:center;">';
  if (interaction.holding?.length) html += `<span class="tag" style="background:var(--accent);">Holding: ${interaction.holding.join(', ')}</span>`;
  if (interaction.furniture) html += `<span class="tag" style="background:var(--primary);">At: ${interaction.furniture}</span>`;
  const l = interaction.lightIntensity;
  html += `<span class="tag" style="background:${l > 0.5 ? '#4ade80' : (l > 0 ? '#fbbf24' : '#6b7280')}">Light: ${l > 0.5 ? 'On' : (l > 0 ? 'Dim' : 'Off')}</span></div>`;
  container.innerHTML = html;
}

function updateWeatherParticles(weather) {
  if (!rainParticles || !snowParticles) return;
  rainParticles.visible = (weather === 'rainy' || weather === 'stormy');
  snowParticles.visible = (weather === 'snowy');
}

function animateWeatherParticles() {
  if (!scene) return;
  const time = Date.now() * 0.001;
  if (rainParticles?.visible) {
    const p = rainParticles.geometry.attributes.position.array;
    for (let i = 1; i < p.length; i += 3) { p[i] -= 0.1; if (p[i] < 0) p[i] = 10; }
    rainParticles.geometry.attributes.position.needsUpdate = true;
  }
  if (snowParticles?.visible) {
    const p = snowParticles.geometry.attributes.position.array;
    for (let i = 1; i < p.length; i += 3) { p[i] -= 0.02; p[i-1] += Math.sin(time+i)*0.002; if (p[i] < 0) p[i] = 10; }
    snowParticles.geometry.attributes.position.needsUpdate = true;
  }
}

function updateAtmosphereUI(atmosphere) {
  const el = document.getElementById('avatar-status-text');
  if (el) {
    const emojis = { 'clear': '☀️', 'cloudy': '☁️', 'rainy': '🌧️', 'stormy': '⛈️', 'snowy': '❄️', 'foggy': '🌫️', 'windy': '💨' };
    el.textContent = `${emojis[atmosphere.weather] || '🌤️'} ${atmosphere.timeOfDay} | ${atmosphere.weather}`;
  }
}

// Global Exports
window.initAvatar = initAvatar;
window.setAvatarPose = async (pose) => {
  try { await fetch('/api/avatar/update', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'pose', value: pose }) }); applyPose(pose); } catch (e) {}
};
window.setAvatarEmote = async (emote) => {
  try { await fetch('/api/avatar/update', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'emote', value: emote }) }); applyEmote(emote); } catch (e) {}
};
window.setLightState = async (action) => {
  try {
    const res = await fetch('/api/config/simulation', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'light', light_action: action }) });
    if (directionalLight) {
      const intensities = { on: 0.8, off: 0, dim: 0.3, bright: 1.0, toggle: currentInteraction.lightIntensity > 0 ? 0 : 0.8 };
      const intensity = intensities[action];
      directionalLight.intensity = intensity;
      if (ambientLight) ambientLight.intensity = intensity * 0.75;
      currentInteraction.lightIntensity = intensity;
    }
  } catch (e) {}
};
window.playAvatarVoice = playAudioWithLipSync;
window.syncAvatarWardrobe = syncWardrobe;

// Auto-init if tab active
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('tab-avatar')?.classList.contains('active')) initAvatar();
});
