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

function renderSortButtons(targetId) {
    return `
        <div class="btn-group btn-group-sm ms-2" role="group" aria-label="Ordenar por">
            <button type="button" class="btn btn-outline-primary sort-btn${currentSort==='relevancia' ? ' active' : ''}" data-sort="relevancia">Relevância</button>
            <button type="button" class="btn btn-outline-primary sort-btn${currentSort==='menor_preco' ? ' active' : ''}" data-sort="menor_preco">Menor preço</button>
            <button type="button" class="btn btn-outline-primary sort-btn${currentSort==='maior_preco' ? ' active' : ''}" data-sort="maior_preco">Maior preço</button>
            <button type="button" class="btn btn-outline-primary sort-btn${currentSort==='maior_desconto' ? ' active' : ''}" data-sort="maior_desconto">Maior desconto</button>
        </div>
    `;
}

function attachSortButtonListeners(products, renderListFn, renderChartFn) {
    document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.onclick = function() {
            currentSort = this.getAttribute('data-sort');
            renderListFn(products);
            if (renderChartFn) renderChartFn(products);
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
            <div class="row stats-row" id="statsSection" style="display: none;">
                <div>
                    <div class="stats-card text-center">
                        <div class="stats-number" id="totalBrands">0</div>
                        <div class="stats-label">Total de Marcas</div>
                    </div>
                </div>
                <div>
                    <div class="stats-card text-center">
                        <div class="stats-number" id="minPrice">R$ 0,00</div>
                        <div class="stats-label">Menor Preço</div>
                    </div>
                </div>
                <div>
                    <div class="stats-card text-center">
                        <div class="stats-number" id="avgPrice">R$ 0,00</div>
                        <div class="stats-label">Preço Médio</div>
                    </div>
                </div>
                <div>
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
            updatePositionComparison();
            highlightFirstProduct();
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
                ? (b.brand === selectedProduct.brand ? '#ffe4e1' : '#a3bffa')
                : '#667eea'
        );
        priceChart.data.datasets[0].borderColor = sortedBrands.map(b => 
            selectedProduct
                ? (b.brand === selectedProduct.brand ? '#c0392b' : '#a3bffa')
                : '#667eea'
        );
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
        <div class="row">
            <div class="col-md-6">
                <strong>${selectedProduct.brand}</strong><br>
                <span class="position-indicator ${positionClass}">${positionText}</span><br>
                <small>Posição ${position} de ${totalBrands} marcas</small>
            </div>
            <div class="col-md-6">
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
                <div class="row align-items-center">
                    <div class="col-md-1">
                        <div class="pharmacy-logo">
                            ${product.pharmacy === 'Droga Raia' ? 
                                '<img src="/static/logos/raia.png" alt="Raia Drogasil" title="Raia Drogasil" class="logo-img">' :
                                `<i class="fas fa-store logo-icon" title="${product.pharmacy}" aria-label="${product.pharmacy}"></i>`
                            }
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h6 class="fw-bold mb-1">${product.name}</h6>
                        <span class="brand-badge">${product.brand}</span>
                        ${product.description ? `<p class="description-text mb-1">${product.description}</p>` : ''}
                    </div>
                    <div class="col-md-5 text-end">
                        <div class="price">${priceDisplay}</div>
                        ${product.has_discount ? 
                            `<div class="original-price">${originalPriceDisplay}</div>
                             <span class="discount-badge">-${product.discount_percentage}%</span>` : ''
                        }
                        ${product.product_url ? 
                            `<a href="${product.product_url}" target="_blank" class="btn btn-sm btn-outline-primary mt-2">
                                <i class="fas fa-external-link-alt me-1"></i>Ver produto
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
        <div class="chart-container mt-4" id="priceChartSection">
            <div class="d-flex align-items-center justify-content-between">
                <h5 class="mb-0"><i class="fas fa-chart-bar me-2"></i>Preços por Marca</h5>
                ${renderSortButtons('priceChartSection')}
            </div>
            <div class="chart-wrapper">
                <canvas id="priceChart"></canvas>
            </div>
        </div>
        <div class="pharmacy-card">
            <div class="pharmacy-header d-flex align-items-center justify-content-between">
                <div><i class="fas fa-list me-2"></i>Lista de Produtos <span class="badge bg-light text-dark ms-2">${products.length} produtos</span></div>
                ${renderSortButtons('productsList')}
            </div>
            <div class="p-3" id="productsList">
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
    // Criar gráfico
    const priceCtx = document.getElementById('priceChart').getContext('2d');
    if (window.priceChart && typeof window.priceChart.destroy === 'function') window.priceChart.destroy();
    window.priceChart = new Chart(priceCtx, {
        type: 'bar',
        data: {
            labels: sortedBrands.map(b => b.brand),
            datasets: [{
                label: 'Preço Médio (R$)',
                data: sortedBrands.map(b => b.avgPrice),
                backgroundColor: sortedBrands.map(b =>
                    selectedProduct
                        ? (b.brand === selectedProduct.brand ? '#ffe4e1' : '#a3bffa')
                        : '#667eea'
                ),
                borderColor: sortedBrands.map(b =>
                    selectedProduct
                        ? (b.brand === selectedProduct.brand ? '#c0392b' : '#a3bffa')
                        : '#667eea'
                ),
                borderWidth: 1,
                discounts: sortedBrands.map(b => b.maxDiscount > 0 ? b.maxDiscount : null)
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
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