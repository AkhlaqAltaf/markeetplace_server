


const menuBtn = document.getElementById('menu-btn');
const closeMenuBtn = document.getElementById('close-menu');
const mobileMenu = document.getElementById('mobile-menu');

// Open menu
menuBtn.addEventListener('click', () => {
    mobileMenu.classList.remove('-translate-x-full');
});

// Close menu
closeMenuBtn.addEventListener('click', () => {
    mobileMenu.classList.add('-translate-x-full');
});

// Close menu when clicking outside
document.addEventListener('click', (event) => {
    if (!mobileMenu.contains(event.target) && !menuBtn.contains(event.target)) {
        mobileMenu.classList.add('-translate-x-full');
    }
});
