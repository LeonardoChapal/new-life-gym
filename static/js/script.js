// ========== NEW LIFE GYM - JavaScript Principal ==========

document.addEventListener('DOMContentLoaded', function () {
    initNavigation();
    initAnimations();
    initFormValidation();
    initGallery();
    initScrollEffects();
    initImageUploads();   // drag-over visual feedback
});

// ========== NAVEGACIÓN ==========
function initNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-menu a');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath ||
            (currentPath === '/' && link.getAttribute('href').includes('home'))) {
            link.classList.add('active');
        }
    });

    const navbar = document.querySelector('.navbar');
    let lastScroll = 0, isScrolling;

    window.addEventListener('scroll', () => {
        const cur = window.pageYOffset;
        clearTimeout(isScrolling);

        if (cur <= 0) {
            navbar.style.transform = 'translateY(0)';
            navbar.style.opacity  = '1';
        } else if (cur > lastScroll && cur > 100) {
            navbar.style.transform = 'translateY(-100%)';
            navbar.style.opacity  = '0';
        } else if (cur < lastScroll) {
            navbar.style.transform = 'translateY(0)';
            navbar.style.opacity  = '1';
        }

        lastScroll = cur;
        navbar.classList.add('scrolling');
        isScrolling = setTimeout(() => navbar.classList.remove('scrolling'), 150);
    });
}

// ========== ANIMACIONES ==========
function initAnimations() {
    const cards = document.querySelectorAll('.card');
    const opts  = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity   = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, i * 100);
                observer.unobserve(entry.target);
            }
        });
    }, opts);

    cards.forEach(c => {
        c.style.opacity   = '0';
        c.style.transform = 'translateY(30px)';
        c.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(c);
    });

    // Hero fade on scroll
    const hero = document.querySelector('.hero');
    if (hero && !hero.classList.contains('hero-video-section')) {
        function handleHeroFade() {
            const scroll = window.pageYOffset;
            const h = hero.offsetHeight;
            hero.style.opacity = Math.max(0, Math.min(1, 1 - scroll / h));
        }
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(() => { handleHeroFade(); ticking = false; });
                ticking = true;
            }
        });
        handleHeroFade();
    }
}

// ========== VALIDACIÓN FORMULARIOS ==========
function initFormValidation() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function () {
            const btn = this.querySelector('button[type="submit"]');
            if (btn) {
                const orig = btn.innerHTML;
                btn.innerHTML  = '⏳ Procesando...';
                btn.disabled   = true;
                setTimeout(() => { btn.innerHTML = orig; btn.disabled = false; }, 2000);
            }
        });
    });
}

// ========== GALERÍA / LIGHTBOX ==========
function initGallery() {
    const items = document.querySelectorAll('.gallery-item');
    if (!items.length) return;

    if (!document.getElementById('lightbox')) {
        const lb = document.createElement('div');
        lb.id        = 'lightbox';
        lb.className = 'lightbox';
        lb.innerHTML = `
            <span class="lightbox-close">&times;</span>
            <img class="lightbox-content" id="lightbox-img" alt="Imagen ampliada" style="display:none">
            <div id="lightbox-placeholder" style="
                display:none; flex-direction:column; align-items:center;
                justify-content:center; color:white; text-align:center; padding:2rem;">
                <div style="font-size:5rem; margin-bottom:1.5rem;">📷</div>
                <h3 id="lightbox-ph-name" style="color:#ff0000; margin-bottom:1rem;"></h3>
                <p style="color:#ccc;">Imagen del gimnasio</p>
            </div>
            <div class="lightbox-filename" id="lightbox-filename"></div>`;
        document.body.appendChild(lb);

        lb.querySelector('.lightbox-close').onclick = () => lb.classList.remove('active');
        lb.onclick = e => { if (e.target === lb) lb.classList.remove('active'); };
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') lb.classList.remove('active');
        });
    }

    const lb      = document.getElementById('lightbox');
    const lbImg   = document.getElementById('lightbox-img');
    const lbPh    = document.getElementById('lightbox-placeholder');
    const lbPhN   = document.getElementById('lightbox-ph-name');
    const lbFname = document.getElementById('lightbox-filename');

    items.forEach(item => {
        item.style.cursor = 'pointer';
        item.addEventListener('click', function () {
            const img = this.querySelector('img');

            if (img && img.src && !img.complete === false && img.naturalWidth > 0) {
                // Imagen real cargada correctamente → mostrar en grande
                lbImg.src           = img.src;
                lbImg.style.display = 'block';
                lbPh.style.display  = 'none';
                lbFname.textContent = '';
            } else if (img && img.src) {
                lbImg.src           = img.src;
                lbImg.style.display = 'block';
                lbPh.style.display  = 'none';
                lbFname.textContent = '';
            } else {
                // Sin imagen real → mostrar placeholder con nombre
                const ph = this.querySelector('.gallery-placeholder');
                lbImg.style.display = 'none';
                lbPh.style.display  = 'flex';
                lbPhN.textContent   = ph ? ph.textContent.trim() : 'Foto del Gimnasio';
                lbFname.textContent = '';
            }
            lb.classList.add('active');
        });
    });
}

// ========== PREVIEW DE IMAGEN en formularios admin ==========
/**
 * previewImage(input, previewId, wrapperId, currentImgId?)
 *  - input        : el <input type="file"> que disparó el evento
 *  - previewId    : id del .image-preview-box donde mostrar la preview
 *  - wrapperId    : id del .image-upload-wrapper (para ocultar el placeholder)
 *  - currentImgId : (opcional) id del .image-current a ocultar cuando se selecciona nueva imagen
 */
function previewImage(input, previewId, wrapperId, currentImgId) {
    const file = input.files && input.files[0];
    if (!file) return;

    // Validar tamaño (5 MB)
    if (file.size > 5 * 1024 * 1024) {
        alert('La imagen no debe superar los 5 MB.');
        input.value = '';
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        const previewBox = document.getElementById(previewId);
        if (!previewBox) return;

        // Limpiar preview anterior y crear <img>
        previewBox.innerHTML = '';
        const img = document.createElement('img');
        img.src = e.target.result;
        previewBox.appendChild(img);
        previewBox.style.display = 'block';

        // Ocultar el placeholder del wrapper para dar más protagonismo a la preview
        const wrapper = document.getElementById(wrapperId);
        if (wrapper) {
            const ph = wrapper.querySelector('.upload-placeholder');
            if (ph) ph.style.display = 'none';
        }

        // Ocultar imagen actual (en editar) cuando el usuario elige una nueva
        if (currentImgId) {
            const cur = document.getElementById(currentImgId);
            if (cur) cur.style.display = 'none';
        }
    };
    reader.readAsDataURL(file);
}

// Drag-and-drop visual feedback
function initImageUploads() {
    document.querySelectorAll('.image-upload-wrapper').forEach(wrapper => {
        wrapper.addEventListener('dragover',  e => { e.preventDefault(); wrapper.classList.add('dragover'); });
        wrapper.addEventListener('dragleave', ()  => wrapper.classList.remove('dragover'));
        wrapper.addEventListener('drop',      e => {
            e.preventDefault();
            wrapper.classList.remove('dragover');
            const input = wrapper.querySelector('input[type="file"]');
            if (input && e.dataTransfer.files.length) {
                input.files = e.dataTransfer.files;
                input.dispatchEvent(new Event('change'));
            }
        });
    });
}

// ========== EFECTOS SCROLL ==========
function initScrollEffects() {
    const hero = document.querySelector('.hero-video-section') || document.querySelector('.hero');
    if (hero && !hero.classList.contains('hero-video-section')) {
        window.addEventListener('scroll', () => {
            hero.style.transform = `translateY(${window.pageYOffset * 0.5}px)`;
        });
    }
    createScrollTopButton();
}

function createScrollTopButton() {
    const btn = document.createElement('button');
    btn.innerHTML = '↑';
    btn.style.cssText = `
        position:fixed; bottom:30px; right:30px; width:50px; height:50px;
        background:var(--primary-color); color:white; border:none; border-radius:50%;
        font-size:1.5rem; cursor:pointer; opacity:0;
        transition:opacity 0.3s ease, transform 0.3s ease; z-index:1000;
        box-shadow:0 4px 15px rgba(255,0,0,0.4);`;
    btn.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
    btn.addEventListener('mouseenter', () => btn.style.transform = 'scale(1.1)');
    btn.addEventListener('mouseleave', () => btn.style.transform = 'scale(1)');
    window.addEventListener('scroll', () => {
        btn.style.opacity = window.pageYOffset > 300 ? '1' : '0';
    });
    document.body.appendChild(btn);
}

// ========== ANIMACIONES CSS EXTRA ==========
const styleEl = document.createElement('style');
styleEl.textContent = `
    @keyframes slideIn  { from { transform:translateX(400px); opacity:0 } to { transform:translateX(0); opacity:1 } }
    @keyframes slideOut { from { transform:translateX(0); opacity:1 } to { transform:translateX(400px); opacity:0 } }
    @keyframes pulse    { 0%,100% { transform:scale(1) } 50% { transform:scale(1.05) } }
`;
document.head.appendChild(styleEl);

// ========== DETECCIÓN DISPOSITIVO ==========
if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent) &&
    !/iPad|Android/i.test(navigator.userAgent) || window.innerWidth <= 768) {
    document.body.classList.add('mobile-device');
}

// ========== COMPRAS ==========
document.addEventListener('submit', function (e) {
    const form = e.target;
    if (form.action.includes('comprar_membresia') || form.action.includes('comprar_producto')) {
        console.log('Procesando compra...');
    }
});