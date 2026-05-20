const categories = {
    todos: 'Todos',
    anillos: 'Anillos',
    pulseras: 'Pulseras',
    collares: 'Collares'
};

let products = [];
let cart = loadCartFromStorage();
let selectedCategory = 'todos';

// DOM Elements
const cartItemsElement = document.getElementById('cart-items');
const cartTotalElement = document.getElementById('cart-total');
const checkoutButton = document.getElementById('checkout-button');
const checkoutModal = document.getElementById('checkout-modal');
const closeCheckout = document.getElementById('close-checkout');
const checkoutForm = document.getElementById('checkout-form');
const notification = document.getElementById('notification');
const productGridElement = document.getElementById('product-grid');
const searchInput = document.getElementById('search-input');
const searchBtn = document.querySelector('.search-btn');
const cartCount = document.getElementById('cart-count');
const cartFabNav = document.getElementById('cart-fab-nav');

// --- LocalStorage ---
function loadCartFromStorage() {
    try {
        return JSON.parse(localStorage.getItem('pj_cart')) || [];
    } catch {
        return [];
    }
}

function saveCartToStorage() {
    localStorage.setItem('pj_cart', JSON.stringify(cart));
}

// --- Category cards ---
function selectCategory(category) {
    const catalogSection = document.getElementById('catalogo');
    const eyebrow = document.getElementById('catalogo-eyebrow');
    const titulo = document.getElementById('catalogo-titulo');
    const labels = { todos: 'Todos los productos', anillos: 'Anillos', pulseras: 'Pulseras', collares: 'Collares' };

    if (category === 'combos') {
        document.getElementById('combos').scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
    }

    selectedCategory = category;
    renderProducts();
    catalogSection.style.display = 'block';
    if (eyebrow) eyebrow.textContent = labels[category];
    if (titulo) titulo.textContent = labels[category];
    setTimeout(() => catalogSection.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);
}

// --- Products ---
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        if (!response.ok) throw new Error('Error al cargar productos');
        products = await response.json();
        renderProducts();
        renderOffers();
        updateCart();
    } catch (err) {
        productGridElement.innerHTML = '<p style="color:#f87171;grid-column:1/-1">No se pudieron cargar los productos. Intenta recargar la página.</p>';
    }
}

function renderProducts() {
    const filtered = selectedCategory === 'todos'
        ? products.filter(p => p.category !== 'combos')
        : products.filter(p => p.category === selectedCategory);

    productGridElement.innerHTML = filtered.length
        ? filtered.map(createProductCard).join('')
        : '<p class="empty-message">No hay productos en esta categoría.</p>';

    const combosContainer = document.getElementById('combos-grid');
    combosContainer.innerHTML = products.filter(p => p.category === 'combos').map(createProductCard).join('');
}

function renderOffers() {
    const offersList = document.getElementById('offers-list');
    if (!offersList) return;
    const picks = products.slice(0, 4);
    offersList.innerHTML = picks.map(p => `
        <div class="offer-item" onclick="openProductModal(${p.id})">
            <img src="${p.image}" alt="${p.name}" />
            <div class="offer-info">
                <strong>${p.name}</strong>
                <div class="offer-prices">
                    <span class="offer-original">$${p.original_price.toLocaleString('es-AR')}</span>
                    <span class="offer-discount">$${p.price.toLocaleString('es-AR')}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function createProductCard(product) {
    const hasDiscount = product.original_price && product.original_price !== product.price;
    return `
        <article class="product-card" data-category="${product.category_label}">
            <div class="product-media" style="cursor:pointer" onclick="openProductModal(${product.id})">
                <img src="${product.image}" alt="${product.name}" loading="lazy" />
                ${hasDiscount ? '<span class="discount-badge">-20%</span>' : ''}
            </div>
            <div class="product-card-body">
                <h3 style="cursor:pointer" onclick="openProductModal(${product.id})">${product.name}</h3>
                <p>${product.description}</p>
                <div class="price-group">
                    ${hasDiscount ? `<span class="price-original">$${product.original_price.toLocaleString('es-AR')}</span>` : ''}
                    <span class="price">$${product.price.toLocaleString('es-AR')}</span>
                </div>
                <button class="btn btn-primary" onclick="addToCart(${product.id})">Agregar al carrito</button>
            </div>
        </article>
    `;
}

// --- Product Modal ---
function openProductModal(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;

    document.getElementById('modal-product-img').src = product.image;
    document.getElementById('modal-product-img').alt = product.name;
    document.getElementById('modal-product-category').textContent = product.category_label;
    document.getElementById('modal-product-name').textContent = product.name;
    document.getElementById('modal-product-desc').textContent = product.description;
    document.getElementById('modal-product-price').textContent = `$${product.price.toLocaleString('es-AR')}`;

    const addBtn = document.getElementById('modal-add-to-cart');
    addBtn.onclick = () => {
        addToCart(product.id);
        closeProductModal();
    };

    document.getElementById('product-modal').classList.add('active');
}

function closeProductModal() {
    document.getElementById('product-modal').classList.remove('active');
}

document.getElementById('close-product-modal').addEventListener('click', closeProductModal);
document.getElementById('product-modal').addEventListener('click', e => {
    if (e.target === document.getElementById('product-modal')) closeProductModal();
});

// --- Cart ---
function addToCart(productId) {
    const product = products.find(item => item.id === productId);
    if (!product) return;
    const existing = cart.find(item => item.id === productId);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ ...product, quantity: 1 });
    }
    saveCartToStorage();
    updateCart();
    showNotification(`✓ ${product.name} agregado`);
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCartToStorage();
    updateCart();
}

function changeQty(productId, delta) {
    const item = cart.find(i => i.id === productId);
    if (!item) return;
    item.quantity += delta;
    if (item.quantity <= 0) {
        cart = cart.filter(i => i.id !== productId);
    }
    saveCartToStorage();
    updateCart();
}

function updateCart() {
    const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

    // Update counter badge
    if (totalItems > 0) {
        cartCount.textContent = totalItems;
        cartCount.classList.add('visible');
    } else {
        cartCount.classList.remove('visible');
    }

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
                <span>$${(item.price * item.quantity).toLocaleString('es-AR')}</span>
            </div>
            <div class="cart-item-qty">
                <button class="qty-btn" onclick="changeQty(${item.id}, -1)">−</button>
                <span class="qty-value">${item.quantity}</span>
                <button class="qty-btn" onclick="changeQty(${item.id}, 1)">+</button>
                <button class="cart-item button" onclick="removeFromCart(${item.id})" style="margin-left:0.5rem">✕</button>
            </div>
        </div>
    `).join('');

    cartTotalElement.textContent = `$${total.toLocaleString('es-AR')}`;
    checkoutButton.disabled = false;
}

// Scroll al carrito al hacer clic en el ícono del navbar
cartFabNav.addEventListener('click', () => {
    document.querySelector('.section-cart').scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// --- Notification ---
function showNotification(message) {
    notification.textContent = message;
    notification.classList.add('show');
    setTimeout(() => notification.classList.remove('show'), 2800);
}

// --- Checkout Modal ---
checkoutButton.addEventListener('click', () => {
    checkoutModal.classList.add('active');
});

closeCheckout.addEventListener('click', () => {
    checkoutModal.classList.remove('active');
});

checkoutModal.addEventListener('click', e => {
    if (e.target === checkoutModal) checkoutModal.classList.remove('active');
});

checkoutForm.addEventListener('submit', async event => {
    event.preventDefault();
    const submitBtn = checkoutForm.querySelector('button[type=submit]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Procesando...';

    const formData = new FormData(checkoutForm);
    const order = {
        buyerName: formData.get('buyerName'),
        buyerEmail: formData.get('buyerEmail'),
        buyerDni: formData.get('buyerDni'),
        paymentMethod: formData.get('paymentMethod'),
        items: cart.map(item => ({ id: item.id, title: item.name, quantity: item.quantity, unit_price: item.price }))
    };

    try {
        const response = await fetch('/api/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(order)
        });

        if (!response.ok) {
            const error = await response.json();
            showNotification(error.message || 'Error procesando la compra.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Confirmar compra';
            return;
        }

        const result = await response.json();
        cart = [];
        saveCartToStorage();
        updateCart();
        showNotification('Compra iniciada. Redirigiendo...');
        checkoutModal.classList.remove('active');
        window.open(result.invoice_url, '_blank');
        window.location.href = result.payment_url;
    } catch {
        showNotification('Error de conexión. Intenta nuevamente.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Confirmar compra';
    }
});

// --- Menu ---
const menuBtn = document.getElementById('menu-btn');
const menuPanel = document.getElementById('menu-panel');
const menuClose = document.getElementById('menu-close');

function openMenu() {
    menuPanel.classList.add('active');
    document.body.classList.add('menu-open');
}

function closeMenu() {
    menuPanel.classList.remove('active');
    document.body.classList.remove('menu-open');
}

menuBtn.addEventListener('click', () => {
    menuPanel.classList.contains('active') ? closeMenu() : openMenu();
});

menuClose.addEventListener('click', closeMenu);

menuPanel.addEventListener('click', e => {
    if (e.target === menuPanel) closeMenu();
});

document.querySelectorAll('.menu-link').forEach(button => {
    button.addEventListener('click', () => {
        const { action, target, category } = button.dataset;
        closeMenu();

        if (action === 'section' && target) {
            document.getElementById(target)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            return;
        }
        if (action === 'category') {
            selectCategory(category || 'todos');
            return;
        }
        if (action === 'cart') {
            document.querySelector('.section-cart')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            return;
        }
    });
});

const menuActionButton = document.querySelector('.menu-action');
if (menuActionButton) {
    menuActionButton.addEventListener('click', () => {
        closeMenu();
        if (cart.length === 0) {
            showNotification('Agrega productos al carrito antes de comprar.');
            return;
        }
        checkoutModal.classList.add('active');
    });
}

// --- Search ---
function handleSearch(query) {
    const q = query.trim().toLowerCase();

    if (!q) {
        renderProducts();
        document.getElementById('search-results-section')?.remove();
        return;
    }

    const filtered = products.filter(p =>
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.category_label.toLowerCase().includes(q)
    );

    // Ocultar secciones normales y mostrar sección de resultados
    document.getElementById('catalogo').style.display = 'none';
    document.getElementById('combos').style.display = 'none';

    let resultsSection = document.getElementById('search-results-section');
    if (!resultsSection) {
        resultsSection = document.createElement('section');
        resultsSection.id = 'search-results-section';
        resultsSection.className = 'section';
        document.querySelector('main').prepend(resultsSection);
    }

    if (filtered.length === 0) {
        resultsSection.innerHTML = `
            <div class="section-header">
                <p class="eyebrow">Búsqueda</p>
                <h2>Sin resultados para "${query}"</h2>
            </div>
            <p style="color:#999">Probá con otro término, como "anillo", "collar" o "combo".</p>
        `;
    } else {
        resultsSection.innerHTML = `
            <div class="section-header">
                <p class="eyebrow">Búsqueda</p>
                <h2>${filtered.length} resultado${filtered.length !== 1 ? 's' : ''} para "${query}"</h2>
            </div>
            <div class="product-grid">${filtered.map(createProductCard).join('')}</div>
        `;
    }

    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function clearSearch() {
    searchInput.value = '';
    document.getElementById('search-results-section')?.remove();
    document.getElementById('catalogo').style.display = '';
    document.getElementById('combos').style.display = '';
}

searchInput.addEventListener('input', e => {
    if (!e.target.value.trim()) {
        clearSearch();
    } else {
        handleSearch(e.target.value);
    }
});

searchInput.addEventListener('keydown', e => {
    if (e.key === 'Escape') clearSearch();
});

searchBtn.addEventListener('click', () => handleSearch(searchInput.value));

window.addEventListener('load', loadProducts);
