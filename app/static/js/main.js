// ==================== GLOBAL CART ====================
let cart = [];
try {
    const stored = localStorage.getItem('cart');
    cart = stored ? JSON.parse(stored) : [];
    if (!Array.isArray(cart)) cart = [];
} catch (error) {
    console.warn('Invalid cart data in localStorage, resetting cart.', error);
    cart = [];
    localStorage.removeItem('cart');
}

// Update cart count in navbar
function updateCartCount() {
    const countElement = document.getElementById('cart-count');
    if (countElement) {
        const total = cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
        countElement.textContent = total;
    }
}

// ==================== ADD TO CART ====================
function addToCart(id, name, price, image) {
    const qtyInput = document.getElementById(`qty-${id}`);
    const quantity = qtyInput ? parseInt(qtyInput.value) || 1 : 1;

    const normalizedImage = image ? image.toString() : '';
    const existing = cart.find(item => item.id === id);
    
    if (existing) {
        existing.quantity += quantity;
    } else {
        cart.push({
            id: id,
            name: name,
            price: parseFloat(price),
            image: normalizedImage,
            quantity: quantity
        });
    }

    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    showToast(`${quantity} × ${name} added to cart!`);
}

function getCartImageUrl(image) {
    if (!image) return 'https://via.placeholder.com/300x300?text=No+Image';
    
    // If it's already a data URI, return as-is
    if (image.startsWith('data:image/')) {
        return image;
    }
    
    let normalized = image.toString();

    try {
        const parsed = new URL(normalized, window.location.href);
        normalized = parsed.pathname + parsed.search + parsed.hash;
    } catch (err) {
        // ignore invalid URL parse and fall back to raw value
    }

    if (normalized.startsWith('/static/uploads/') || normalized.startsWith('/static/')) {
        return normalized;
    }
    if (normalized.startsWith('http://') || normalized.startsWith('https://')) {
        return normalized;
    }
    const uploadsPrefix = window.STATIC_UPLOADS_PREFIX || '/static/uploads/';
    const cleaned = normalized.replace(/^uploads\//, '');
    return `${uploadsPrefix}${cleaned}`;
}

// ==================== RENDER CART ====================
function renderCart() {
    const container = document.getElementById('cart-items');
    if (!container) return;

    container.innerHTML = '';
    let total = 0;

    if (cart.length === 0) {
        container.innerHTML = `
            <div class="text-center py-20">
                <i class="fas fa-shopping-cart text-6xl text-gray-300 mb-4"></i>
                <p class="text-xl text-gray-500">Your cart is empty</p>
            </div>`;
        document.getElementById('cart-total').textContent = 'KSh 0';
        return;
    }

    cart.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;

        const div = document.createElement('div');
        div.className = "flex gap-6 bg-white p-6 rounded-2xl shadow-sm";
        const imageUrl = getCartImageUrl(item.image);
        div.innerHTML = `
            <img src="${imageUrl}" class="w-28 h-28 object-cover rounded-xl" alt="${item.name}">
            <div class="flex-1">
                <h4 class="font-semibold text-lg">${item.name}</h4>
                <p class="text-amber-700 font-bold">KSh ${item.price}</p>
                <div class="flex items-center gap-4 mt-4">
                    <button onclick="changeQuantity(${index}, -1)" class="w-8 h-8 border rounded-lg">-</button>
                    <span class="font-medium w-8 text-center">${item.quantity}</span>
                    <button onclick="changeQuantity(${index}, 1)" class="w-8 h-8 border rounded-lg">+</button>
                    <button onclick="removeFromCart(${index})" class="ml-auto text-red-600 hover:text-red-700">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="text-right font-bold text-xl">KSh ${itemTotal}</div>
        `;
        container.appendChild(div);
    });

    document.getElementById('cart-total').textContent = `KSh ${total}`;
}

function changeQuantity(index, change) {
    cart[index].quantity += change;
    if (cart[index].quantity < 1) cart[index].quantity = 1;
    localStorage.setItem('cart', JSON.stringify(cart));
    renderCart();
    updateCartCount();
}

function removeFromCart(index) {
    cart.splice(index, 1);
    localStorage.setItem('cart', JSON.stringify(cart));
    renderCart();
    updateCartCount();
}

// ==================== IMAGE SLIDER ====================
function nextImage(btn) {
    const images = btn.parentElement.querySelectorAll('.slider-image');
    let active = 0;
    images.forEach((img, i) => { if (parseFloat(img.style.opacity) === 1) active = i; });

    images[active].style.opacity = '0';
    const next = (active + 1) % images.length;
    images[next].style.opacity = '1';
}

function prevImage(btn) {
    const images = btn.parentElement.querySelectorAll('.slider-image');
    let active = 0;
    images.forEach((img, i) => { if (parseFloat(img.style.opacity) === 1) active = i; });

    images[active].style.opacity = '0';
    const prev = (active - 1 + images.length) % images.length;
    images[prev].style.opacity = '1';
}

// ==================== CHECKOUT ====================
function handleCheckout() {
    const form = document.getElementById('checkout-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('submit-btn');
        const originalText = btn.textContent;
        btn.disabled = true;
        btn.textContent = "Processing...";

        const name = document.getElementById('name').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const location = document.getElementById('location').value.trim();

        if (!name || !phone || !location) {
            showToast("Please fill all fields");
            btn.disabled = false;
            btn.textContent = originalText;
            return;
        }

        if (cart.length === 0) {
            showToast("Your cart is empty. Add items before checkout.");
            btn.disabled = false;
            btn.textContent = originalText;
            return;
        }

        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

        try {
            const res = await fetch('/checkout', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, phone, location, items: cart, total})
            });
            const data = await res.json();

            if (data.success) {
                localStorage.removeItem('cart');
                window.location.href = `/order_success?order_number=${data.order_number}`;
            } else {
                alert("Failed to place order");
            }
        } catch (err) {
            console.error(err);
            alert("Error connecting to server");
        } finally {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    });
}

// Toast
function showToast(msg) {
    const t = document.createElement('div');
    t.style.cssText = 'position:fixed;bottom:25px;right:25px;background:#1f2937;color:white;padding:16px 24px;border-radius:12px;z-index:9999;';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2500);
}

// ==================== INITIALIZE ====================
document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();

    document.querySelectorAll('.add-to-cart-button').forEach(button => {
        button.addEventListener('click', () => {
            const id = parseInt(button.dataset.productId, 10);
            const name = button.dataset.productName || '';
            const price = parseFloat(button.dataset.productPrice) || 0;
            const image = button.dataset.productImage || '';
            addToCart(id, name, price, image);
        });
    });

    if (document.getElementById('cart-items')) renderCart();
    if (document.getElementById('checkout-form')) {
        const totalEl = document.getElementById('total-amount');
        if (totalEl) totalEl.textContent = `KSh ${cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)}`;

        if (cart.length === 0) {
            const btn = document.getElementById('submit-btn');
            if (btn) {
                btn.disabled = true;
                btn.textContent = 'Cart is empty';
                btn.classList.add('bg-gray-400', 'cursor-not-allowed');
            }
            showToast('Your cart is empty. Add items before checkout.');
        }

        handleCheckout();
    }
});