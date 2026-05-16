const categories = {
    todos: 'Todos',
    anillos: 'Anillos',
    pulseras: 'Pulseras',
    collares: 'Collares'
};

let products = [];
let cart = [];
let selectedCategory = 'todos';

const cartItemsElement = document.getElementById('cart-items');
const cartTotalElement = document.getElementById('cart-total');
const checkoutButton = document.getElementById('checkout-button');
const checkoutModal = document.getElementById('checkout-modal');
const closeCheckout = document.getElementById('close-checkout');
const checkoutForm = document.getElementById('checkout-form');
const notification = document.getElementById('notification');
const filterButtonsElement = document.getElementById('filter-buttons');
const productGridElement = document.getElementById('product-grid');
const hamburgerBtn = document.getElementById('hamburger-btn');
const navMenu = document.getElementById('nav-menu');

async function loadProducts() {
    const response = await fetch('/api/products');
    products = await response.json();
    renderFilterButtons();
    renderProducts();
}

function renderFilterButtons() {
    filterButtonsElement.innerHTML = Object.entries(categories).map(([key, title]) => {
        const activeClass = key === selectedCategory ? 'filter-btn active' : 'filter-btn';
        return `<button class="${activeClass}" data-category="${key}">${title}</button>`;
    }).join('');

    filterButtonsElement.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', () => {
            selectedCategory = button.dataset.category;
            renderFilterButtons();
            renderProducts();
        });
    });
}

function renderProducts() {
    const filteredProducts = selectedCategory === 'todos'
        ? products.filter(item => item.category !== 'combos')
        : products.filter(item => item.category === selectedCategory);

    productGridElement.innerHTML = filteredProducts.length
        ? filteredProducts.map(createProductCard).join('')
        : '<p class="empty-message">No hay productos disponibles en esta categoría.</p>';

    const combosContainer = document.getElementById('combos');
    const comboCards = products.filter(item => item.category === 'combos').map(createProductCard).join('');
    combosContainer.innerHTML = comboCards;
}

function createProductCard(product) {
    return `
        <article class="product-card" data-category="${product.category_label}">
            <div class="product-media">
                <img src="${product.image}" alt="${product.name}" loading="lazy" />
            </div>
            <div class="product-card-body">
                <h3>${product.name}</h3>
                <p>${product.description}</p>
                <div class="price">$${product.price.toFixed(2)}</div>
                <button class="btn btn-primary" onclick="addToCart(${product.id})">Agregar al carrito</button>
            </div>
        </article>
    `;
}

function addToCart(productId) {
    const product = products.find(item => item.id === productId);
    if (!product) return;
    const existing = cart.find(item => item.id === productId);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ ...product, quantity: 1 });
    }
    updateCart();
    showNotification(`Agregado: ${product.name}`);
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCart();
}

function updateCart() {
    if (cart.length === 0) {
        cartItemsElement.innerHTML = 'Tu carrito está vacío.';
        checkoutButton.disabled = true;
        cartTotalElement.textContent = '$0';
        return;
    }

    cartItemsElement.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div>
                <strong>${item.name}</strong>
                <span>${item.quantity} unidad(es) · $${(item.price * item.quantity).toFixed(2)}</span>
            </div>
            <button onclick="removeFromCart(${item.id})">Eliminar</button>
        </div>
    `).join('');

    const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    cartTotalElement.textContent = `$${total.toFixed(2)}`;
    checkoutButton.disabled = false;
}

function showNotification(message) {
    notification.textContent = message;
    notification.classList.add('show');
    setTimeout(() => notification.classList.remove('show'), 2800);
}

checkoutButton.addEventListener('click', () => {
    checkoutModal.classList.add('active');
});

closeCheckout.addEventListener('click', () => {
    checkoutModal.classList.remove('active');
});

checkoutForm.addEventListener('submit', async event => {
    event.preventDefault();
    const formData = new FormData(checkoutForm);
    const order = {
        buyerName: formData.get('buyerName'),
        buyerEmail: formData.get('buyerEmail'),
        buyerDni: formData.get('buyerDni'),
        paymentMethod: formData.get('paymentMethod'),
        items: cart.map(item => ({ id: item.id, title: item.name, quantity: item.quantity, unit_price: item.price }))
    };

    checkoutForm.querySelector('button[type=submit]').disabled = true;
    const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(order)
    });

    if (!response.ok) {
        const error = await response.json();
        showNotification(error.message || 'Error procesando la compra.');
        checkoutForm.querySelector('button[type=submit]').disabled = false;
        return;
    }

    const result = await response.json();
    showNotification('Compra iniciada. Redirigiendo...');
    checkoutModal.classList.remove('active');
    window.open(result.invoice_url, '_blank');
    window.location.href = result.payment_url;
});

// Hamburger Menu
hamburgerBtn.addEventListener('click', () => {
    hamburgerBtn.classList.toggle('active');
    navMenu.classList.toggle('active');
});

// Close menu when clicking on a link
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        hamburgerBtn.classList.remove('active');
        navMenu.classList.remove('active');
    });
});

// Close menu when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.navbar-container')) {
        hamburgerBtn.classList.remove('active');
        navMenu.classList.remove('active');
    }
});

window.addEventListener('load', loadProducts);
