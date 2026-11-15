
/* ========================================
   MOBILE NAVIGATION
======================================== */

const menuToggle = document.getElementById("menuToggle");
const navLinks = document.getElementById("navLinks");

menuToggle.addEventListener("click", () => {
    navLinks.classList.toggle("show");
});

document.querySelectorAll(".nav-links a").forEach(link => {
    link.addEventListener("click", () => {
        navLinks.classList.remove("show");
    });
});


/* ========================================
   TYPING ANIMATION
======================================== */

const words = [
    "AI & Data Science Developer",
    "Machine Learning Enthusiast",
    "Problem Solver",
    "Software Developer"
];

const typingText = document.getElementById("typing-text");

let wordIndex = 0;
let charIndex = words[0].length;
let deleting = true;

function typeEffect() {

    const currentWord = words[wordIndex];

    if (deleting) {

        charIndex--;

        typingText.textContent =
            currentWord.substring(0, charIndex);

        if (charIndex === 0) {

            deleting = false;

            wordIndex = (wordIndex + 1) % words.length;

            setTimeout(typeEffect, 400);
            return;
        }

    } else {

        const nextWord = words[wordIndex];

        charIndex++;

        typingText.textContent =
            nextWord.substring(0, charIndex);

        if (charIndex === nextWord.length) {

            deleting = true;

            setTimeout(typeEffect, 1800);
            return;
        }
    }

    setTimeout(typeEffect, deleting ? 45 : 75);
}

setTimeout(typeEffect, 1800);
