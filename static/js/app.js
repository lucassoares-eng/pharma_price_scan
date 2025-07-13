let allProducts = [];
let selectedProduct = null;
let priceChart = null;
let currentSort = 'relevancia';

window.descontoBadgePlugin = {
    afterDatasetsDraw: function(chart) {
        const ctx = chart.ctx;
        const dataset = chart.data.datasets[0];
        if (!dataset.discounts) return;
        ctx.save();
        chart.getDatasetMeta(0).data.forEach((bar, i) => {
            const discount = dataset.discounts[i];
            const price = dataset.data[i];
            const priceLabel = `R$ ${price.toFixed(2).replace('.', ',')}`;
            ctx.font = 'bold 16px Segoe UI, Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            // Calcular o centro da barra horizontal
            const barStart = chart.scales.x.left;
            const centerX = barStart + (bar.x - barStart) / 2;
            let textX = centerX;
            let textY = bar.y;
            // Cor do preço: preto se barra selecionada, branco caso contrário
            let isSelected = window.selectedProduct && chart.data.labels[i] === window.selectedProduct.brand;
            ctx.fillStyle = isSelected ? '#222' : '#fff';
            ctx.fillText(priceLabel, textX, textY);
            const priceWidth = ctx.measureText(priceLabel).width;
            if (discount) {
                // Badge imediatamente ao lado direito do texto centralizado
                const badgeWidth = 48, badgeHeight = 24;
                let x = textX + priceWidth / 2 + 8;
                let y = textY - badgeHeight / 2;
                if (x + badgeWidth > chart.chartArea.right - 8) {
                    x = chart.chartArea.right - badgeWidth - 8;
                }
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
                ctx.font = 'bold 14px Segoe UI, Arial';
                ctx.fillStyle = '#fff';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(`-${discount}%`, x + badgeWidth / 2, y + badgeHeight / 2);
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

function attachSortButtonListeners(products, renderListFn, renderChartFn) {
    document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.onclick = function() {
            currentSort = this.getAttribute('data-sort');
            renderListFn(products);
            if (renderChartFn) {
                renderChartFn(products);
                setTimeout(() => {
                    renderPositionChart(products);
                }, 100);
            } else {
                renderPositionChart(products);
            }
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
    
    const results = data.results;
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
    
    // Obter marcas únicas
    const uniqueBrands = [...new Set(allProducts.map(p => p.brand))];
    const brandSelect = document.getElementById('brandSelect');
    
    // Limpar opções existentes
    brandSelect.innerHTML = '<option value="">Selecione uma marca...</option>';
    
    // Adicionar opções
    uniqueBrands.forEach(brand => {
        const option = document.createElement('option');
        option.value = brand;
        option.textContent = brand;
        brandSelect.appendChild(option);
    });
    
    // Adicionar event listener
    brandSelect.addEventListener('change', function() {
        const selectedBrand = this.value;
                    if (selectedBrand) {
                // Encontrar o primeiro produto da marca selecionada
                selectedProduct = allProducts.find(p => p.brand === selectedBrand);
                renderPriceChart(allProducts);
                setTimeout(() => {
                    renderPositionChart(allProducts);
                }, 100);
                updatePositionComparison();
                highlightFirstProduct();
            } else {
                selectedProduct = null;
                renderPriceChart(allProducts);
                setTimeout(() => {
                    renderPositionChart(allProducts);
                }, 100);
                document.getElementById('comparisonSection').style.display = 'none';
                // Remover destaque na lista de produtos
                document.querySelectorAll('.product-card.destaque-produto').forEach(el => {
                    el.classList.remove('destaque-produto');
                });
            }
    });
    
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
                avgPrice: data.prices.reduce((a, b) => a + b, 0) / data.prices.length,
                count: data.prices.length
            }))
            .sort((a, b) => a.avgPrice - b.avgPrice);
        
        priceChart.data.labels = sortedBrands.map(b => b.brand);
        priceChart.data.datasets[0].data = sortedBrands.map(b => b.avgPrice);
        priceChart.data.datasets[0].backgroundColor = sortedBrands.map(b => 
            selectedProduct
                ? (b.brand === selectedProduct.brand ? '#1e3a8a' : '#a3bffa')
                : '#667eea'
        );
        priceChart.data.datasets[0].borderColor = sortedBrands.map(b => 
            selectedProduct
                ? (b.brand === selectedProduct.brand ? '#1e3a8a' : '#a3bffa')
                : '#667eea'
        );
        priceChart.data.datasets[0].borderWidth = 1;
        priceChart.update();
    }
    // Sempre remover destaque da lista de produtos ao atualizar gráfico sem seleção
    if (!selectedProduct) {
        document.querySelectorAll('.product-card.destaque-produto').forEach(el => {
            el.classList.remove('destaque-produto');
        });
    }
}

function updatePositionComparison() {
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
    
    document.getElementById('positionInfo').innerHTML = `
        <div class="row g-3">
            <div class="col-12 col-md-6">
                <strong>${selectedProduct.brand}</strong><br>
                <span class="position-indicator ${positionClass}">${positionText}</span><br>
                <small>Posição ${position} de ${totalBrands} marcas</small>
            </div>
            <div class="col-12 col-md-6">
                <strong>Preço médio: R$ ${selectedBrandAvg.avgPrice.toFixed(2).replace('.', ',')}</strong><br>
                <small>${priceDiffText} em relação à média geral</small><br>
                <small>${selectedBrandAvg.prices.length} produtos encontrados</small>
            </div>
        </div>
    `;
    
    document.getElementById('comparisonSection').style.display = 'block';
}

function highlightFirstProduct() {
    // Remover destaque anterior
    document.querySelectorAll('.product-card.destaque-produto').forEach(el => {
        el.classList.remove('destaque-produto');
    });
    if (!selectedProduct) return;
    // Encontrar o primeiro card de qualquer farmácia com a marca selecionada
    const cards = document.querySelectorAll('.pharmacy-card');
    for (const card of cards) {
        const productCards = card.querySelectorAll('.product-card');
        for (const prodCard of productCards) {
            // Checar se é da marca selecionada
            const brandBadge = prodCard.querySelector('.brand-badge');
            if (brandBadge && brandBadge.textContent === selectedProduct.brand) {
                prodCard.classList.add('destaque-produto');
                return;
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

function renderProductsAndChart(products) {
    const resultsDiv = document.getElementById('results');
    // Renderizar header da lista com botões de ordenação
    let productsHtml = '';
    const sortedProducts = getSortedProducts(products, currentSort);
    sortedProducts.forEach(product => {
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
                <div class="col-12 col-lg-6 mb-3 mb-lg-4">
                    <h6 class="text-center mb-3"><i class="fas fa-chart-bar me-2"></i>Preços por Marca</h6>
                    <div class="chart-wrapper">
                        <canvas id="priceChart"></canvas>
                    </div>
                </div>
                <div class="col-12 col-lg-6 mb-3 mb-lg-4">
                    <h6 class="text-center mb-3"><i class="fas fa-sort-numeric-up me-2"></i>Posição nos Sites</h6>
                    <div class="chart-wrapper">
                        <canvas id="positionChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        <div class="pharmacy-card">
            <div class="pharmacy-header d-flex flex-column flex-md-row align-items-start align-items-md-center justify-content-between">
                <div class="d-flex align-items-center mb-2 mb-md-0">
                    <i class="fas fa-list me-2"></i>Lista de Produtos <span class="badge bg-light text-dark ms-2">${products.length} produtos</span>
                    <button type="button" class="btn btn-success btn-sm ms-2 ms-md-3" onclick="downloadExcel()">
                        <i class="fas fa-download me-1"></i><span class="d-none d-sm-inline">Exportar Excel</span>
                    </button>
                </div>
                <div class="d-flex align-items-center justify-content-center justify-content-md-end">
                    ${renderSortButtons('productsList', true)}
                </div>
            </div>
            <div class="p-2 p-md-3" id="productsList">
                ${productsHtml}
            </div>
        </div>
        <div class="comparison-highlight" id="comparisonSection" style="display: none;">
            <h5><i class="fas fa-chart-line me-2"></i>Análise Comparativa da Marca Selecionada</h5>
            <div id="positionInfo"></div>
        </div>
    `;
    attachSortButtonListeners(products, renderProductsAndChart, renderPriceChart);
    setTimeout(() => {
        renderPriceChart(products);
        setTimeout(() => {
            renderPositionChart(products);
        }, 100);
        showBrandSelector();
    }, 0);

    // Atualizar estatísticas e gráfico de preços após a renderização
    // updateStatistics(); // Removido
    // createPriceChart(); // Removido
}

function renderPriceChart(products) {
    // Agrupar produtos por marca e calcular preço médio por marca
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
    // Calcular preço médio por marca e ordenar conforme o sort
    let sortedBrands = Object.entries(brandData)
        .map(([brand, data]) => ({
            brand: brand,
            avgPrice: data.prices.reduce((a, b) => a + b, 0) / data.prices.length,
            count: data.prices.length,
            maxDiscount: Math.max(...allProducts.filter(p => p.brand === brand).map(p => p.discount_percentage || 0))
        }));
    if (currentSort === 'menor_preco') {
        sortedBrands.sort((a, b) => a.avgPrice - b.avgPrice);
    } else if (currentSort === 'maior_preco') {
        sortedBrands.sort((a, b) => b.avgPrice - a.avgPrice);
    } else if (currentSort === 'maior_desconto') {
        sortedBrands.sort((a, b) => b.maxDiscount - a.maxDiscount);
    } else { // relevancia
        // Ordenar por menor posição de produto daquela marca
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
    // Ajustar altura do chart-wrapper via CSS
    const chartWrapper = document.getElementById('priceChart').parentElement;
    if (isMobile) {
        chartWrapper.style.minHeight = `${Math.max(48 * barCount, 160)}px`;
    } else if (isTablet) {
        chartWrapper.style.minHeight = `${Math.max(38 * barCount, 180)}px`;
    } else {
        chartWrapper.style.minHeight = `${Math.max(32 * barCount, 200)}px`;
    }

    // Espessura e espaçamento das barras
    let barThickness = isMobile ? 14 : isTablet ? 20 : 26;
    let maxBarThickness = isMobile ? 18 : isTablet ? 24 : 32;
    let barPercentage = isMobile ? 0.45 : 0.65;
    let categoryPercentage = isMobile ? 0.5 : 0.7;
    // Fonte dos rótulos
    let fontSize = isMobile ? 12 : isTablet ? 13 : 14;

    if (window.priceChart && typeof window.priceChart.destroy === 'function') window.priceChart.destroy();
    window.priceChart = new Chart(document.getElementById('priceChart').getContext('2d'), {
        type: 'bar',
        data: {
            labels: sortedBrands.map(b => b.brand),
            datasets: [{
                label: 'Preço Médio (R$)',
                data: sortedBrands.map(b => b.avgPrice),
                backgroundColor: sortedBrands.map(b =>
                    selectedProduct
                        ? (b.brand === selectedProduct.brand ? '#1e3a8a' : '#a3bffa')
                        : '#667eea'
                ),
                borderColor: sortedBrands.map(b =>
                    selectedProduct
                        ? (b.brand === selectedProduct.brand ? '#1e3a8a' : '#a3bffa')
                        : '#667eea'
                ),
                borderWidth: 1,
                discounts: sortedBrands.map(b => b.maxDiscount > 0 ? b.maxDiscount : null),
                barThickness: barThickness,
                maxBarThickness: maxBarThickness,
                barPercentage: barPercentage,
                categoryPercentage: categoryPercentage
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    top: isMobile ? 10 : 20,
                    bottom: isMobile ? 10 : 20,
                    left: 0,
                    right: 0
                }
            },
            plugins: {
                legend: { display: false },
                datalabels: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const discount = context.dataset.discounts[context.dataIndex];
                            let label = `Preço médio: R$ ${context.parsed.x.toFixed(2).replace('.', ',')}`;
                            if (discount) label += ` | Desconto: -${discount}%`;
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: { display: true, text: 'Preço (R$)' }
                },
                y: {
                    offset: true,
                    grace: isMobile ? '10%' : '5%',
                    ticks: {
                        font: {
                            size: fontSize,
                            weight: 'bold'
                        },
                        color: '#333',
                        padding: isMobile ? 8 : 12
                    }
                }
            }
        },
        plugins: [window.descontoBadgePlugin]
    });
    document.getElementById('priceChart').onclick = function(evt) {
        const points = window.priceChart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
        if (points.length) {
            const index = points[0].index;
            const brand = window.priceChart.data.labels[index];
            const brandSelect = document.getElementById('brandSelect');
            // Se já está selecionada, deseleciona
            if (selectedProduct && selectedProduct.brand === brand) {
                brandSelect.value = '';
                selectedProduct = null;
                renderPriceChart(allProducts);
                document.getElementById('comparisonSection').style.display = 'none';
            } else {
                brandSelect.value = brand;
                // Disparar o evento de change para atualizar análise
                const event = new Event('change', { bubbles: true });
                brandSelect.dispatchEvent(event);
            }
        }
    };
}

function renderPositionChart(products) {
    // Obter marcas únicas na mesma ordem do gráfico de preços
    const priceChartData = window.priceChart ? window.priceChart.data.labels : [];
    const brands = priceChartData.length > 0 ? priceChartData : [...new Set(products.map(p => p.brand))];
    
    // Obter farmácias únicas
    const pharmacies = [...new Set(products.map(p => p.pharmacy))];
    
    // Criar dados do heatmap: Produto x Site
    const heatmapData = brands.map(brand => {
        const brandProducts = products.filter(p => p.brand === brand);
        return pharmacies.map(pharmacy => {
            const product = brandProducts.find(p => p.pharmacy === pharmacy);
            return product && typeof product.position === 'number' ? product.position : null;
        });
    });
    
    // Função para determinar a cor baseada na posição
    function getPositionColor(position) {
        if (position === null) return '#f8f9fa'; // Cinza claro para posições não encontradas
        if (position <= 5) return '#28a745'; // Verde para posições muito boas (1-5)
        if (position <= 10) return '#90EE90'; // Verde claro para posições boas (6-10)
        if (position <= 20) return '#FFD700'; // Amarelo para posições médias (11-20)
        if (position <= 30) return '#FFA500'; // Laranja para posições ruins (21-30)
        return '#dc3545'; // Vermelho para posições muito ruins (31+)
    }
    
    // Criar gráfico heatmap
    const positionCtx = document.getElementById('positionChart').getContext('2d');
    if (window.positionChart && typeof window.positionChart.destroy === 'function') window.positionChart.destroy();
    
    // Criar dados para o heatmap usando scatter plot
    const scatterData = [];
    brands.forEach((brand, brandIndex) => {
        pharmacies.forEach((pharmacy, pharmacyIndex) => {
            const position = heatmapData[brandIndex][pharmacyIndex];
            if (position !== null) {
                scatterData.push({
                    x: pharmacyIndex,
                    y: brandIndex,
                    r: 8, // Tamanho do ponto
                    position: position,
                    brand: brand,
                    pharmacy: pharmacy
                });
            }
        });
    });
    
    window.positionChart = new Chart(positionCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Posições',
                data: scatterData,
                backgroundColor: scatterData.map(point => getPositionColor(point.position)),
                borderColor: scatterData.map(point => 
                    selectedProduct && point.brand === selectedProduct.brand ? '#1e3a8a' : '#333'
                ),
                borderWidth: scatterData.map(point => 
                    selectedProduct && point.brand === selectedProduct.brand ? 2 : 1
                ),
                pointRadius: scatterData.map(point => 
                    selectedProduct && point.brand === selectedProduct.brand ? 10 : 8
                )
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const point = context.raw;
                            return [
                                `Marca: ${point.brand}`,
                                `Site: ${point.pharmacy}`,
                                `Posição: ${point.position}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    min: -0.5,
                    max: pharmacies.length - 0.5,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return pharmacies[value] || '';
                        },
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    type: 'linear',
                    min: -0.5,
                    max: brands.length - 0.5,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return brands[value] || '';
                        },
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
    
    document.getElementById('positionChart').onclick = function(evt) {
        const points = window.positionChart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
        if (points.length) {
            const point = points[0].raw;
            const brandSelect = document.getElementById('brandSelect');
            // Se já está selecionada, deseleciona
            if (selectedProduct && selectedProduct.brand === point.brand) {
                brandSelect.value = '';
                selectedProduct = null;
                renderPriceChart(allProducts);
                renderPositionChart(allProducts);
                document.getElementById('comparisonSection').style.display = 'none';
            } else {
                brandSelect.value = point.brand;
                // Disparar o evento de change para atualizar análise
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