document.addEventListener("DOMContentLoaded", function () {
  // Get all product rows
  const productRows = document.querySelectorAll(".product-row");

  productRows.forEach((row) => {
    const minusBtn = row.querySelector(".minus-btn");
    const plusBtn = row.querySelector(".plus-btn");
    const quantitySpan = row.querySelector(".quantity-value");
    const subtotalDiv = row.querySelector(".product-subtotal");
    const priceElement =
      row.querySelector(".price-current") ||
      row.querySelector(".product-price");

    // Get base price (remove $ and convert to number)
    const basePrice = parseFloat(priceElement.innerText.replace("$", ""));

    // Function to format price
    function formatPrice(price) {
      return `$${price.toFixed(2)}`;
    }

    // Function to update subtotal
    function updateSubtotal(quantity) {
      const subtotal = basePrice * quantity;
      subtotalDiv.textContent = formatPrice(subtotal);
      updateCartTotals();

      // Update button states
      minusBtn.disabled = quantity <= 1;
      plusBtn.disabled = quantity >= 10;
    }

    // Minus button click
    minusBtn.addEventListener("click", () => {
      let quantity = parseInt(quantitySpan.textContent);
      if (quantity > 1) {
        quantity--;
        quantitySpan.textContent = quantity;
        updateSubtotal(quantity);
      }
    });

    // Plus button click
    plusBtn.addEventListener("click", () => {
      let quantity = parseInt(quantitySpan.textContent);
      if (quantity < 10) {
        quantity++;
        quantitySpan.textContent = quantity;
        updateSubtotal(quantity);
      }
    });

    // Initialize subtotal
    updateSubtotal(parseInt(quantitySpan.textContent));
  });

  // Function to update cart totals
  function updateCartTotals() {
    let subtotal = 0;

    // Calculate subtotal from all products
    productRows.forEach((row) => {
      const amount = parseFloat(
        row.querySelector(".product-subtotal").textContent.replace("$", "")
      );
      subtotal += amount;
    });

    // Calculate other amounts
    const tax = subtotal * 0.18; // 18% tax
    const total = subtotal + tax;

    // Update the display
    document.querySelector(
      ".total-row:nth-child(1) span:last-child"
    ).textContent = formatPrice(subtotal);
    document.querySelector(
      ".total-row:nth-child(3) span:last-child"
    ).textContent = formatPrice(tax);
    document.querySelector(".total-row.final span:last-child").textContent =
      formatPrice(total);
  }

  // Helper function to format price
  function formatPrice(price) {
    return `$${price.toFixed(2)}`;
  }

  // Update cart button functionality
  const updateCartBtn = document.querySelector(".update-btn");
  updateCartBtn.addEventListener("click", () => {
    updateCartTotals();
    alert("Cart updated successfully!");
  });

  // Initialize totals
  updateCartTotals();
});
