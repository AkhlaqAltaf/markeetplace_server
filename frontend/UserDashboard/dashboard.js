document.addEventListener("DOMContentLoaded", function () {
  // Get all menu toggles
  const menuToggles = document.querySelectorAll(".menu-toggle");
  const dropdownMenus = document.querySelectorAll(".dropdown-menu");

  // Handle menu toggle clicks
  menuToggles.forEach((toggle) => {
    toggle.addEventListener("click", (e) => {
      e.stopPropagation();
      const cardMenu = toggle.closest(".card-menu");
      const dropdown = cardMenu.querySelector(".dropdown-menu");

      // Close all other dropdowns
      dropdownMenus.forEach((menu) => {
        if (menu !== dropdown) {
          menu.classList.add("hidden");
        }
      });

      // Toggle current dropdown
      dropdown.classList.toggle("hidden");
    });
  });

  // Close dropdowns when clicking outside
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".card-menu")) {
      dropdownMenus.forEach((menu) => {
        menu.classList.add("hidden");
      });
    }
  });

  // Handle copy icon clicks
  const copyIcons = document.querySelectorAll(".copy-icon");
  copyIcons.forEach((icon) => {
    icon.addEventListener("click", () => {
      const cardNumber = icon.previousElementSibling.textContent;
      navigator.clipboard
        .writeText(cardNumber)
        .then(() => {
          // Optional: Show a tooltip or notification that the number was copied
          alert("Card number copied to clipboard!");
        })
        .catch((err) => {
          console.error("Failed to copy text: ", err);
        });
    });
  });

  const hamburgerMenu = document.querySelector(".hamburger-menu");
  const sidebar = document.getElementById("sidebar");
  const mainContent = document.querySelector(".main-content");

  // Create overlay element
  const overlay = document.createElement("div");
  overlay.className = "sidebar-overlay";
  document.body.appendChild(overlay);

  // Toggle sidebar
  function toggleSidebar() {
    hamburgerMenu.classList.toggle("active");
    sidebar.classList.toggle("active");
    overlay.classList.toggle("active");
    document.body.style.overflow = sidebar.classList.contains("active")
      ? "hidden"
      : "";
  }

  // Event listeners
  hamburgerMenu.addEventListener("click", toggleSidebar);
  overlay.addEventListener("click", toggleSidebar);

  // Close sidebar when clicking a menu item on mobile
  const menuItems = document.querySelectorAll(".menu-item");
  menuItems.forEach((item) => {
    item.addEventListener("click", () => {
      if (window.innerWidth <= 1024) {
        toggleSidebar();
      }
    });
  });

  // Close sidebar when window is resized above mobile breakpoint
  window.addEventListener("resize", () => {
    if (window.innerWidth > 1024 && sidebar.classList.contains("active")) {
      toggleSidebar();
    }
  });

  // Update toggleSidebar function to handle escape key
  function toggleSidebar() {
    hamburgerMenu.classList.toggle("active");
    sidebar.classList.toggle("active");
    overlay.classList.toggle("active");
    document.body.style.overflow = sidebar.classList.contains("active")
      ? "hidden"
      : "";
  }

  // Add escape key handler
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && sidebar.classList.contains("active")) {
      toggleSidebar();
    }
  });
});
