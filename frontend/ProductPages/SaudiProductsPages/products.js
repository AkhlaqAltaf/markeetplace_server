// Configuration
const ITEMS_PER_PAGE = 20;
let currentPage = 1;
let totalPages = 1;

// Products data with diverse categories and prices
const products = [
  // SmartPhones
  {
    id: 1,
    name: "iPhone 14 Pro",
    category: "SmartPhone",
    price: 999,
    brand: "Apple",
    image: "https://via.placeholder.com/150",
    description: "Latest iPhone with dynamic island",
    stars: 720,
    tag: "HOT",
  },
  {
    id: 2,
    name: "Samsung Galaxy S23",
    category: "SmartPhone",
    price: 899,
    brand: "Samsung",
    image: "https://via.placeholder.com/150",
    description: "Premium Android smartphone",
    stars: 650,
  },
  {
    id: 3,
    name: "Google Pixel 7",
    category: "SmartPhone",
    price: 699,
    brand: "Google",
    image: "https://via.placeholder.com/150",
    description: "Pure Android experience",
    stars: 600,
  },
  // Computer Accessories
  {
    id: 4,
    name: "MacBook Pro 16",
    category: "Computer Accessories",
    price: 2499,
    brand: "Apple",
    image: "https://via.placeholder.com/150",
    description: "Powerful laptop with M2 chip",
    stars: 480,
    tag: "BEST DEALS",
  },
  {
    id: 5,
    name: "Logitech MX Master 3",
    category: "Computer Accessories",
    price: 99,
    brand: "Logitech",
    image: "https://via.placeholder.com/150",
    description: "Premium wireless mouse",
    stars: 320,
  },
  // Headphones
  {
    id: 6,
    name: "Sony WH-1000XM4",
    category: "Headphone",
    price: 349,
    brand: "Sony",
    image: "https://via.placeholder.com/150",
    description: "Premium noise-cancelling headphones",
    stars: 550,
  },
  // TV & Home Appliances
  {
    id: 7,
    name: 'Samsung 65" QLED TV',
    category: "TV & Homes Appliances",
    price: 1299,
    brand: "Samsung",
    image: "https://via.placeholder.com/150",
    description: "4K QLED Smart TV",
    stars: 420,
  },
  {
    id: 8,
    name: "Samsung Microwave",
    category: "TV & Homes Appliances",
    price: 159,
    brand: "Samsung",
    image: "https://via.placeholder.com/150",
    description: "Smart microwave oven",
    stars: 240,
  },
  // Mobile Accessories
  {
    id: 9,
    name: "AirPods Pro",
    category: "Mobile Accessories",
    price: 249,
    brand: "Apple",
    image: "https://via.placeholder.com/150",
    description: "Wireless earbuds with noise cancellation",
    stars: 680,
  },
  // Watches & Accessories
  {
    id: 10,
    name: "Apple Watch Series 8",
    category: "Watchs & Accessories",
    price: 399,
    brand: "Apple",
    image: "https://via.placeholder.com/150",
    description: "Latest smartwatch with health features",
    stars: 380,
  },
  // Camera & Photo
  {
    id: 11,
    name: "Canon EOS R5",
    category: "Camera & Photo",
    price: 3899,
    brand: "Canon",
    image: "https://via.placeholder.com/150",
    description: "Professional mirrorless camera",
    stars: 280,
  },
  // GPS & Navigation
  {
    id: 12,
    name: "Garmin Fenix 7",
    category: "GPS & Navigation",
    price: 699,
    brand: "Garmin",
    image: "https://via.placeholder.com/150",
    description: "Premium GPS smartwatch",
    stars: 290,
  },
  // Gaming Console
  {
    id: 13,
    name: "PlayStation 5",
    category: "Gaming Console",
    price: 499,
    brand: "Sony",
    image: "https://via.placeholder.com/150",
    description: "Next-gen gaming console",
    stars: 750,
    tag: "HOT",
  },
];

// Initialize products arrays AFTER products array is defined
window.allProducts = [...products];
window.displayedProducts = [...products];

// Function to create product card
function createProductCard(product) {
  return `
        <div class="product-card">
            <div class="relative">
                ${
                  product.tag
                    ? `<div class="product-tag ${
                        product.tag === "HOT"
                          ? "hot-tag"
                          : product.tag === "BEST DEALS"
                          ? "best-deals-tag"
                          : product.tag === "25% OFF"
                          ? "discount-tag"
                          : product.tag === "SALE"
                          ? "sale-tag"
                          : ""
                      }">${product.tag}</div>`
                    : ""
                }
                <img src="${product.image}" alt="${
    product.name
  }" class="product-image">
            </div>
            <div class="product-info">
                <div class="rating">
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <i class="fas fa-star"></i>
                    <span>(${product.stars})</span>
                </div>
                <h2 class="product-title">${product.name}</h2>
                <p class="product-desc">${product.description}</p>
                <div class="product-price">$${product.price.toFixed(2)}</div>
            </div>
        </div>
    `;
}

// Function to display products with pagination
function displayProducts() {
  const container = document.getElementById("productsContainer");
  if (!container) {
    console.error("Products container not found!");
    return;
  }

  // Calculate total pages based on currently displayed products
  totalPages = Math.ceil(window.displayedProducts.length / ITEMS_PER_PAGE);

  // Ensure current page is valid
  if (currentPage > totalPages) currentPage = totalPages;
  if (currentPage < 1) currentPage = 1;

  // Get products for current page
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = Math.min(
    startIndex + ITEMS_PER_PAGE,
    window.displayedProducts.length
  );
  const productsToShow = window.displayedProducts.slice(startIndex, endIndex);

  console.log(
    `Showing ${productsToShow.length} products on page ${currentPage} of ${totalPages}`
  );

  // Display products
  container.innerHTML = productsToShow.map(createProductCard).join("");

  // Update pagination and counts
  updatePagination();
  updateTotalProducts();
}

// Function to update total products count
function updateTotalProducts() {
  const totalElement = document.getElementById("totalProducts");
  if (totalElement) {
    totalElement.textContent = window.displayedProducts.length;
  }
}

// Update pagination function
function updatePagination() {
  const paginationContainer = document.getElementById("pageNumbers");
  if (!paginationContainer) return;

  paginationContainer.innerHTML = "";

  // Show max 5 pages at a time
  let startPage = Math.max(1, currentPage - 2);
  let endPage = Math.min(totalPages, startPage + 4);

  // Add page numbers
  for (let i = startPage; i <= endPage; i++) {
    const button = document.createElement("button");
    button.className = `page-btn ${i === currentPage ? "active" : ""}`;
    button.textContent = String(i).padStart(2, "0");
    button.onclick = () => {
      currentPage = i;
      displayProducts();
    };
    paginationContainer.appendChild(button);
  }

  // Update prev/next buttons
  const prevButton = document.getElementById("prevPage");
  const nextButton = document.getElementById("nextPage");

  if (prevButton) prevButton.disabled = currentPage === 1;
  if (nextButton) nextButton.disabled = currentPage === totalPages;
}

// Initialize pagination controls
function initializePagination() {
  const prevButton = document.getElementById("prevPage");
  const nextButton = document.getElementById("nextPage");

  if (prevButton) {
    prevButton.addEventListener("click", () => {
      if (currentPage > 1) {
        currentPage--;
        displayProducts();
      }
    });
  }

  if (nextButton) {
    nextButton.addEventListener("click", () => {
      if (currentPage < totalPages) {
        currentPage++;
        displayProducts();
      }
    });
  }
}

// Initialize everything
document.addEventListener("DOMContentLoaded", () => {
  // Generate more products
  const allGeneratedProducts = generateMoreProducts();
  console.log("Total products generated:", allGeneratedProducts.length);

  // Set initial products
  window.allProducts = allGeneratedProducts;
  window.displayedProducts = allGeneratedProducts;

  // Calculate initial pages
  totalPages = Math.ceil(allGeneratedProducts.length / ITEMS_PER_PAGE);
  currentPage = 1;

  // Initialize controls
  initializePagination();
  displayProducts();

  // Initialize search
  const searchInput = document.getElementById("searchInput");
  if (searchInput) {
    searchInput.addEventListener("input", handleSearch);
  }

  // Initialize sort
  const sortSelect = document.getElementById("sortSelect");
  if (sortSelect) {
    sortSelect.addEventListener("change", handleSort);
  }
});

// Make displayProducts function globally available
window.displayProducts = displayProducts;

// Function to generate more products
function generateMoreProducts() {
  const baseProducts = [...products];
  const moreProducts = [];
  let id = products.length + 1;

  baseProducts.forEach((baseProduct) => {
    // Create variations of each product
    for (let i = 1; i <= 3; i++) {
      moreProducts.push({
        ...baseProduct,
        id: id++,
        name: `${baseProduct.name} ${i === 1 ? "" : i}`,
        price: Math.round(baseProduct.price * (0.9 + Math.random() * 0.2)),
        stars: Math.round(baseProduct.stars * (0.9 + Math.random() * 0.2)),
      });
    }
  });

  return [...products, ...moreProducts];
}

function handleSearch() {
  const searchTerm = document.getElementById("searchInput").value.toLowerCase();

  if (!searchTerm) {
    window.displayedProducts = [...window.allProducts];
  } else {
    window.displayedProducts = window.allProducts.filter(
      (product) =>
        product.name.toLowerCase().includes(searchTerm) ||
        product.description.toLowerCase().includes(searchTerm) ||
        product.category.toLowerCase().includes(searchTerm) ||
        product.brand.toLowerCase().includes(searchTerm)
    );
  }

  currentPage = 1;
  displayProducts();
}

// Make sure sorting is using the correct array
function handleSort() {
  const sortValue = document.getElementById("sortSelect").value;

  switch (sortValue) {
    case "popular":
      window.displayedProducts.sort((a, b) => b.stars - a.stars);
      break;
    case "priceAsc":
      window.displayedProducts.sort((a, b) => a.price - b.price);
      break;
    case "priceDesc":
      window.displayedProducts.sort((a, b) => b.price - a.price);
      break;
    case "nameAsc":
      window.displayedProducts.sort((a, b) => a.name.localeCompare(b.name));
      break;
    case "nameDesc":
      window.displayedProducts.sort((a, b) => b.name.localeCompare(a.name));
      break;
  }

  currentPage = 1; // Reset to first page when sorting
  displayProducts();
}
