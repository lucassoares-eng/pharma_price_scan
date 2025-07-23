let allProducts = [];
let selectedProduct = null;
let priceChart = null;
let currentSort = 'relevancia';
let currentPharmacyFilter = ''; // Variável global para preservar o filtro
let iaAnalysisCache = {}; // Cache para análises de IA
let currentPage = 1; // Página atual
let productsPerPage = 10; // Produtos por página

window.descontoBadgePlugin = {
    afterDatasetsDraw: function(chart) {
        const ctx = chart.ctx;
        const dataset = chart.data.datasets[0];
        if (!dataset.discounts) return;
        ctx.save();
        // Restaurar títulos
        let titleFont = window.innerWidth < 576 ? 'bold 9px Segoe UI, Arial' : 'bold 12px Segoe UI, Arial';
        ctx.font = titleFont;
        ctx.fillStyle = '#495057';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        const titleX = chart.scales.x.left - 20;
        const titleY = chart.chartArea.top - 10;
        ctx.fillText('Ranking', titleX, titleY);
        ctx.textAlign = 'right';
        ctx.font = titleFont;
        const descontoTitleX = chart.chartArea.right + (window.innerWidth < 576 ? 38 : 72);
        ctx.fillText('Desconto', descontoTitleX, titleY);
        ctx.textAlign = 'center';
        ctx.font = titleFont;
        const precoTitleX = (chart.chartArea.left + chart.chartArea.right) / 2;
        ctx.fillText('Preço (R$)', precoTitleX, titleY);
        chart.getDatasetMeta(0).data.forEach((bar, i) => {
            const discount = dataset.discounts[i];
            const price = dataset.data[i];
            const position = dataset.positions ? dataset.positions[i] : null;
            const priceLabel = `R$ ${price.toFixed(2).replace('.', ',')}`;
            // Fonte do preço mínimo/máximo
            let priceFont = 'bold 12px Segoe UI, Arial';
            if (window.innerWidth < 576) {
                priceFont = 'bold 8px Segoe UI, Arial';
            } else if (window.innerWidth < 992) {
                priceFont = 'bold 10px Segoe UI, Arial';
            } else {
                priceFont = 'bold 11px Segoe UI, Arial';
            }
            ctx.font = priceFont;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            // Centro da barra
            const barStart = chart.scales.x.left;
            const centerX = barStart + (bar.x - barStart) / 2;
            let textX = centerX;
            let textY = bar.y;
            let isSelected = window.selectedProduct && chart.data.labels[i] === window.selectedProduct.brand;
            ctx.fillStyle = isSelected ? '#222' : '#fff';
            ctx.fillText(priceLabel, textX, textY);
            // Preço máximo dentro da barra, alinhado à direita
            const chartData = chart.data;
            let maxPrice = null;
            if (chartData && chartData.datasets && chartData.datasets[1] && chartData.datasets[1].data) {
                maxPrice = price + chartData.datasets[1].data[i];
            }
            // Ajuste: alinhar ao final da barra de maior preço (usando a posição do segundo dataset)
            const metaMax = chart.getDatasetMeta(1); // meta do segundo dataset (diferença até o máximo)
            if (maxPrice && maxPrice > price && metaMax && metaMax.data && metaMax.data[i]) {
                let maxLabel = `R$ ${maxPrice.toFixed(2).replace('.', ',')}`;
                ctx.font = priceFont;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = '#222';
                // Alinhar ao lado externo direito da barra de maior preço
                ctx.fillText(maxLabel, metaMax.data[i].x + 6, metaMax.data[i].y);
            }
            const priceWidth = ctx.measureText(priceLabel).width;
            // Barras verticais de ranking
            if (position) {
                const brandProducts = allProducts.filter(p => p.brand === chart.data.labels[i]);
                const positions = brandProducts.map(p => p.position).filter(pos => pos !== null && pos !== undefined);
                let moda = null;
                if (positions.length > 0) {
                    const freq = {};
                    positions.forEach(pos => { freq[pos] = (freq[pos] || 0) + 1; });
                    const maxFreq = Math.max(...Object.values(freq));
                    const modaCandidates = Object.keys(freq).filter(pos => freq[pos] === maxFreq).map(Number);
                    moda = Math.floor(Math.min(...modaCandidates));
                }
                let barColors = [];
                if (moda === 1) {
                    barColors = ['#FFD700', '#FFD700', '#FFD700', '#FFD700', '#FFD700'];
                } else if (moda === 2) {
                    barColors = ['#5bc0f7', '#5bc0f7', '#5bc0f7', '#5bc0f7', '#e0e0e0'];
                } else if (moda === 3) {
                    barColors = ['#CD7F32', '#CD7F32', '#CD7F32', '#e0e0e0', '#e0e0e0'];
                } else if (moda === 4) {
                    barColors = ['#555555', '#555555', '#e0e0e0', '#e0e0e0', '#e0e0e0'];
                } else if (moda === 5) {
                    barColors = ['#555555', '#e0e0e0', '#e0e0e0', '#e0e0e0', '#e0e0e0'];
                } else {
                    barColors = ['#e0e0e0', '#e0e0e0', '#e0e0e0', '#e0e0e0', '#e0e0e0'];
                }
                const baseFontSize = window.innerWidth < 576 ? 10 : window.innerWidth < 992 ? 13 : 14;
                const barWidth = Math.round(baseFontSize * 0.32);
                const barHeight = Math.round(baseFontSize * 1.1);
                const barSpacing = Math.round(barWidth * 0.7);
                let barsX = window.innerWidth < 576 ? barStart - 28 : barStart - 43;
                let barsY = bar.y;
                for (let b = 0; b < 5; b++) {
                    ctx.beginPath();
                    const x = barsX + b * (barWidth + barSpacing);
                    const y = barsY - barHeight / 2;
                    const radius = barWidth / 2;
                    ctx.moveTo(x + radius, y);
                    ctx.lineTo(x + barWidth - radius, y);
                    ctx.quadraticCurveTo(x + barWidth, y, x + barWidth, y + radius);
                    ctx.lineTo(x + barWidth, y + barHeight - radius);
                    ctx.quadraticCurveTo(x + barWidth, y + barHeight, x + barWidth - radius, y + barHeight);
                    ctx.lineTo(x + radius, y + barHeight);
                    ctx.quadraticCurveTo(x, y + barHeight, x, y + barHeight - radius);
                    ctx.lineTo(x, y + radius);
                    ctx.quadraticCurveTo(x, y, x + radius, y);
                    ctx.closePath();
                    ctx.fillStyle = barColors[b];
                    ctx.fill();
                }
            }
            // Badges de desconto
            if (discount || (dataset.minDiscounts && dataset.minDiscounts[i] !== null)) {
                let badgeWidth = 36, badgeHeight = 16, badgeFont = 'bold 10px Segoe UI, Arial';
                if (window.innerWidth < 576) {
                    badgeWidth = 22;
                    badgeHeight = 11;
                    badgeFont = 'bold 7px Segoe UI, Arial';
                } else if (window.innerWidth < 992) {
                    badgeWidth = 28;
                    badgeHeight = 13;
                    badgeFont = 'bold 8px Segoe UI, Arial';
                }
                const minDiscount = dataset.minDiscounts ? dataset.minDiscounts[i] : null;
                const maxDiscount = dataset.maxDiscounts ? dataset.maxDiscounts[i] : null;
                const hasMultipleDiscounts = minDiscount !== null && maxDiscount !== null && minDiscount !== maxDiscount;
                if (hasMultipleDiscounts) {
                    let adjustedBadgeWidth;
                    let y = textY - badgeHeight / 2;
                    const maxText = `até -${maxDiscount}%`;
                    const textWidth = ctx.measureText(maxText).width;
                    adjustedBadgeWidth = Math.max(badgeWidth, textWidth + 16);
                    let x = chart.chartArea.right + 12;
                    ctx.fillStyle = '#dc3545';
                    ctx.beginPath();
                    ctx.moveTo(x + 6, y);
                    ctx.lineTo(x + adjustedBadgeWidth - 6, y);
                    ctx.quadraticCurveTo(x + adjustedBadgeWidth, y, x + adjustedBadgeWidth, y + 6);
                    ctx.lineTo(x + adjustedBadgeWidth, y + badgeHeight - 6);
                    ctx.quadraticCurveTo(x + adjustedBadgeWidth, y + badgeHeight, x + adjustedBadgeWidth - 6, y + badgeHeight);
                    ctx.lineTo(x + 6, y + badgeHeight);
                    ctx.quadraticCurveTo(x, y + badgeHeight, x, y + badgeHeight - 6);
                    ctx.lineTo(x, y + 6);
                    ctx.quadraticCurveTo(x, y, x + 6, y);
                    ctx.closePath();
                    ctx.fill();
                    ctx.font = badgeFont;
                    ctx.fillStyle = '#fff';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(maxText, x + adjustedBadgeWidth / 2, y + badgeHeight / 2);
                } else {
                    let x = chart.chartArea.right + 12;
                    let y = textY - badgeHeight / 2;
                    ctx.fillStyle = '#dc3545';
                    ctx.beginPath();
                    ctx.moveTo(x + 6, y);
                    ctx.lineTo(x + badgeWidth - 6, y);
                    ctx.quadraticCurveTo(x + badgeWidth, y, x + badgeWidth, y + 6);
                    ctx.lineTo(x + badgeWidth, y + badgeHeight - 6);
                    ctx.quadraticCurveTo(x + badgeWidth, y + badgeHeight, x + badgeWidth - 6, y + badgeHeight);
                    ctx.lineTo(x + 6, y + badgeHeight);
                    ctx.quadraticCurveTo(x, y + badgeHeight, x, y + badgeHeight - 6);
                    ctx.lineTo(x, y + 6);
                    ctx.quadraticCurveTo(x, y, x + 6, y);
                    ctx.closePath();
                    ctx.fill();
                    ctx.font = badgeFont;
                    ctx.fillStyle = '#fff';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(`-${discount}%`, x + badgeWidth / 2, y + badgeHeight / 2);
                }
            }
        });
        ctx.restore();
    }
};

function getSortedProducts(products, sortType) {
    let sorted = [...products];
    if (sortType === 'menor_preco') {
        sorted.sort((a, b) => (a.price ?? Infinity) - (b.price ?? Infinity));
    } else if (sortType === 'maior_preco') {
        sorted.sort((a, b) => (b.price ?? -Infinity) - (a.price ?? -Infinity));
    } else if (sortType === 'maior_desconto') {
        sorted.sort((a, b) => (b.discount_percentage ?? 0) - (a.discount_percentage ?? 0));
    } else { // relevancia
        sorted.sort((a, b) => (a.position ?? Infinity) - (b.position ?? Infinity));
    }
    return sorted;
}

function renderSortButtons(targetId, useWhiteBackground = false) {
    const baseClass = useWhiteBackground ? 'btn btn-light' : 'btn btn-outline-primary';
    return `
        <div class="sort-buttons-container ms-2" role="group" aria-label="Ordenar por">
            <button type="button" class="${baseClass} sort-btn${currentSort==='relevancia' ? ' active' : ''}" data-sort="relevancia">
                <span class="d-none d-md-inline">Relevância</span>
                <span class="d-none d-sm-inline d-md-none">Relev</span>
                <span class="d-inline d-sm-none">Rel</span>
            </button>
            <button type="button" class="${baseClass} sort-btn${currentSort==='menor_preco' ? ' active' : ''}" data-sort="menor_preco">
                <span class="d-none d-md-inline">Menor preço</span>
                <span class="d-none d-sm-inline d-md-none">Menor</span>
                <span class="d-inline d-sm-none">Min</span>
            </button>
            <button type="button" class="${baseClass} sort-btn${currentSort==='maior_preco' ? ' active' : ''}" data-sort="maior_preco">
                <span class="d-none d-md-inline">Maior preço</span>
                <span class="d-none d-sm-inline d-md-none">Maior</span>
                <span class="d-inline d-sm-none">Max</span>
            </button>
            <button type="button" class="${baseClass} sort-btn${currentSort==='maior_desconto' ? ' active' : ''}" data-sort="maior_desconto">
                <span class="d-none d-md-inline">Maior desconto</span>
                <span class="d-none d-sm-inline d-md-none">Desconto</span>
                <span class="d-inline d-sm-none">Desc</span>
            </button>
        </div>
    `;
}

function renderPagination(totalProducts, currentPage, productsPerPage) {
    const totalPages = Math.ceil(totalProducts / productsPerPage);
    if (totalPages <= 1) return '';
    
    let paginationHtml = '<div class="pagination-container mt-3 d-flex justify-content-center align-items-center">';
    paginationHtml += '<nav aria-label="Navegação de páginas">';
    paginationHtml += '<ul class="pagination pagination-sm mb-0">';
    
    // Botão Anterior
    if (currentPage > 1) {
        paginationHtml += `<li class="page-item"><button class="page-link" onclick="changePage(${currentPage - 1})">Anterior</button></li>`;
    } else {
        paginationHtml += `<li class="page-item disabled"><span class="page-link">Anterior</span></li>`;
    }
    
    // Números das páginas
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        paginationHtml += `<li class="page-item"><button class="page-link" onclick="changePage(1)">1</button></li>`;
        if (startPage > 2) {
            paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        if (i === currentPage) {
            paginationHtml += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
        } else {
            paginationHtml += `<li class="page-item"><button class="page-link" onclick="changePage(${i})">${i}</button></li>`;
        }
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
        paginationHtml += `<li class="page-item"><button class="page-link" onclick="changePage(${totalPages})">${totalPages}</button></li>`;
    }
    
    // Botão Próximo
    if (currentPage < totalPages) {
        paginationHtml += `<li class="page-item"><button class="page-link" onclick="changePage(${currentPage + 1})">Próximo</button></li>`;
    } else {
        paginationHtml += `<li class="page-item disabled"><span class="page-link">Próximo</span></li>`;
    }
    
    paginationHtml += '</ul>';
    paginationHtml += '</nav>';
    paginationHtml += '</div>';
    
    return paginationHtml;
}

function changePage(page) {
    currentPage = page;
    renderProductsAndChart(allProducts);
}

function attachSortButtonListeners(products, renderListFn, renderChartFn) {
    document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.onclick = function() {
            currentSort = this.getAttribute('data-sort');
            
            // Salvar estado atual da marca selecionada
            const currentSelectedBrand = selectedProduct ? selectedProduct.brand : null;
            const comparisonSection = document.getElementById('comparisonSection');
            const wasComparisonVisible = comparisonSection && comparisonSection.style.display !== 'none';
            
            // Salvar estado atual do filtro de farmácia
            const pharmacyFilter = document.getElementById('pharmacyFilter');
            currentPharmacyFilter = pharmacyFilter ? pharmacyFilter.value : '';
            
            // Não resetar página ao ordenar
            const originalCurrentPage = currentPage;
            
            renderListFn(products);
            if (renderChartFn) {
                renderChartFn(products);
            }
            
            // Restaurar página atual se estava em uma página > 1
            if (originalCurrentPage > 1) {
                currentPage = originalCurrentPage;
                // Re-aplicar a paginação correta
                const filteredProducts = currentPharmacyFilter && currentPharmacyFilter.trim() !== '' 
                    ? products.filter(product => product.pharmacy === currentPharmacyFilter)
                    : products;
                const sortedProducts = getSortedProducts(filteredProducts, currentSort);
                const totalProducts = sortedProducts.length;
                const totalPages = Math.ceil(totalProducts / productsPerPage);
                
                // Ajustar se a página atual é maior que o total de páginas
                if (currentPage > totalPages && totalPages > 0) {
                    currentPage = totalPages;
                }
                
                // Re-renderizar apenas a lista com a página correta
                const startIndex = (currentPage - 1) * productsPerPage;
                const endIndex = startIndex + productsPerPage;
                const currentPageProducts = sortedProducts.slice(startIndex, endIndex);
                
                // Renderizar produtos da página atual
                let productsHtml = '';
                currentPageProducts.forEach(product => {
                    const priceDisplay = typeof product.price === 'number' 
                        ? `R$ ${product.price.toFixed(2).replace('.', ',')}` 
                        : product.price;
                    const originalPriceDisplay = typeof product.original_price === 'number' 
                        ? `R$ ${product.original_price.toFixed(2).replace('.', ',')}` 
                        : product.original_price;
                    productsHtml += `
                        <div class="product-card" data-product-id="${product.name}">
                            <div class="row align-items-center g-2">
                                <div class="col-2 col-md-1">
                                    <div class="pharmacy-logo">
                                        ${product.pharmacy === 'Droga Raia' ? 
                                            '<img src="/static/logos/raia.png" alt="Raia Drogasil" title="Raia Drogasil" class="logo-img">' :
                                            product.pharmacy === 'São João' ?
                                            '<img src="/static/logos/sao_joao.png" alt="São João" title="São João" class="logo-img">' :
                                            `<i class="fas fa-store logo-icon" title="${product.pharmacy}" aria-label="${product.pharmacy}"></i>`
                                        }
                                    </div>
                                </div>
                                <div class="col-7 col-md-6">
                                    <h6 class="fw-bold mb-1 text-truncate">${product.name}</h6>
                                    <span class="brand-badge">${product.brand}</span>
                                    ${product.description ? `<p class="description-text mb-1 d-none d-md-block">${product.description}</p>` : ''}
                                </div>
                                <div class="col-3 col-md-5 text-end">
                                    <div class="price">${priceDisplay}</div>
                                    ${product.has_discount ? 
                                        `<div class="original-price">${originalPriceDisplay}</div>
                                         <span class="discount-badge">-${product.discount_percentage}%</span>` : ''
                                    }
                                    ${product.product_url ? 
                                        `<a href="${product.product_url}" target="_blank" class="btn btn-sm btn-outline-primary mt-2 d-none d-md-inline-block">
                                            <i class="fas fa-external-link-alt me-1"></i><span class="d-none d-lg-inline">Ver produto</span>
                                        </a>` : ''
                                    }
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                // Atualizar apenas a lista de produtos e paginação
                const productsListContainer = document.getElementById('productsList');
                if (productsListContainer) {
                    productsListContainer.innerHTML = productsHtml;
                }
                
                // Atualizar paginação
                const paginationContainer = document.querySelector('.pagination-container');
                if (paginationContainer) {
                    paginationContainer.outerHTML = renderPagination(totalProducts, currentPage, productsPerPage);
                }
                
                // Atualizar contador de produtos
                const badge = document.querySelector('.pharmacy-header .badge');
                if (badge) {
                    badge.innerHTML = `${totalProducts} produtos`;
                }
            }
            
            // Restaurar estado da marca selecionada se existia
            if (currentSelectedBrand) {
                selectedProduct = allProducts.find(p => p.brand === currentSelectedBrand);
                if (selectedProduct) {
                    // Atualizar seletor de marca
                    const brandSelect = document.getElementById('brandSelect');
                    if (brandSelect) {
                        brandSelect.value = currentSelectedBrand;
                    }
                    
                    // Manter análise comparativa visível
                    if (wasComparisonVisible) {
                        updatePositionComparison(false); // Usa cache quando ordenação é alterada
                        document.getElementById('comparisonSection').style.display = 'block';
                    }
                    
                    // Manter destaque dos cards
                    highlightAllProductsOfBrand();
                }
            }
            
            // O filtro de farmácia é restaurado automaticamente pelo setupPharmacyFilter
        };
    });
}

document.getElementById('searchForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const medicineDescription = document.getElementById('medicineInput').value.trim();
    if (!medicineDescription) {
        alert('Por favor, digite a descrição do medicamento.');
        return;
    }
    
    // Limpar cache de análises de IA para nova busca
    iaAnalysisCache = {};
    // Resetar página atual
    currentPage = 1;
    
    // Mostrar seção de resultados e loading
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    
    try {
        const response = await fetch('/api/pharma/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                medicine_description: medicineDescription
            })
        });
        
        const data = await response.json();
        console.log('Resposta do servidor:', data);
        console.log('Status da resposta:', response.ok);
        console.log('Tem results?', !!data.results);
        
        if (response.ok && data.results && Object.keys(data.results).length > 0) {
            displayResults(data);
        } else {
            displayError(data.error || 'Erro ao buscar medicamentos');
        }
        
    } catch (error) {
        console.error('Erro no fetch:', error);
        displayError('Erro de conexão. Tente novamente.');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
});

function displayResults(data) {
    console.log('Iniciando displayResults com data:', data);
    const resultsDiv = document.getElementById('results');
    
    // Criar estrutura HTML básica primeiro
    resultsDiv.innerHTML = `
        <!-- Estatísticas -->
        <div class="container-fluid px-0">
            <div class="row stats-row g-2 g-md-3" id="statsSection" style="display: none;">
                <div class="col-6 col-md-3">
                    <div class="stats-card text-center">
                        <div class="stats-number" id="totalBrands">0</div>
                        <div class="stats-label">Total de Marcas</div>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="stats-card text-center">
                        <div class="stats-number" id="minPrice">R$ 0,00</div>
                        <div class="stats-label">Menor Preço</div>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="stats-card text-center">
                        <div class="stats-number" id="avgPrice">R$ 0,00</div>
                        <div class="stats-label">Preço Médio</div>
                    </div>
                </div>
                <div class="col-6 col-md-3">
                    <div class="stats-card text-center">
                        <div class="stats-number" id="maxPrice">R$ 0,00</div>
                        <div class="stats-label">Maior Preço</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Seletor de Marca -->
        <div class="product-selector" id="brandSelector" style="display: none;">
            <h4><i class="fas fa-tags me-2"></i>Selecionar Marca para Análise</h4>
            <p class="text-muted">Escolha uma marca para ver a análise comparativa:</p>
            <div class="row">
                <div class="col-md-6">
                    <select id="brandSelect" class="form-select">
                        <option value="">Selecione uma marca...</option>
                    </select>
                </div>
            </div>
        </div>
        
        <!-- Gráfico de Preços por Marca -->
        <div class="chart-container mt-4" id="priceChartSection" style="display: none;">
            <h5><i class="fas fa-chart-bar me-2"></i>Preços por Marca (Menor para Maior)</h5>
            <div class="chart-wrapper">
                <canvas id="priceChart"></canvas>
            </div>
        </div>
        
        
        <!-- Análise Comparativa da Marca Selecionada -->
        <div class="comparison-highlight" id="comparisonSection" style="display: none;">
            <h5><i class="fas fa-chart-line me-2"></i>Análise Comparativa da Marca Selecionada</h5>
            <div id="positionInfo"></div>
        </div>
        
        <!-- Lista de Produtos -->
        <div id="productsList"></div>
    `;
    
    // Usar processed_results se disponível, senão usar results
    const results = data.processed_results || data.results;
    console.log('Results:', results);
    let hasResults = false;
    allProducts = [];
    
    // Primeiro, coletar todos os produtos e erros
    let allProductsList = [];
    let errorsList = [];
    
    for (const [pharmacyKey, pharmacyData] of Object.entries(results)) {
        if (pharmacyData.error) {
            // Adicionar erro à lista
            errorsList.push({
                pharmacy: pharmacyData.pharmacy || pharmacyKey,
                error: pharmacyData.error
            });
        } else if (pharmacyData.products && pharmacyData.products.length > 0) {
            console.log(`Processando ${pharmacyData.products.length} produtos de ${pharmacyData.pharmacy}`);
            hasResults = true;
            
            // Adicionar produtos à lista global
            pharmacyData.products.forEach(product => {
                allProducts.push({
                    ...product,
                    pharmacy: pharmacyData.pharmacy
                });
                
                // Adicionar à lista de produtos para exibição
                allProductsList.push({
                    ...product,
                    pharmacy: pharmacyData.pharmacy
                });
            });
        }
    }
    
    // Mostrar erros primeiro (se houver)
    errorsList.forEach(errorData => {
        resultsDiv.innerHTML += `
            <div class="pharmacy-card">
                <div class="pharmacy-header">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${errorData.pharmacy}
                </div>
                <div class="p-3">
                    <div class="error-message">
                        ${errorData.error}
                    </div>
                </div>
            </div>
        `;
    });
    
    // Mostrar lista única de produtos (se houver)
    if (allProductsList.length > 0) {
        renderProductsAndChart(allProductsList);
    }
    
    console.log('hasResults:', hasResults);
    if (!hasResults) {
        console.log('Nenhum resultado encontrado');
        resultsDiv.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h4>Nenhum resultado encontrado</h4>
                <p class="text-muted">Tente ajustar os termos da busca</p>
            </div>
        `;
    } else {
        console.log('Mostrando resultados e gráficos');
        try {
            // Não chame mais updateStatistics() ou createPriceChart() aqui
            // Tudo é feito por renderProductsAndChart
            // showBrandSelector(); // Removido
        } catch (error) {
            console.error('Erro ao mostrar resultados:', error);
            displayError('Erro ao processar resultados: ' + error.message);
        }
    }
    
    resultsDiv.style.display = 'block';
}

function showBrandSelector() {
    console.log('Iniciando showBrandSelector');
    
    // Verificar se já foi inicializado
    const brandSelect = document.getElementById('brandSelect');
    if (brandSelect.getAttribute('data-initialized') === 'true') {
        console.log('BrandSelector já foi inicializado, pulando...');
        return;
    }
    
    // Obter marcas únicas
    const uniqueBrands = [...new Set(allProducts.map(p => p.brand))];
    
    // Limpar opções existentes
    brandSelect.innerHTML = '<option value="">Selecione uma marca...</option>';
    
    // Adicionar opções
    uniqueBrands.forEach(brand => {
        const option = document.createElement('option');
        option.value = brand;
        option.textContent = brand;
        brandSelect.appendChild(option);
    });
    
    // Adicionar event listener (só uma vez)
    brandSelect.addEventListener('change', function() {
        const selectedBrand = this.value;
                    if (selectedBrand) {
                // Encontrar o primeiro produto da marca selecionada
                selectedProduct = allProducts.find(p => p.brand === selectedBrand);
                renderPriceChart(allProducts);
                updatePositionComparison(true); // Força nova análise quando marca é selecionada
                highlightAllProductsOfBrand();
            } else {
                selectedProduct = null;
                renderPriceChart(allProducts);
                document.getElementById('comparisonSection').style.display = 'none';
                // Remover destaque na lista de produtos
                document.querySelectorAll('.product-card.destaque-produto').forEach(el => {
                    el.classList.remove('destaque-produto');
                });
            }
    });
    
    // Marcar como inicializado
    brandSelect.setAttribute('data-initialized', 'true');
    
    document.getElementById('brandSelector').style.display = 'block';
}

function updatePriceChart() {
    if (priceChart) {
        // Recalcular dados do gráfico
        const brandData = {};
        allProducts.forEach(product => {
            if (typeof product.price === 'number' && product.price > 0) {
                if (brandData[product.brand]) {
                    brandData[product.brand].prices.push(product.price);
                } else {
                    brandData[product.brand] = {
                        prices: [product.price],
                        count: 1
                    };
                }
            }
        });
        
        const sortedBrands = Object.entries(brandData)
            .map(([brand, data]) => ({
                brand: brand,
                minPrice: Math.min(...data.prices),
                count: data.prices.length,
                maxDiscount: Math.max(...data.prices) - Math.min(...data.prices),
                minDiscount: Math.min(...data.prices),
                hasMultipleDiscounts: Math.max(...data.prices) !== Math.min(...data.prices),
                minPosition: Math.min(...allProducts.filter(p => p.brand === brand).map(p => p.position ?? Infinity))
            }))
            .sort((a, b) => a.minPrice - b.minPrice);
        
        priceChart.data.labels = sortedBrands.map(b => b.brand);
        priceChart.data.datasets[0].data = sortedBrands.map(b => b.minPrice);
        priceChart.data.datasets[0].backgroundColor = sortedBrands.map(b => 
            selectedProduct && b.brand === selectedProduct.brand ? '#1e3a8a' : 
            selectedProduct ? '#a8b4e6' : '#667eea'
        );
        priceChart.data.datasets[0].borderColor = sortedBrands.map(b => 
            selectedProduct && b.brand === selectedProduct.brand ? '#1e3a8a' : 
            selectedProduct ? '#a8b4e6' : '#667eea'
        );
        const isMobile = window.innerWidth < 576;
        const isTablet = window.innerWidth >= 576 && window.innerWidth < 992;
        priceChart.data.datasets[0].borderWidth = isMobile ? 0 : isTablet ? 0.8 : 1;
        priceChart.update('none'); // Desabilita animações na atualização
    }
    // Sempre remover destaque da lista de produtos ao atualizar gráfico sem seleção
    if (!selectedProduct) {
        document.querySelectorAll('.product-card.destaque-produto').forEach(el => {
            el.classList.remove('destaque-produto');
        });
    }
}

async function updatePositionComparison(forceNewAnalysis = false) {
    if (!selectedProduct) return;
    
    // Calcular estatísticas por marca
    const brandData = {};
    allProducts.forEach(product => {
        if (typeof product.price === 'number' && product.price > 0) {
            if (brandData[product.brand]) {
                brandData[product.brand].prices.push(product.price);
            } else {
                brandData[product.brand] = {
                    prices: [product.price]
                };
            }
        }
    });
    
    // Calcular preço médio por marca
    const brandAverages = Object.entries(brandData).map(([brand, data]) => ({
        brand: brand,
        avgPrice: data.prices.reduce((a, b) => a + b, 0) / data.prices.length,
        prices: data.prices // Adicionado para evitar erro de undefined
    }));
    
    const selectedBrandAvg = brandAverages.find(b => b.brand === selectedProduct.brand);
    const sortedBrands = brandAverages.sort((a, b) => a.avgPrice - b.avgPrice);
    const position = sortedBrands.findIndex(b => b.brand === selectedProduct.brand) + 1;
    const totalBrands = sortedBrands.length;
    
    let positionClass = 'position-similar';
    let positionText = 'Preço similar';
    
    if (position <= Math.ceil(totalBrands * 0.3)) {
        positionClass = 'position-better';
        positionText = 'Entre as mais baratas';
    } else if (position >= Math.ceil(totalBrands * 0.7)) {
        positionClass = 'position-worse';
        positionText = 'Entre as mais caras';
    }
    
    const avgAllBrands = brandAverages.reduce((sum, b) => sum + b.avgPrice, 0) / brandAverages.length;
    const priceDiff = selectedBrandAvg.avgPrice - avgAllBrands;
    const priceDiffText = priceDiff > 0 ? `+R$ ${priceDiff.toFixed(2)}` : `-R$ ${Math.abs(priceDiff).toFixed(2)}`;
    
    // Calcular número de farmácias onde a marca foi encontrada
    const brandProducts = allProducts.filter(p => p.brand === selectedProduct.brand);
    const uniquePharmacies = [...new Set(brandProducts.map(p => p.pharmacy))];
    const pharmacyCount = uniquePharmacies.length;
    
    // Calcular maior e menor preço da marca
    const brandPrices = brandProducts.map(p => p.price).filter(price => typeof price === 'number' && price > 0);
    const minPrice = Math.min(...brandPrices);
    const maxPrice = Math.max(...brandPrices);
    
    // Identificar farmácias analisadas
    const pharmaciesAnalyzed = [...new Set(allProducts.map(p => p.pharmacy))];
    
    // Preparar dados de TODOS os produtos para enviar à IA
    const allProductsData = allProducts.map(product => ({
        name: product.name,
        pharmacy: product.pharmacy,
        price: product.price,
        original_price: product.original_price,
        has_discount: product.has_discount,
        discount_percentage: product.discount_percentage,
        position: product.position,
        brand: product.brand
    }));

    // Calcular a moda das posições para a marca (mesmo cálculo do gráfico)
    const allBrandProducts = allProducts.filter(p => p.brand === selectedProduct.brand);
    const positions = allBrandProducts.map(p => p.position).filter(pos => pos !== null && pos !== undefined);
    let moda = null;
    if (positions.length > 0) {
        const freq = {};
        positions.forEach(pos => { freq[pos] = (freq[pos] || 0) + 1; });
        const maxFreq = Math.max(...Object.values(freq));
        const modaCandidates = Object.keys(freq).filter(pos => freq[pos] === maxFreq).map(Number);
        moda = Math.floor(Math.min(...modaCandidates)); // arredonda para baixo se empate
    }
    
    // Gerar cards para cada farmácia
    let pharmacyCardsHtml = '';
    allBrandProducts.forEach(product => {
        // Encontrar produtos da mesma farmácia para comparação
        const pharmacyProducts = allProducts.filter(p => p.pharmacy === product.pharmacy);
        
        // Contar produtos da marca selecionada nesta farmácia
        const brandProductsInPharmacy = pharmacyProducts.filter(p => p.brand === selectedProduct.brand);
        const productCount = brandProductsInPharmacy.length;
        
        // Encontrar produto mais barato da farmácia
        const cheapestProduct = pharmacyProducts.reduce((cheapest, current) => {
            if (typeof current.price === 'number' && current.price > 0) {
                if (!cheapest || current.price < cheapest.price) {
                    return current;
                }
            }
            return cheapest;
        }, null);
        
        // Encontrar produto melhor posicionado da farmácia
        const bestPositionedProduct = pharmacyProducts.reduce((best, current) => {
            if (current.position && current.position > 0) {
                if (!best || current.position < best.position) {
                    return current;
                }
            }
            return best;
        }, null);
        
        // Verificar se há produto mais barato e melhor posicionado
        const hasBetterOption = cheapestProduct && bestPositionedProduct && 
                               cheapestProduct.brand !== product.brand && 
                               bestPositionedProduct.brand !== product.brand &&
                               cheapestProduct.price < product.price &&
                               bestPositionedProduct.position < product.position;
        
        // Definir cor do badge baseada na posição específica daquele produto naquela farmácia
        let positionBadgeClass = 'bg-secondary'; // padrão cinza
        const productPosition = product.position;
        if (productPosition === 1) {
            positionBadgeClass = 'bg-warning text-dark'; // dourado
        } else if (productPosition === 2) {
            positionBadgeClass = 'bg-info text-white'; // azul claro
        } else if (productPosition === 3) {
            positionBadgeClass = 'bg-danger text-white'; // bronze/vermelho
        } else if (productPosition === 4 || productPosition === 5) {
            positionBadgeClass = 'bg-dark text-white'; // cinza escuro
        } else if (productPosition > 5) {
            positionBadgeClass = 'bg-secondary text-white'; // cinza claro
        }
        
        const priceDisplay = typeof product.price === 'number' 
            ? `R$ ${product.price.toFixed(2).replace('.', ',')}` 
            : product.price;
        const originalPriceDisplay = typeof product.original_price === 'number' 
            ? `R$ ${product.original_price.toFixed(2).replace('.', ',')}` 
            : product.original_price;
        
        pharmacyCardsHtml += `
            <div class="col-12 col-md-4 col-lg-3 mb-2">
                <div class="card pharmacy-detail-card ${hasBetterOption ? 'border-warning' : ''}">
                    <div class="card-header d-flex align-items-center">
                        <div class="pharmacy-logo me-1">
                            ${product.pharmacy === 'Droga Raia' ? 
                                '<img src="/static/logos/raia.png" alt="Raia Drogasil" title="Raia Drogasil" class="logo-img" style="width: 32px; height: 32px;">' :
                                product.pharmacy === 'São João' ?
                                '<img src="/static/logos/sao_joao.png" alt="São João" title="São João" class="logo-img" style="width: 32px; height: 32px;">' :
                                `<i class="fas fa-store logo-icon" style="font-size: 32px; color: #fff;" title="${product.pharmacy}" aria-label="${product.pharmacy}"></i>`
                            }
                        </div>
                        <strong class="pharmacy-name">${product.pharmacy}</strong>
                        ${hasBetterOption ? '<span class="badge bg-warning text-dark ms-auto"><i class="fas fa-exclamation-triangle"></i></span>' : ''}
                    </div>
                    <div class="card-body">
                        <div class="row g-1 mb-1">
                            <div class="col-6">
                                <small class="text-muted">Preço:</small><br>
                                <strong class="text-primary price-text">${priceDisplay}</strong>
                            </div>
                            <div class="col-6">
                                <small class="text-muted">Posição:</small><br>
                                <span class="badge ${positionBadgeClass}">${product.position || 'N/A'}</span>
                            </div>
                        </div>
                        <div class="row g-1 mb-1">
                            <div class="col-12">
                                <small class="text-muted">Produtos encontrados:</small><br>
                                <span class="badge bg-info">${productCount} produto${productCount > 1 ? 's' : ''}</span>
                            </div>
                        </div>
                        ${product.has_discount ? `
                            <div class="row g-1 mb-1">
                                <div class="col-6">
                                    <small class="text-muted">Original:</small><br>
                                    <span class="text-decoration-line-through text-muted small">${originalPriceDisplay}</span>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">Desconto:</small><br>
                                    <span class="badge bg-success">-${product.discount_percentage}%</span>
                                </div>
                            </div>
                        ` : ''}
                        ${hasBetterOption ? `
                            <div class="alert alert-warning alert-sm mt-1 mb-0">
                                <small>
                                    <i class="fas fa-info-circle me-1"></i>
                                    <strong>${cheapestProduct.brand}</strong> mais barata<br>
                                    <strong>${bestPositionedProduct.brand}</strong> melhor posição
                                </small>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    });

    // Renderizar interface com spinner primeiro
    if (!selectedProduct) {
        document.getElementById('positionInfo').innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-hand-pointer fa-2x mb-2"></i><br>
                Selecione uma marca para ver a análise comparativa.
            </div>
        `;
    } else {
        document.getElementById('positionInfo').innerHTML = `
            <div class="row g-3 mb-4">
                <div class="col-12 col-md-6">
                    <strong>${selectedProduct.brand}</strong><br>
                    <span class="position-indicator ${positionClass}">${positionText}</span><br>
                    <small>${selectedBrandAvg.prices.length} produtos encontrados em ${pharmacyCount} farmácia${pharmacyCount > 1 ? 's' : ''}</small>
                </div>
                <div class="col-12 col-md-6">
                    <strong>Preço médio: R$ ${selectedBrandAvg.avgPrice.toFixed(2).replace('.', ',')}</strong><br>
                    <small><i class="fas fa-arrow-down text-success me-1"></i>Menor: R$ ${minPrice.toFixed(2).replace('.', ',')} | <i class="fas fa-arrow-up text-danger me-1"></i>Maior: R$ ${maxPrice.toFixed(2).replace('.', ',')}</small><br>
                    <small>${priceDiffText} em relação à média geral</small>
                </div>
            </div>
            <div class="ia-analysis-section">
                <h6 class="mb-3"><i class="fas fa-magic me-2"></i>Análise Inteligente</h6>
                <div class="ia-loading text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Carregando análise...</span>
                    </div>
                    <p class="mt-2 text-muted">Gerando análise inteligente...</p>
                </div>
            </div>
            <h6 class="mb-3"><i class="fas fa-store me-2"></i>Detalhes por Farmácia</h6>
            <div class="row g-2">
                ${pharmacyCardsHtml}
            </div>
        `;
    }
    
    document.getElementById('comparisonSection').style.display = 'block';
    document.querySelector('#comparisonSection h5').innerHTML = '<i class="fas fa-chart-line me-2"></i>Análise Comparativa';

    // Verificar se já temos análise em cache para esta marca
    const brandKey = selectedProduct.brand;
    let iaAnalysis = '';
    
    if (!forceNewAnalysis && iaAnalysisCache[brandKey]) {
        // Usar análise em cache
        iaAnalysis = iaAnalysisCache[brandKey];
        console.log('Usando análise em cache para:', brandKey);
    } else {
        // Gerar nova análise com IA
        try {
            const requestData = {
                brand: selectedProduct.brand,
                position: position,
                total_brands: totalBrands,
                avg_price: selectedBrandAvg.avgPrice,
                min_price: minPrice,
                max_price: maxPrice,
                pharmacy_count: pharmacyCount,
                price_diff_text: priceDiffText,
                pharmacies_analyzed: pharmaciesAnalyzed,
                products_data: allProductsData
            };
            
            console.log('Dados enviados para IA:', requestData);
            console.log('Total de produtos enviados:', allProductsData.length);
            
            const response = await fetch('/api/pharma/ia/brand-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            if (data.success) {
                iaAnalysis = `<div class="ia-summary alert alert-info mb-3"><i class="fas fa-robot me-1"></i>${data.analysis}</div>`;
                // Salvar no cache
                iaAnalysisCache[brandKey] = iaAnalysis;
                console.log('Análise salva em cache para:', brandKey);
            } else {
                console.error('Erro na análise de IA:', data.error);
                iaAnalysis = `<div class="ia-summary alert alert-warning mb-3"><i class="fas fa-exclamation-triangle me-1"></i>Não foi possível gerar a análise inteligente. Erro: ${data.error}</div>`;
            }
        } catch (error) {
            console.error('Erro ao chamar API de IA:', error);
            iaAnalysis = `<div class="ia-summary alert alert-warning mb-3"><i class="fas fa-exclamation-triangle me-1"></i>Erro de conexão com o serviço de IA. Tente novamente.</div>`;
        }
    }

    // Atualizar a seção de análise com o resultado
    const iaSection = document.querySelector('.ia-analysis-section');
    if (iaSection) {
        iaSection.innerHTML = `
            <h6 class="mb-3"><i class="fas fa-magic me-2"></i>Análise Inteligente</h6>
            <div class="ia-summary ia-summary-modern mb-3">${iaAnalysis.replace(/<i class=\"fas fa-robot[^>]*><\/i>/g, '').replace(/<i class=\"fas fa-brain[^>]*><\/i>/g, '').replace(/<i class=\"fas fa-sparkles[^>]*><\/i>/g, '')}</div>
        `;
    }
    
    document.getElementById('comparisonSection').style.display = 'block';
}

function highlightAllProductsOfBrand() {
    // Remover destaque anterior
    document.querySelectorAll('.product-card.destaque-produto').forEach(el => {
        el.classList.remove('destaque-produto');
    });
    if (!selectedProduct) return;
    
    // Encontrar todos os cards de produtos da marca selecionada
    const cards = document.querySelectorAll('.pharmacy-card');
    for (const card of cards) {
        const productCards = card.querySelectorAll('.product-card');
        for (const prodCard of productCards) {
            // Checar se é da marca selecionada
            const brandBadge = prodCard.querySelector('.brand-badge');
            if (brandBadge && brandBadge.textContent === selectedProduct.brand) {
                prodCard.classList.add('destaque-produto');
            }
        }
    }
}

function displayError(message) {
    console.log('displayError chamada com:', message);
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
        </div>
    `;
    resultsDiv.style.display = 'block';
} 

function renderProductsAndChart(products, preservePage = false) {
    const resultsDiv = document.getElementById('results');
    
    // Aplicar filtro de farmácia se necessário
    let filteredProducts = products;
    if (currentPharmacyFilter && currentPharmacyFilter.trim() !== '') {
        filteredProducts = products.filter(product => product.pharmacy === currentPharmacyFilter);
    }
    // --- INÍCIO: Filtro por Marca ---
    if (window.currentBrandFilter && window.currentBrandFilter.trim() !== '') {
        filteredProducts = filteredProducts.filter(product => product.brand === window.currentBrandFilter);
    }
    // --- FIM: Filtro por Marca ---
    
    // Ordenar produtos
    const sortedProducts = getSortedProducts(filteredProducts, currentSort);
    
    // Calcular paginação
    const totalProducts = sortedProducts.length;
    const totalPages = Math.ceil(totalProducts / productsPerPage);
    
    // Ajustar página atual se necessário
    if (currentPage > totalPages && totalPages > 0) {
        currentPage = totalPages;
    }
    
    // Obter produtos da página atual
    const startIndex = (currentPage - 1) * productsPerPage;
    const endIndex = startIndex + productsPerPage;
    const currentPageProducts = sortedProducts.slice(startIndex, endIndex);
    
    // Renderizar produtos da página atual
    let productsHtml = '';
    currentPageProducts.forEach(product => {
        const priceDisplay = typeof product.price === 'number' 
            ? `R$ ${product.price.toFixed(2).replace('.', ',')}` 
            : product.price;
        const originalPriceDisplay = typeof product.original_price === 'number' 
            ? `R$ ${product.original_price.toFixed(2).replace('.', ',')}` 
            : product.original_price;
        productsHtml += `
            <div class="product-card" data-product-id="${product.name}">
                <div class="row align-items-center g-2">
                    <div class="col-2 col-md-1">
                        <div class="pharmacy-logo">
                            ${product.pharmacy === 'Droga Raia' ? 
                                '<img src="/static/logos/raia.png" alt="Raia Drogasil" title="Raia Drogasil" class="logo-img">' :
                                product.pharmacy === 'São João' ?
                                '<img src="/static/logos/sao_joao.png" alt="São João" title="São João" class="logo-img">' :
                                `<i class="fas fa-store logo-icon" title="${product.pharmacy}" aria-label="${product.pharmacy}"></i>`
                            }
                        </div>
                    </div>
                    <div class="col-7 col-md-6">
                        <h6 class="fw-bold mb-1 text-truncate">${product.name}</h6>
                        <span class="brand-badge">${product.brand}</span>
                        ${product.description ? `<p class="description-text mb-1 d-none d-md-block">${product.description}</p>` : ''}
                    </div>
                    <div class="col-3 col-md-5 text-end">
                        <div class="price">${priceDisplay}</div>
                        ${product.has_discount ? 
                            `<div class="original-price">${originalPriceDisplay}</div>
                             <span class="discount-badge">-${product.discount_percentage}%</span>` : ''
                        }
                        ${product.product_url ? 
                            `<a href="${product.product_url}" target="_blank" class="btn btn-sm btn-outline-primary mt-2 d-none d-md-inline-block">
                                <i class="fas fa-external-link-alt me-1"></i><span class="d-none d-lg-inline">Ver produto</span>
                            </a>` : ''
                        }
                    </div>
                </div>
            </div>
        `;
    });
    resultsDiv.innerHTML = `
        <div class="product-selector" id="brandSelector">
            <h4><i class="fas fa-tags me-2"></i>Selecionar Marca para Análise</h4>
            <p class="text-muted">Escolha uma marca para ver a análise comparativa:</p>
            <div class="row">
                <div class="col-md-6">
                    <select id="brandSelect" class="form-select">
                        <option value="">Selecione uma marca...</option>
                    </select>
                </div>
            </div>
        </div>
        <div class="chart-container mt-4" id="chartsSection">
            <div class="d-flex flex-column flex-md-row align-items-start align-items-md-center justify-content-between mb-3">
                <h5 class="mb-2 mb-md-0"><i class="fas fa-chart-bar me-2"></i>Análise Comparativa</h5>
                <div class="d-flex flex-wrap justify-content-center justify-content-md-end">
                    ${renderSortButtons('chartsSection')}
                </div>
            </div>
            <div class="row g-3">
                <div class="col-12">
                    <h6 class="text-center mb-3"><i class="fas fa-chart-bar me-2"></i>Preços por Marca</h6>
                    <div class="chart-wrapper">
                        <canvas id="priceChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        <div class="comparison-highlight" id="comparisonSection" style="display: none;">
            <h5><i class="fas fa-chart-line me-2"></i>Análise Comparativa da Marca Selecionada</h5>
            <div id="positionInfo"></div>
        </div>
        <div class="pharmacy-card">
            <div class="pharmacy-header d-flex flex-column flex-md-row align-items-start align-items-md-center justify-content-between">
                <div class="d-flex align-items-center mb-2 mb-md-0">
                    <i class="fas fa-list me-2"></i>Lista de Produtos 
                    <span class="badge bg-light text-dark ms-2">
                        ${totalProducts} produtos
                    </span>
                    <button type="button" class="btn btn-success btn-sm ms-2 ms-md-3" onclick="downloadExcel()">
                        <i class="fas fa-download me-1"></i><span class="d-none d-sm-inline">Exportar Excel</span>
                    </button>
                </div>
                <div class="d-flex align-items-center justify-content-center justify-content-md-end">
                    ${renderSortButtons('productsList', true)}
                </div>
            </div>
            <div class="p-3">
                <div class="row g-3 mb-3">
                    <div class="col-md-4">
                        <label for="pharmacyFilter" class="form-label"><i class="fas fa-filter me-1"></i>Filtrar por Farmácia</label>
                        <select id="pharmacyFilter" class="form-select">
                            <option value="">Todas as farmácias</option>
                        </select>
                    </div>
                    <!-- INÍCIO: Filtro por Marca -->
                    <div class="col-md-4">
                        <label for="brandFilter" class="form-label"><i class="fas fa-filter me-1"></i>Filtrar por Marca</label>
                        <select id="brandFilter" class="form-select">
                            <option value="">Todas as marcas</option>
                        </select>
                    </div>
                    <!-- FIM: Filtro por Marca -->
                </div>
                <div id="productsList">
                    ${productsHtml}
                </div>
                ${renderPagination(totalProducts, currentPage, productsPerPage)}
            </div>
        </div>
    `;
    attachSortButtonListeners(products, renderProductsAndChart, renderPriceChart);
    setTimeout(() => {
        renderPriceChart(products);
        showBrandSelector();
        // Só configurar o filtro se não existir ainda
        const pharmacyFilter = document.getElementById('pharmacyFilter');
        if (!pharmacyFilter || pharmacyFilter.options.length <= 1) {
            setupPharmacyFilter(products);
        }
        // INÍCIO: Configurar filtro por Marca
        const brandFilter = document.getElementById('brandFilter');
        if (!brandFilter || brandFilter.options.length <= 1) {
            setupBrandFilter(products);
        }
        // FIM: Configurar filtro por Marca
    }, 0);

    // Atualizar estatísticas e gráfico de preços após a renderização
    // updateStatistics(); // Removido
    // createPriceChart(); // Removido
}

function setupPharmacyFilter(products) {
    // Obter farmácias únicas
    const uniquePharmacies = [...new Set(products.map(p => p.pharmacy))];
    const pharmacyFilter = document.getElementById('pharmacyFilter');
    
    // Limpar opções existentes (exceto a primeira)
    pharmacyFilter.innerHTML = '<option value="">Todas as farmácias</option>';
    
    // Adicionar opções de farmácias
    uniquePharmacies.forEach(pharmacy => {
        const option = document.createElement('option');
        option.value = pharmacy;
        option.textContent = pharmacy;
        pharmacyFilter.appendChild(option);
    });
    
    // Restaurar valor da variável global se ainda for válido
    if (currentPharmacyFilter && currentPharmacyFilter.trim() !== '' && uniquePharmacies.includes(currentPharmacyFilter)) {
        pharmacyFilter.value = currentPharmacyFilter;
        filterProductsByPharmacy(currentPharmacyFilter, products);
    }
    
    // Adicionar event listener para filtro (só se não existir)
    const existingListeners = pharmacyFilter.getAttribute('data-has-listener');
    if (!existingListeners) {
        pharmacyFilter.addEventListener('change', function() {
            const selectedPharmacy = this.value;
            filterProductsByPharmacy(selectedPharmacy, products);
        });
        pharmacyFilter.setAttribute('data-has-listener', 'true');
    }
}

function filterProductsByPharmacy(selectedPharmacy, allProducts) {
    // Atualizar filtro global
    currentPharmacyFilter = selectedPharmacy;
    
    // Resetar página para 1 quando filtro é alterado
    currentPage = 1;
    
    // Se não há filtro aplicado (Todas as farmácias), re-renderizar tudo
    if (!selectedPharmacy || selectedPharmacy.trim() === '') {
        renderProductsAndChart(allProducts);
        return;
    }
    
    // Re-renderizar apenas a lista de produtos sem re-inicializar componentes
    const resultsDiv = document.getElementById('results');
    
    // Aplicar filtro de farmácia
    const filteredProducts = allProducts.filter(product => product.pharmacy === selectedPharmacy);
    
    // Ordenar produtos
    const sortedProducts = getSortedProducts(filteredProducts, currentSort);
    
    // Calcular paginação
    const totalProducts = sortedProducts.length;
    const totalPages = Math.ceil(totalProducts / productsPerPage);
    
    // Ajustar página atual se necessário
    if (currentPage > totalPages && totalPages > 0) {
        currentPage = totalPages;
    }
    
    // Obter produtos da página atual
    const startIndex = (currentPage - 1) * productsPerPage;
    const endIndex = startIndex + productsPerPage;
    const currentPageProducts = sortedProducts.slice(startIndex, endIndex);
    
    // Renderizar produtos da página atual
    let productsHtml = '';
    currentPageProducts.forEach(product => {
        const priceDisplay = typeof product.price === 'number' 
            ? `R$ ${product.price.toFixed(2).replace('.', ',')}` 
            : product.price;
        const originalPriceDisplay = typeof product.original_price === 'number' 
            ? `R$ ${product.original_price.toFixed(2).replace('.', ',')}` 
            : product.original_price;
        productsHtml += `
            <div class="product-card" data-product-id="${product.name}">
                <div class="row align-items-center g-2">
                    <div class="col-2 col-md-1">
                        <div class="pharmacy-logo">
                            ${product.pharmacy === 'Droga Raia' ? 
                                '<img src="/static/logos/raia.png" alt="Raia Drogasil" title="Raia Drogasil" class="logo-img">' :
                                product.pharmacy === 'São João' ?
                                '<img src="/static/logos/sao_joao.png" alt="São João" title="São João" class="logo-img">' :
                                `<i class="fas fa-store logo-icon" title="${product.pharmacy}" aria-label="${product.pharmacy}"></i>`
                            }
                        </div>
                    </div>
                    <div class="col-7 col-md-6">
                        <h6 class="fw-bold mb-1 text-truncate">${product.name}</h6>
                        <span class="brand-badge">${product.brand}</span>
                        ${product.description ? `<p class="description-text mb-1 d-none d-md-block">${product.description}</p>` : ''}
                    </div>
                    <div class="col-3 col-md-5 text-end">
                        <div class="price">${priceDisplay}</div>
                        ${product.has_discount ? 
                            `<div class="original-price">${originalPriceDisplay}</div>
                             <span class="discount-badge">-${product.discount_percentage}%</span>` : ''
                        }
                        ${product.product_url ? 
                            `<a href="${product.product_url}" target="_blank" class="btn btn-sm btn-outline-primary mt-2 d-none d-md-inline-block">
                                <i class="fas fa-external-link-alt me-1"></i><span class="d-none d-lg-inline">Ver produto</span>
                            </a>` : ''
                        }
                    </div>
                </div>
            </div>
        `;
    });
    
    // Atualizar apenas a lista de produtos e paginação
    const productsListContainer = document.getElementById('productsList');
    if (productsListContainer) {
        productsListContainer.innerHTML = productsHtml;
    }
    
    // Atualizar paginação
    const paginationContainer = document.querySelector('.pagination-container');
    if (paginationContainer) {
        paginationContainer.outerHTML = renderPagination(totalProducts, currentPage, productsPerPage);
    }
    
    // Atualizar contador de produtos
    const badge = document.querySelector('.pharmacy-header .badge');
    if (badge) {
        badge.innerHTML = `${totalProducts} produtos`;
    }
}

function renderPriceChart(products) {
    // Agrupar produtos por marca e calcular preço mínimo e máximo por marca
    const brandData = {};
    products.forEach(product => {
        if (typeof product.price === 'number' && product.price > 0) {
            if (brandData[product.brand]) {
                brandData[product.brand].prices.push(product.price);
            } else {
                brandData[product.brand] = {
                    prices: [product.price],
                    count: 1
                };
            }
        }
    });
    // Calcular preços mínimo e máximo por marca e ordenar conforme o sort
    let sortedBrands = Object.entries(brandData)
        .map(([brand, data]) => {
            const brandProducts = allProducts.filter(p => p.brand === brand);
            const discounts = brandProducts.map(p => p.discount_percentage || 0);
            const maxDiscount = discounts.length > 0 ? Math.max(...discounts) : 0;
            const minDiscount = discounts.length > 0 ? Math.min(...discounts) : 0;
            const minPrice = Math.min(...data.prices);
            const maxPrice = Math.max(...data.prices);
            return {
                brand: brand,
                minPrice: minPrice,
                maxPrice: maxPrice,
                count: data.prices.length,
                maxDiscount: maxDiscount,
                minDiscount: minDiscount,
                hasMultipleDiscounts: maxDiscount !== minDiscount,
                minPosition: Math.min(...allProducts.filter(p => p.brand === brand).map(p => p.position ?? Infinity))
            };
        });
    if (currentSort === 'menor_preco') {
        sortedBrands.sort((a, b) => a.minPrice - b.minPrice);
    } else if (currentSort === 'maior_preco') {
        sortedBrands.sort((a, b) => b.minPrice - a.minPrice);
    } else if (currentSort === 'maior_desconto') {
        sortedBrands.sort((a, b) => b.maxDiscount - a.maxDiscount);
    } else { // relevancia
        sortedBrands.sort((a, b) => {
            const posA = Math.min(...allProducts.filter(p => p.brand === a.brand).map(p => p.position ?? Infinity));
            const posB = Math.min(...allProducts.filter(p => p.brand === b.brand).map(p => p.position ?? Infinity));
            return posA - posB;
        });
    }

    // --- NOVO: Ajuste responsivo e altura via CSS ---
    const isMobile = window.innerWidth < 576;
    const isTablet = window.innerWidth >= 576 && window.innerWidth < 992;
    const barCount = sortedBrands.length;
    const chartWrapper = document.getElementById('priceChart').parentElement;
    if (isMobile) {
        chartWrapper.style.minHeight = `${Math.max(32 * barCount, 120)}px`;
    } else if (isTablet) {
        chartWrapper.style.minHeight = `${Math.max(40 * barCount, 180)}px`;
    } else {
        chartWrapper.style.minHeight = `${Math.max(40 * barCount, 200)}px`;
    }

    // Espessura e espaçamento das barras
    let barThickness = isMobile ? 22 : isTablet ? 22 : 22;
    let maxBarThickness = isMobile ? 28 : isTablet ? 28 : 28;
    let barPercentage = isMobile ? 0.40 : 0.40;
    let categoryPercentage = isMobile ? 0.5 : 0.5;
    let fontSize = isMobile ? 9 : isTablet ? 13 : 13;

    if (window.priceChart && typeof window.priceChart.destroy === 'function') window.priceChart.destroy();
    const ctx = document.getElementById('priceChart').getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 600, 0);
    gradient.addColorStop(0, '#667eea');
    gradient.addColorStop(1, '#764ba2');
    // Lighter color for max segment
    const lighterGradient = ctx.createLinearGradient(0, 0, 600, 0);
    lighterGradient.addColorStop(0, '#b3c6f7');
    lighterGradient.addColorStop(1, '#d1b3f7');

    window.priceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedBrands.map(b => b.brand),
            datasets: [
                {
                    label: 'Preço Mínimo (R$)',
                    data: sortedBrands.map(b => b.minPrice),
                    backgroundColor: sortedBrands.map(_ => gradient),
                    borderColor: 'rgba(102,126,234,0.18)',
                    borderWidth: 1.5,
                    borderRadius: 12,
                    stack: 'precos',
                    discounts: sortedBrands.map(b => b.maxDiscount > 0 ? b.maxDiscount : null),
                    minDiscounts: sortedBrands.map(b => b.hasMultipleDiscounts ? b.minDiscount : null),
                    maxDiscounts: sortedBrands.map(b => b.hasMultipleDiscounts ? b.maxDiscount : null),
                    positions: sortedBrands.map(b => b.minPosition !== Infinity ? b.minPosition : null),
                    barThickness: barThickness,
                    maxBarThickness: maxBarThickness,
                    barPercentage: barPercentage,
                    categoryPercentage: categoryPercentage
                },
                {
                    label: 'Diferença até o Máximo (R$)',
                    data: sortedBrands.map(b => b.maxPrice - b.minPrice),
                    backgroundColor: sortedBrands.map(_ => lighterGradient),
                    borderColor: 'rgba(102,126,234,0.10)',
                    borderWidth: 1.5,
                    borderRadius: 12,
                    stack: 'precos',
                    barThickness: barThickness,
                    maxBarThickness: maxBarThickness,
                    barPercentage: barPercentage,
                    categoryPercentage: categoryPercentage
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 700,
                easing: 'easeOutQuart'
            },
            layout: {
                padding: {
                    top: isMobile ? 2 : 20,
                    bottom: isMobile ? 2 : 20,
                    left: isMobile ? 6 : 10,
                    right: isMobile ? 90 : 90
                }
            },
            plugins: {
                legend: { display: false },
                datalabels: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(60, 60, 80, 0.92)',
                    titleFont: { family: 'Segoe UI', weight: 'bold', size: 15 },
                    bodyFont: { family: 'Segoe UI', weight: 'normal', size: 13 },
                    borderColor: '#667eea',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            const brand = context.chart.data.labels[context.dataIndex];
                            const min = sortedBrands[context.dataIndex].minPrice;
                            const max = sortedBrands[context.dataIndex].maxPrice;
                            if (context.datasetIndex === 0) {
                                return `Mínimo: R$ ${min.toFixed(2).replace('.', ',')}`;
                            } else if (context.datasetIndex === 1) {
                                return `Máximo: R$ ${max.toFixed(2).replace('.', ',')}`;
                            }
                            return '';
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    stacked: true,
                    grid: { display: false },
                    ticks: {
                        color: '#2d2e4a',
                        font: { size: isMobile ? 8 : fontSize, weight: 'bold' },
                        maxTicksLimit: isMobile ? 6 : undefined,
                        stepSize: isMobile ? 10 : undefined
                    }
                },
                y: {
                    offset: true,
                    grace: isMobile ? '5%' : '5%',
                    stacked: true,
                    grid: { color: 'rgba(102,126,234,0.07)', drawBorder: false },
                    ticks: {
                        font: {
                            size: isMobile ? 9 : fontSize,
                            weight: 'bold'
                        },
                        color: '#2d2e4a',
                        padding: isMobile ? 25 : 45
                    }
                }
            },
            transitions: {
                active: {
                    animation: {
                        duration: 0
                    }
                }
            }
        },
        plugins: [
            // Plugin para destacar a barra selecionada
            {
                afterDatasetsDraw: function(chart) {
                    if (!selectedProduct) return;
                    const dataset = chart.data.datasets[0];
                    const meta = chart.getDatasetMeta(0);
                    chart.data.labels.forEach((brand, i) => {
                        if (brand === selectedProduct.brand) {
                            const bar = meta.data[i];
                            if (!bar) return;
                            const ctx = chart.ctx;
                            ctx.save();
                            ctx.shadowColor = 'rgba(30,58,138,0.18)';
                            ctx.shadowBlur = 10;
                            ctx.lineWidth = 3;
                            ctx.strokeStyle = '#1e3a8a';
                            ctx.beginPath();
                            const left = Math.min(bar.x, bar.base) - 4;
                            const right = Math.max(bar.x, bar.base) + 4;
                            const top = bar.y - bar.height / 2 - 4;
                            const bottom = bar.y + bar.height / 2 + 4;
                            const width = right - left;
                            const height = bottom - top;
                            const radius = Math.min(12, bar.height / 2 + 2);
                            ctx.moveTo(left + radius, top);
                            ctx.lineTo(left + width - radius, top);
                            ctx.quadraticCurveTo(left + width, top, left + width, top + radius);
                            ctx.lineTo(left + width, top + height - radius);
                            ctx.quadraticCurveTo(left + width, top + height, left + width - radius, bottom);
                            ctx.lineTo(left + radius, bottom);
                            ctx.quadraticCurveTo(left, bottom, left, bottom - radius);
                            ctx.lineTo(left, top + radius);
                            ctx.quadraticCurveTo(left, top, left + radius, top);
                            ctx.closePath();
                            ctx.stroke();
                            ctx.restore();
                        }
                    });
                }
            },
            // Plugin do badge de desconto (deve ser o último para ficar na frente)
            window.descontoBadgePlugin
        ]
    });
    // Adicionar hover para as estrelas
    document.getElementById('priceChart').onmousemove = function(evt) {
        const rect = this.getBoundingClientRect();
        const x = evt.clientX - rect.left;
        const y = evt.clientY - rect.top;
        const existingTooltip = document.getElementById('starTooltip');
        if (existingTooltip) {
            existingTooltip.remove();
        }
        const chartArea = window.priceChart.chartArea;
        if (x < chartArea.left + 15 && y > chartArea.top && y < chartArea.bottom) {
            const barHeight = (chartArea.bottom - chartArea.top) / window.priceChart.data.labels.length;
            const brandIndex = Math.floor((y - chartArea.top) / barHeight);
            if (brandIndex >= 0 && brandIndex < window.priceChart.data.labels.length) {
                const brand = window.priceChart.data.labels[brandIndex];
                const brandProducts = allProducts.filter(p => p.brand === brand);
                if (brandProducts.length > 0) {
                    const tooltip = document.createElement('div');
                    tooltip.id = 'starTooltip';
                    tooltip.style.cssText = `
                        position: absolute;
                        background: rgba(0,0,0,0.8);
                        color: white;
                        padding: 8px 12px;
                        border-radius: 6px;
                        font-size: 12px;
                        z-index: 1000;
                        pointer-events: none;
                        left: ${evt.clientX + 10}px;
                        top: ${evt.clientY - 10}px;
                        max-width: 200px;
                    `;
                    let tooltipContent = `<strong>${brand}</strong><br>`;
                    brandProducts.forEach(product => {
                        if (product.position) {
                            tooltipContent += `${product.pharmacy}: posição ${product.position}<br>`;
                        }
                    });
                    tooltip.innerHTML = tooltipContent;
                    document.body.appendChild(tooltip);
                }
            }
        }
    };
    document.getElementById('priceChart').onmouseleave = function() {
        const existingTooltip = document.getElementById('starTooltip');
        if (existingTooltip) {
            existingTooltip.remove();
        }
    };
    document.getElementById('priceChart').onclick = function(evt) {
        const points = window.priceChart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
        if (points.length) {
            const index = points[0].index;
            const brand = window.priceChart.data.labels[index];
            const brandSelect = document.getElementById('brandSelect');
            if (selectedProduct && selectedProduct.brand === brand) {
                brandSelect.value = '';
                selectedProduct = null;
                renderPriceChart(allProducts);
                document.getElementById('comparisonSection').style.display = 'none';
                document.querySelectorAll('.product-card.destaque-produto').forEach(el => {
                    el.classList.remove('destaque-produto');
                });
            } else {
                brandSelect.value = brand;
                const event = new Event('change', { bubbles: true });
                brandSelect.dispatchEvent(event);
            }
        }
    };
}

 

function downloadExcel() {
    if (!allProducts || allProducts.length === 0) {
        alert('Nenhum dado disponível para exportar.');
        return;
    }
    
    // Preparar dados para exportação
    const exportData = allProducts.map(product => ({
        'Nome do Produto': product.name,
        'Marca': product.brand,
        'Farmácia': product.pharmacy,
        'Preço (R$)': typeof product.price === 'number' ? product.price.toFixed(2).replace('.', ',') : product.price,
        'Preço Original (R$)': typeof product.original_price === 'number' ? product.original_price.toFixed(2).replace('.', ',') : product.original_price,
        'Desconto (%)': product.discount_percentage || '',
        'Tem Desconto': product.has_discount ? 'Sim' : 'Não',
        'Posição': product.position || '',
        'Descrição': product.description || '',
        'URL do Produto': product.product_url || ''
    }));
    
    // Criar cabeçalho da planilha
    const headers = Object.keys(exportData[0]);
    
    // Criar conteúdo CSV
    let csvContent = '\ufeff'; // BOM para UTF-8
    csvContent += headers.join(';') + '\n';
    
    exportData.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            // Escapar aspas duplas e envolver em aspas se necessário
            if (typeof value === 'string' && (value.includes(';') || value.includes('"') || value.includes('\n'))) {
                return '"' + value.replace(/"/g, '""') + '"';
            }
            return value;
        });
        csvContent += values.join(';') + '\n';
    });
    
    // Criar blob e download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    // Gerar nome do arquivo com timestamp
    const now = new Date();
    const timestamp = now.toISOString().slice(0, 19).replace(/:/g, '-');
    const fileName = `produtos_medicamentos_${timestamp}.csv`;
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', fileName);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } else {
        // Fallback para navegadores mais antigos
        alert('Seu navegador não suporta download automático. Copie o conteúdo abaixo:');
        const textArea = document.createElement('textarea');
        textArea.value = csvContent;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Conteúdo copiado para a área de transferência!');
    }
} 

// INÍCIO: Função para configurar filtro por Marca
window.currentBrandFilter = '';
function setupBrandFilter(products) {
    // Obter marcas únicas
    const uniqueBrands = [...new Set(products.map(p => p.brand))].sort((a, b) => a.localeCompare(b, 'pt-BR'));
    const brandFilter = document.getElementById('brandFilter');
    
    // Limpar opções existentes (exceto a primeira)
    brandFilter.innerHTML = '<option value="">Todas as marcas</option>';
    
    // Adicionar opções de marcas
    uniqueBrands.forEach(brand => {
        const option = document.createElement('option');
        option.value = brand;
        option.textContent = brand;
        brandFilter.appendChild(option);
    });
    
    // Restaurar valor da variável global se ainda for válido
    if (window.currentBrandFilter && window.currentBrandFilter.trim() !== '' && uniqueBrands.includes(window.currentBrandFilter)) {
        brandFilter.value = window.currentBrandFilter;
        filterProductsByBrand(window.currentBrandFilter, products);
    }
    
    // Adicionar event listener para filtro (só se não existir)
    const existingListeners = brandFilter.getAttribute('data-has-listener');
    if (!existingListeners) {
        brandFilter.addEventListener('change', function() {
            const selectedBrand = this.value;
            filterProductsByBrand(selectedBrand, products);
        });
        brandFilter.setAttribute('data-has-listener', 'true');
    }
}
function filterProductsByBrand(selectedBrand, allProducts) {
    // Atualizar filtro global
    window.currentBrandFilter = selectedBrand;
    // Resetar página para 1 quando filtro é alterado
    currentPage = 1;
    // Se não há filtro aplicado (Todas as marcas), re-renderizar tudo
    if (!selectedBrand || selectedBrand.trim() === '') {
        renderProductsAndChart(allProducts);
        return;
    }
    // Re-renderizar apenas a lista de produtos sem re-inicializar componentes
    const resultsDiv = document.getElementById('results');
    // Aplicar filtro de marca
    let filteredProducts = allProducts.filter(product => product.brand === selectedBrand);
    // Aplicar filtro de farmácia se necessário
    if (currentPharmacyFilter && currentPharmacyFilter.trim() !== '') {
        filteredProducts = filteredProducts.filter(product => product.pharmacy === currentPharmacyFilter);
    }
    // Ordenar produtos
    const sortedProducts = getSortedProducts(filteredProducts, currentSort);
    // Calcular paginação
    const totalProducts = sortedProducts.length;
    const totalPages = Math.ceil(totalProducts / productsPerPage);
    // Ajustar página atual se necessário
    if (currentPage > totalPages && totalPages > 0) {
        currentPage = totalPages;
    }
    // Obter produtos da página atual
    const startIndex = (currentPage - 1) * productsPerPage;
    const endIndex = startIndex + productsPerPage;
    const currentPageProducts = sortedProducts.slice(startIndex, endIndex);
    // Renderizar produtos da página atual
    let productsHtml = '';
    currentPageProducts.forEach(product => {
        const priceDisplay = typeof product.price === 'number' 
            ? `R$ ${product.price.toFixed(2).replace('.', ',')}` 
            : product.price;
        const originalPriceDisplay = typeof product.original_price === 'number' 
            ? `R$ ${product.original_price.toFixed(2).replace('.', ',')}` 
            : product.original_price;
        productsHtml += `
            <div class="product-card" data-product-id="${product.name}">
                <div class="row align-items-center g-2">
                    <div class="col-2 col-md-1">
                        <div class="pharmacy-logo">
                            ${product.pharmacy === 'Droga Raia' ? 
                                '<img src="/static/logos/raia.png" alt="Raia Drogasil" title="Raia Drogasil" class="logo-img">' :
                                product.pharmacy === 'São João' ?
                                '<img src="/static/logos/sao_joao.png" alt="São João" title="São João" class="logo-img">' :
                                `<i class="fas fa-store logo-icon" title="${product.pharmacy}" aria-label="${product.pharmacy}"></i>`
                            }
                        </div>
                    </div>
                    <div class="col-7 col-md-6">
                        <h6 class="fw-bold mb-1 text-truncate">${product.name}</h6>
                        <span class="brand-badge">${product.brand}</span>
                        ${product.description ? `<p class="description-text mb-1 d-none d-md-block">${product.description}</p>` : ''}
                    </div>
                    <div class="col-3 col-md-5 text-end">
                        <div class="price">${priceDisplay}</div>
                        ${product.has_discount ? 
                            `<div class="original-price">${originalPriceDisplay}</div>
                             <span class="discount-badge">-${product.discount_percentage}%</span>` : ''
                        }
                        ${product.product_url ? 
                            `<a href="${product.product_url}" target="_blank" class="btn btn-sm btn-outline-primary mt-2 d-none d-md-inline-block">
                                <i class="fas fa-external-link-alt me-1"></i><span class="d-none d-lg-inline">Ver produto</span>
                            </a>` : ''
                        }
                    </div>
                </div>
            </div>
        `;
    });
    // Atualizar apenas a lista de produtos e paginação
    const productsListContainer = document.getElementById('productsList');
    if (productsListContainer) {
        productsListContainer.innerHTML = productsHtml;
    }
    // Atualizar paginação
    const paginationContainer = document.querySelector('.pagination-container');
    if (paginationContainer) {
        paginationContainer.outerHTML = renderPagination(totalProducts, currentPage, productsPerPage);
    }
    // Atualizar contador de produtos
    const badge = document.querySelector('.pharmacy-header .badge');
    if (badge) {
        badge.innerHTML = `${totalProducts} produtos`;
    }
}
// ... existing code ...