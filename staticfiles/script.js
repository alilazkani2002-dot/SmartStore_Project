/* ============================================================
   Smart Store - Global JS File
   ============================================================ */

function getUserId() {
    return localStorage.getItem("user_id") || 1;
}

function saveToCart(product_id, category, price) {
    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    cart.push({
        product_id: product_id,
        category: category,
        price: price
    });

    localStorage.setItem("cart", JSON.stringify(cart));
}

function logBehavior(product_id, action) {
    const userId = getUserId();

    fetch("/api/behavior/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: userId,
            product_id: product_id,
            action: action
        })
    });
}

function addToCart(product_id, category, price) {
    saveToCart(product_id, category, price);
    logBehavior(product_id, "clicked");
    alert("Product added to cart!");
}

async function fetchProducts() {
    const response = await fetch("/api/products/");
    return await response.json();
}

async function fetchRecommendations() {
    const userId = getUserId();
    const response = await fetch(`/api/recommend/${userId}/`);
    return await response.json();
}

function clearCart() {
    localStorage.removeItem("cart");
}

console.log("Smart Store script.js loaded successfully!");
