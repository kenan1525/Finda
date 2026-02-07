function openProductModal(product) {
    document.getElementById("modalImage").src = product.image;
    document.getElementById("modalTitle").innerText = product.title;
    document.getElementById("modalPrice").innerText = product.price;
    document.getElementById("modalDescription").innerText = product.description;
    document.getElementById("modalSite").innerText = "Mağaza: " + product.site;
    document.getElementById("modalLink").href = product.link;
    document.getElementById("productModal").style.display = "flex";
}

function closeProductModal() {
    document.getElementById("productModal").style.display = "none";
}

function addToCart() {
    const title = document.getElementById('modalTitle').innerText;
    alert(title + ' sepete eklendi.');
    closeProductModal();
}

function openProductModalFromElement(element) {
    const product = {
        title: element.dataset.productTitle,
        price: element.dataset.productPrice,
        image: element.dataset.productImage,
        description: element.dataset.productDescription,
        site: element.dataset.productSite,
        link: element.dataset.productLink
    };
    openProductModal(product);
}

function searchProductBySameBrand(productTitle, site) {
    const encodedTitle = encodeURIComponent(productTitle);
    window.location.href = `/?query=${encodedTitle}&compare=true`;
}

function showAISummaryAfterImages() {
    const images = document.querySelectorAll('.product-image img, .compare-large .product-image img, .thumb-card img');
    if (images.length === 0) {
        const summaries = document.querySelectorAll('.ai-summary');
        summaries.forEach(summary => summary.classList.add('visible'));
        return;
    }

    let loadedCount = 0;
    const totalImages = images.length;
    let showTimeout;

    function showSummaries() {
        const summaries = document.querySelectorAll('.ai-summary');
        summaries.forEach(summary => summary.classList.add('visible'));
    }

    images.forEach(img => {
        if (img.complete) {
            loadedCount++;
        } else {
            img.addEventListener('load', () => {
                loadedCount++;
                if (loadedCount === totalImages) {
                    clearTimeout(showTimeout);
                    showSummaries();
                }
            });
            img.addEventListener('error', () => {
                loadedCount++;
                if (loadedCount === totalImages) {
                    clearTimeout(showTimeout);
                    showSummaries();
                }
            });
        }
    });

    if (loadedCount === totalImages) {
        showSummaries();
    } else {
        showTimeout = setTimeout(showSummaries, 2000);
    }
}

function swapMainProduct(elem) {
    const dataset = elem.dataset;
    const mainImage = document.querySelector('.compare-large .product-image img');
    const mainTitle = document.querySelector('.compare-large .product-title');
    const mainPrice = document.querySelector('.compare-large .product-price');
    const mainDesc = document.querySelector('.compare-large .product-body > p');
    const mainSiteBadge = document.querySelector('.compare-large .product-header .site-badge');
    const mainLink = document.querySelector('.compare-large .btn-primary');

    if (mainImage && dataset.productImage) mainImage.src = dataset.productImage;
    if (mainTitle && dataset.productTitle) mainTitle.innerText = dataset.productTitle;
    if (mainPrice && dataset.productPrice) mainPrice.innerText = dataset.productPrice;
    if (mainDesc && dataset.productDescription) mainDesc.innerText = dataset.productDescription;
    if (mainSiteBadge && dataset.productSite) mainSiteBadge.innerText = dataset.productSite;
    if (mainLink && dataset.productLink) mainLink.href = dataset.productLink;
}

document.addEventListener('DOMContentLoaded', function () {
    const targets = document.querySelectorAll(".typing-target");
    targets.forEach(target => {
        const text = target.dataset.text;
        let i = 0;
        target.innerHTML = "";
        function type() {
            if (i < text.length) {
                target.innerHTML += text.charAt(i);
                i++;
                setTimeout(type, 20);
            }
        }
        type();
    });

    showAISummaryAfterImages();

    setTimeout(() => {
        const compareSections = document.querySelectorAll('[id^="compare-section-"]');
        if (compareSections.length > 0) {
            const lastCompare = compareSections[compareSections.length - 1];
            lastCompare.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }, 300);
});
