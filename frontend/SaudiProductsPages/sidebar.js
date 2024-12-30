document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebarToggle");
  const closeSidebar = document.getElementById("closeSidebar");

  // Create overlay element
  const overlay = document.createElement("div");
  overlay.className = "sidebar-overlay";
  document.body.appendChild(overlay);

  // Toggle sidebar
  function toggleSidebar() {
    sidebar.classList.toggle("active");
    overlay.classList.toggle("active");
    document.body.style.overflow = sidebar.classList.contains("active")
      ? "hidden"
      : "";
  }

  // Open sidebar
  sidebarToggle.addEventListener("click", toggleSidebar);

  // Close sidebar
  closeSidebar.addEventListener("click", toggleSidebar);

  // Close sidebar when clicking overlay
  overlay.addEventListener("click", toggleSidebar);

  // Close sidebar on window resize if larger than mobile breakpoint
  window.addEventListener("resize", function () {
    if (window.innerWidth > 1024 && sidebar.classList.contains("active")) {
      sidebar.classList.remove("active");
      overlay.classList.remove("active");
      document.body.style.overflow = "";
    }
  });
});
