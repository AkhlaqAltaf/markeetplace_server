const backgrounds = [
    "../images/v84_120.png",
    "../images/v84_121.png",
    "../images/v84_122.png"
];

let currentIndex = 0;

function changeBackground(index) {
    document.getElementById('bg-container').style.backgroundImage = `url('${backgrounds[index]}')`;
    currentIndex = index;
    updatePagination();
}

function autoSlide() {
    currentIndex = (currentIndex + 1) % backgrounds.length;
    changeBackground(currentIndex);
}

function updatePagination() {
    let dots = document.querySelectorAll("#bg-container div div");
    dots.forEach((dot, idx) => {
        dot.classList.remove("bg-teal-700");
        dot.classList.add("bg-white");
        if (idx === currentIndex) {
            dot.classList.remove("bg-white");
            dot.classList.add("bg-teal-700");
        }
    });
}

setInterval(autoSlide, 5000);




function toggleAnswer(id) {
    let answer = document.getElementById(`answer-${id}`);
    let icon = answer.previousElementSibling.querySelector("span:last-child");

    if (answer.classList.contains("hidden")) {
        answer.classList.remove("hidden");
        icon.textContent = "-";
    } else {
        answer.classList.add("hidden");
        icon.textContent = "+";
    }
}



document.addEventListener("DOMContentLoaded", function () {
    const carouselWrapper = document.getElementById("carouselWrapper");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const cards = document.querySelectorAll(".testimonial-card");
    
    let currentIndex = 0;
    let visibleCards = getVisibleCards();
    let maxIndex = Math.max(0, cards.length - visibleCards);

    function getVisibleCards() {
        if (window.innerWidth >= 1024) return 3; // Desktop
        if (window.innerWidth >= 640) return 2;  // Tablet
        return 1; // Mobile
    }

    function updateCarousel() {
        const cardWidth = cards[0].getBoundingClientRect().width;
        carouselWrapper.style.transform = `translateX(-${currentIndex * cardWidth}px)`;
    }

    nextBtn.addEventListener("click", () => {
        if (currentIndex < maxIndex) {
            currentIndex++;
            updateCarousel();
        }
    });

    prevBtn.addEventListener("click", () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    });

    window.addEventListener("resize", () => {
        visibleCards = getVisibleCards();
        maxIndex = Math.max(0, cards.length - visibleCards);
        updateCarousel();
    });
});




document.addEventListener("DOMContentLoaded", function () {
    const carousel = document.getElementById("carousel");
    const prevBtn = document.getElementById("prev");
    const nextBtn = document.getElementById("next");

    let scrollStep = calculateScrollStep();

    function calculateScrollStep() {
        const visibleCards = getVisibleCards();
        return carousel.clientWidth / visibleCards;
    }

    function getVisibleCards() {
        if (window.innerWidth >= 1024) return 4; // 4 cards on desktop
        if (window.innerWidth >= 768) return 3;  // 3 cards on tablets
        return 2; // 2 cards on mobile
    }

    nextBtn.addEventListener("click", () => {
        carousel.scrollBy({ left: scrollStep, behavior: "smooth" });
    });

    prevBtn.addEventListener("click", () => {
        carousel.scrollBy({ left: -scrollStep, behavior: "smooth" });
    });

    window.addEventListener("resize", () => {
        scrollStep = calculateScrollStep();
    });
});





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