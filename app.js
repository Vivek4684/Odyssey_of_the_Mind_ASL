/**
 * ASL Performance App - Main Application Logic
 */

/**
 * Start the app (transition from welcome to main screen)
 */
function startApp() {
    document.getElementById('welcome-screen').classList.remove('active');
    document.getElementById('app-screen').classList.add('active');
}
