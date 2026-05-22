/**
 * ASL Performance App - Main Application Logic
 */

let currentScene = 0;
const video = document.getElementById('asl-video');
const placeholder = document.getElementById('video-placeholder');
const sceneTitle = document.getElementById('scene-title');
const sceneText = document.getElementById('scene-text');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const currentSceneLabel = document.getElementById('current-scene-label');
const totalScenesLabel = document.getElementById('total-scenes-label');
const sceneDots = document.getElementById('scene-dots');

/**
 * Initialize the app
 */
function initApp() {
    const totalScenes = storyData.scenes.length;
    totalScenesLabel.textContent = totalScenes;

    // Create scene dots
    sceneDots.innerHTML = '';
    for (let i = 0; i < totalScenes; i++) {
        const dot = document.createElement('div');
        dot.className = 'scene-dot' + (i === 0 ? ' active' : '');
        dot.setAttribute('role', 'button');
        dot.setAttribute('aria-label', `Go to scene ${i + 1}`);
        dot.addEventListener('click', () => goToScene(i));
        sceneDots.appendChild(dot);
    }

    loadScene(0);
}

/**
 * Start the app (transition from welcome to main screen)
 */
function startApp() {
    document.getElementById('welcome-screen').classList.remove('active');
    document.getElementById('app-screen').classList.add('active');
    initApp();
}

/**
 * Load a specific scene
 */
function loadScene(index) {
    const scene = storyData.scenes[index];
    if (!scene) return;

    currentScene = index;

    // Update text content
    sceneTitle.textContent = scene.title;
    sceneText.innerHTML = scene.text;

    // Update scene label
    currentSceneLabel.textContent = `Scene ${index + 1}`;

    // Update navigation buttons
    prevBtn.disabled = index === 0;
    nextBtn.disabled = index === storyData.scenes.length - 1;

    // Update dots
    document.querySelectorAll('.scene-dot').forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
    });

    // Load video
    loadVideo(scene.video);

    // Scroll to top of story
    document.querySelector('.story-section').scrollTop = 0;
}

/**
 * Load video for current scene
 */
function loadVideo(videoSrc) {
    if (videoSrc && videoSrc.trim() !== '') {
        // Check if it's a YouTube URL
        if (videoSrc.includes('youtube.com') || videoSrc.includes('youtu.be')) {
            // For YouTube, we'd need an iframe - for now show placeholder
            showPlaceholder('YouTube video - open in browser');
            return;
        }

        // Try to load the video file
        video.src = videoSrc;
        video.load();

        video.oncanplay = function () {
            video.classList.add('visible');
            placeholder.classList.add('hidden');
        };

        video.onerror = function () {
            showPlaceholder('Video not yet available');
        };
    } else {
        showPlaceholder('No video assigned');
    }
}

/**
 * Show video placeholder with message
 */
function showPlaceholder(message) {
    video.classList.remove('visible');
    video.pause();
    placeholder.classList.remove('hidden');
    placeholder.querySelector('.placeholder-sub').textContent = message;
}

/**
 * Navigate to next scene
 */
function nextScene() {
    if (currentScene < storyData.scenes.length - 1) {
        loadScene(currentScene + 1);
    }
}

/**
 * Navigate to previous scene
 */
function prevScene() {
    if (currentScene > 0) {
        loadScene(currentScene - 1);
    }
}

/**
 * Go to a specific scene by index
 */
function goToScene(index) {
    if (index >= 0 && index < storyData.scenes.length) {
        loadScene(index);
    }
}

// Keyboard navigation support
document.addEventListener('keydown', function (e) {
    if (document.getElementById('app-screen').classList.contains('active')) {
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
            e.preventDefault();
            nextScene();
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            e.preventDefault();
            prevScene();
        }
    }
});

// Swipe gesture support for mobile
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', function (e) {
    touchStartX = e.changedTouches[0].screenX;
}, { passive: true });

document.addEventListener('touchend', function (e) {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}, { passive: true });

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swiped left - next scene
            nextScene();
        } else {
            // Swiped right - previous scene
            prevScene();
        }
    }
}
