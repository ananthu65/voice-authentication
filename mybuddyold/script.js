const robot = document.getElementById('ai-robot');
const robotContainer = document.querySelector('.robot-container');

function setEmotion(emotion) {
    // Change the robot's class to apply emotion-specific styles and gestures
    robot.className = `robot ${emotion}`;

    // Temporarily disable the main container's animation to allow
    // emotion-specific animations (like the surprise jump) to play cleanly.
    robotContainer.style.animation = 'none';
    // This is a trick to force the browser to restart the animation flow
    void robotContainer.offsetWidth; 
    
    // Re-apply the default idle animations
    robotContainer.style.animation = '';
}

// Set the default emotion to 'happy' when the page loads so he waves at you!
document.addEventListener('DOMContentLoaded', () => {
    setEmotion('happy');
});