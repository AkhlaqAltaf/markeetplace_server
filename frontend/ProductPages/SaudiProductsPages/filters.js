// Initialize filters
const filters = {
  categories: new Set(),
  priceRange: {
    min: 0,
    max: 10000,
  },
  brands: new Set(),
};

function updateActiveFilters() {
  const activeFiltersContainer = document.querySelector(".active-filters");
  if (!activeFiltersContainer) return;

  activeFiltersContainer.innerHTML = "<p>Active Filters:</p>";

  // Add category filters
  filters.categories.forEach((category) => {
    addFilterTag(category, () => {
      const checkbox = document.querySelector(
        `.checkbox-item input[type="checkbox"][data-category="${category}"]`
      );
      if (checkbox) checkbox.checked = false;
      filters.categories.delete(category);
      applyFilters();
    });
  });

  // Add price range filter
  if (filters.priceRange.min > 0 || filters.priceRange.max < 10000) {
    addFilterTag(
      `Price: $${filters.priceRange.min} - $${filters.priceRange.max}`,
      () => {
        filters.priceRange.min = 0;
        filters.priceRange.max = 10000;
        // Uncheck all price checkboxes
        document
          .querySelectorAll('.checkbox-item input[type="checkbox"]')
          .forEach((cb) => {
            if (cb.parentElement.textContent.includes("$")) cb.checked = false;
          });
        applyFilters();
      }
    );
  }

  // Add brand filters
  filters.brands.forEach((brand) => {
    addFilterTag(brand, () => {
      const checkbox = document.querySelector(
        `.brand-item input[type="checkbox"][data-brand="${brand}"]`
      );
      if (checkbox) checkbox.checked = false;
      filters.brands.delete(brand);
      applyFilters();
    });
  });
}

function addFilterTag(text, removeCallback) {
  const activeFiltersContainer = document.querySelector(".active-filters");
  const filterTag = document.createElement("div");
  filterTag.className = "filter-tag";
  filterTag.innerHTML = `
    ${text}
    <i class="fas fa-times"></i>
  `;
  filterTag.querySelector("i").addEventListener("click", removeCallback);
  activeFiltersContainer.appendChild(filterTag);
}

function updateTotalProducts() {
  const totalElement = document.getElementById("totalProducts");
  if (totalElement) {
    totalElement.textContent = window.displayedProducts.length;
  }
}

function initializeFilters() {
  // Category filters
  document
    .querySelectorAll('.checkbox-group .checkbox-item input[type="checkbox"]')
    .forEach((checkbox) => {
      const label = checkbox.parentElement.textContent.trim();

      // Skip price checkboxes
      if (!label.includes("$") && label !== "All Price") {
        checkbox.addEventListener("change", () => {
          const category = label;
          if (checkbox.checked) {
            filters.categories.add(category);
          } else {
            filters.categories.delete(category);
          }
          console.log("Category filter changed:", category, checkbox.checked);
          applyFilters();
        });
      }
    });

  // Price range slider
  const priceSlider = document.querySelector(".price-range");
  if (priceSlider) {
    priceSlider.value = filters.priceRange.max;
    priceSlider.addEventListener("input", (e) => {
      filters.priceRange.max = parseInt(e.target.value);
      console.log("Price range changed:", filters.priceRange);
      applyFilters();
    });
  }

  // Price checkbox filters
  document
    .querySelectorAll('.checkbox-group .checkbox-item input[type="checkbox"]')
    .forEach((checkbox) => {
      const label = checkbox.parentElement.textContent.trim();
      if (label.includes("$") || label === "All Price") {
        checkbox.addEventListener("change", () => {
          handlePriceCheckbox(checkbox, label);
        });
      }
    });

  // Brand filters
  document
    .querySelectorAll('.brands-grid .brand-item input[type="checkbox"]')
    .forEach((checkbox) => {
      checkbox.addEventListener("change", () => {
        const brand = checkbox.nextElementSibling.textContent.trim();
        if (checkbox.checked) {
          filters.brands.add(brand);
        } else {
          filters.brands.delete(brand);
        }
        console.log("Brand filter changed:", brand, checkbox.checked);
        applyFilters();
      });
    });
}

function applyFilters() {
  // Start with all products
  let filtered = [...window.allProducts];

  // Apply category filters
  if (filters.categories.size > 0) {
    filtered = filtered.filter((product) => {
      return Array.from(filters.categories).some((category) => {
        if (category === "Electronics and Devices") {
          return [
            "SmartPhone",
            "Computer Accessories",
            "Mobile Accessories",
            "Headphone",
            "TV & Homes Appliances",
            "Camera & Photo",
            "Gaming Console",
          ].includes(product.category);
        }
        return product.category === category;
      });
    });
  }

  // Apply price filter
  filtered = filtered.filter(
    (product) =>
      product.price >= filters.priceRange.min &&
      product.price <= filters.priceRange.max
  );

  // Apply brand filter
  if (filters.brands.size > 0) {
    filtered = filtered.filter((product) => filters.brands.has(product.brand));
  }

  // Update displayed products
  window.displayedProducts = filtered;

  // Reset to first page and display
  currentPage = 1;
  window.displayProducts();
}

function handlePriceCheckbox(checkbox, label) {
  if (checkbox.checked) {
    // Uncheck other price checkboxes
    document
      .querySelectorAll('.checkbox-group .checkbox-item input[type="checkbox"]')
      .forEach((cb) => {
        if (cb !== checkbox && cb.parentElement.textContent.includes("$")) {
          cb.checked = false;
        }
      });

    // Set price range based on label
    switch (label.trim()) {
      case "Under $20":
        filters.priceRange = { min: 0, max: 20 };
        break;
      case "$25 to $100":
        filters.priceRange = { min: 25, max: 100 };
        break;
      case "$100 to $300":
        filters.priceRange = { min: 100, max: 300 };
        break;
      case "$300 to $500":
        filters.priceRange = { min: 300, max: 500 };
        break;
      case "$500 to $1,000":
        filters.priceRange = { min: 500, max: 1000 };
        break;
      case "$1,000 to $10,000":
        filters.priceRange = { min: 1000, max: 10000 };
        break;
      case "All Price":
        filters.priceRange = { min: 0, max: 10000 };
        break;
    }
  } else {
    // Reset price range when unchecked
    filters.priceRange = { min: 0, max: 10000 };
  }

  applyFilters();
}

// Initialize everything when the page loads
document.addEventListener("DOMContentLoaded", () => {
  console.log("Initializing filters...");

  // Initialize filters
  initializeFilters();

  // Display initial products
  window.displayProducts();
  updateTotalProducts();

  console.log("Filter initialization complete");
});
