let allProducts = [];
let selectedProduct = null;
let priceChart = null;
let currentSort = 'relevancia';
let currentPharmacyFilter = ''; // Variável global para preservar o filtro

window.descontoBadgePlugin = {
    afterDatasetsDraw: function(chart) {
        const ctx = chart.ctx;
        const dataset = chart.data.datasets[0];
        if (!dataset.discounts) return;
        ctx.save();
        
        // Desenhar título "★ Ranking" em cima das estrelas
        ctx.font = 'bold 12px Segoe UI, Arial';
        ctx.fillStyle = '#495057';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        const titleX = chart.scales.x.left - 20;
        const titleY = chart.chartArea.top - 10;
        ctx.fillText('Ranking', titleX, titleY);
        chart.getDatasetMeta(0).data.forEach((bar, i) => {
            const discount = dataset.discounts[i];
            const price = dataset.data[i];
            const position = dataset.positions ? dataset.positions[i] : null;
            const priceLabel = `R$ ${price.toFixed(2).replace('.', ',')}`;
            
            // --- Ajuste responsivo da fonte do preço ---
            let priceFont = 'bold 16px Segoe UI, Arial';
            if (window.innerWidth < 576) {
                priceFont = 'bold 12px Segoe UI, Arial';
            } else if (window.innerWidth < 992) {
                priceFont = 'bold 14px Segoe UI, Arial';
            }
            ctx.font = priceFont;
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
            
            // Desenhar estrelas com posições (menor e maior)
            if (position) {
                const starSize = window.innerWidth < 576 ? 6 : window.innerWidth < 992 ? 10 : 14;
                const starSpacing = starSize * 1.4; // Espaçamento ainda menor entre as estrelas
                
                // Calcular menor e maior posição para esta marca
                const brandProducts = allProducts.filter(p => p.brand === chart.data.labels[i]);
                const positions = brandProducts.map(p => p.position).filter(pos => pos !== null && pos !== undefined);
                
                if (positions.length > 0) {
                    const minPosition = Math.min(...positions);
                    const maxPosition = Math.max(...positions);
                    
                    // Desenhar primeira estrela (maior posição) próxima dos nomes
                    let starX = maxPosition !== minPosition ? barStart - 35 : barStart - 25; // Centralizada quando uma estrela
                    let starY = maxPosition !== minPosition ? bar.y + 8 : bar.y; // No meio quando uma estrela, mais abaixo quando duas
                    
                    // Definir cor da primeira estrela baseada na maior posição
                    let starColor1, textColor1;
                    if (maxPosition === 1) {
                        starColor1 = '#FFD700'; // Dourado
                        textColor1 = '#fff';
                    } else if (maxPosition === 2) {
                        starColor1 = '#C0C0C0'; // Prata
                        textColor1 = '#fff';
                    } else if (maxPosition === 3) {
                        starColor1 = '#CD7F32'; // Bronze
                        textColor1 = '#fff';
                    } else {
                        starColor1 = '#555555'; // Cinza escuro
                        textColor1 = '#fff';
                    }
                    
                    // Desenhar primeira estrela com pontas menores
                    ctx.fillStyle = starColor1;
                    ctx.beginPath();
                    for (let j = 0; j < 10; j++) {
                        const angle = (j * 2 * Math.PI) / 10 - Math.PI / 2;
                        const radius = j % 2 === 0 ? starSize : starSize * 0.5; // Pontas menores
                        const x = starX + radius * Math.cos(angle);
                        const y = starY + radius * Math.sin(angle);
                        if (j === 0) {
                            ctx.moveTo(x, y);
                        } else {
                            ctx.lineTo(x, y);
                        }
                    }
                    ctx.closePath();
                    ctx.fill();
                    
                    // Adicionar número da maior posição
                    ctx.fillStyle = textColor1;
                    ctx.font = `bold ${starSize * 0.8}px Segoe UI, Arial`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(maxPosition.toString(), starX, starY);
                    
                    // Desenhar segunda estrela (menor posição) se for diferente da primeira
                    if (maxPosition !== minPosition) {
                        starX = barStart - 35 + (starSpacing * 0.8); // Ajustado para sobreposição moderada
                        
                        // Definir cor da segunda estrela baseada na menor posição
                        let starColor2, textColor2;
                        if (minPosition === 1) {
                            starColor2 = '#FFD700'; // Dourado
                            textColor2 = '#fff';
                        } else if (minPosition === 2) {
                            starColor2 = '#C0C0C0'; // Prata
                            textColor2 = '#fff';
                        } else if (minPosition === 3) {
                            starColor2 = '#CD7F32'; // Bronze
                            textColor2 = '#fff';
                        } else {
                            starColor2 = '#555555'; // Cinza escuro
                            textColor2 = '#fff';
                        }
                        
                        // Desenhar segunda estrela com pontas menores (acima e à direita)
                        ctx.fillStyle = starColor2;
                        ctx.beginPath();
                        for (let j = 0; j < 10; j++) {
                            const angle = (j * 2 * Math.PI) / 10 - Math.PI / 2;
                            const radius = j % 2 === 0 ? starSize : starSize * 0.5; // Pontas menores
                            const x = starX + radius * Math.cos(angle);
                            const y = (starY - 12) + radius * Math.sin(angle); // Posicionada mais acima da primeira
                            if (j === 0) {
                                ctx.moveTo(x, y);
                            } else {
                                ctx.lineTo(x, y);
                            }
                        }
                        ctx.closePath();
                        ctx.fill();
                        
                        // Adicionar número da menor posição
                        ctx.fillStyle = textColor2;
                        ctx.font = `bold ${starSize * 0.8}px Segoe UI, Arial`;
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(minPosition.toString(), starX, starY - 12); // Posicionada mais acima da primeira
                    }
                }
            }
            
            if (discount || (dataset.minDiscounts && dataset.minDiscounts[i] !== null)) {
                // --- Ajuste responsivo do badge ---
                let badgeWidth = 40, badgeHeight = 20, badgeFont = 'bold 12px Segoe UI, Arial';
                if (window.innerWidth < 576) {
                    badgeWidth = 28;
                    badgeHeight = 14;
                    badgeFont = 'bold 9px Segoe UI, Arial';
                } else if (window.innerWidth < 992) {
                    badgeWidth = 32;
                    badgeHeight = 16;
                    badgeFont = 'bold 10px Segoe UI, Arial';
                }
                
                // Verificar se há múltiplos descontos para esta marca
                const minDiscount = dataset.minDiscounts ? dataset.minDiscounts[i] : null;
                const maxDiscount = dataset.maxDiscounts ? dataset.maxDiscounts[i] : null;
                const hasMultipleDiscounts = minDiscount !== null && maxDiscount !== null && minDiscount !== maxDiscount;
                
                if (hasMultipleDiscounts) {
                    // Badge único com maior desconto
                    let x = textX + priceWidth / 2 + 8;
                    let y = textY - badgeHeight / 2;
                    
                    // Calcular texto com "até"
                    const maxText = `até -${maxDiscount}%`;
                    
                    // Ajustar largura do badge baseado no texto
                    const textWidth = ctx.measureText(maxText).width;
                    const adjustedBadgeWidth = Math.max(badgeWidth, textWidth + 16);
                    
                    if (x + adjustedBadgeWidth > chart.chartArea.right - 8) {
                        x = chart.chartArea.right - adjustedBadgeWidth - 8;
                    }
                    
                    // Desenhar badge
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
                    
                    // Texto com "até"
                    ctx.font = badgeFont;
                    ctx.fillStyle = '#fff';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(maxText, x + adjustedBadgeWidth / 2, y + badgeHeight / 2);
                    
                } else {
                    // Badge único (comportamento original)
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
            
            renderListFn(products);
            if (renderChartFn) {
                renderChartFn(products);
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
                        updatePositionComparison();
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
                updatePositionComparison();
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
    
    // Calcular número de farmácias onde a marca foi encontrada
    const brandProducts = allProducts.filter(p => p.brand === selectedProduct.brand);
    const uniquePharmacies = [...new Set(brandProducts.map(p => p.pharmacy))];
    const pharmacyCount = uniquePharmacies.length;
    
    // Calcular maior e menor preço da marca
    const brandPrices = brandProducts.map(p => p.price).filter(price => typeof price === 'number' && price > 0);
    const minPrice = Math.min(...brandPrices);
    const maxPrice = Math.max(...brandPrices);
    
    // Gerar cards para cada farmácia
    let pharmacyCardsHtml = '';
    brandProducts.forEach(product => {
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
        
        const priceDisplay = typeof product.price === 'number' 
            ? `R$ ${product.price.toFixed(2).replace('.', ',')}` 
            : product.price;
        const originalPriceDisplay = typeof product.original_price === 'number' 
            ? `R$ ${product.original_price.toFixed(2).replace('.', ',')}` 
            : product.original_price;
        
        pharmacyCardsHtml += `
            <div class="col-6 col-md-4 col-lg-3 mb-2">
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
                                <span class="badge bg-secondary">${product.position || 'N/A'}</span>
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
        <h6 class="mb-3"><i class="fas fa-store me-2"></i>Detalhes por Farmácia</h6>
        <div class="row g-2">
            ${pharmacyCardsHtml}
        </div>
    `;
    
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
                    <!-- Legenda das estrelas -->
                    <div class="star-legend mt-3 text-center">
                        <small class="text-muted">
                            <span class="legend-item me-3">
                                <span class="legend-star" style="color: #FFD700;">★</span> 1ª posição
                            </span>
                            <span class="legend-item me-3">
                                <span class="legend-star" style="color: #C0C0C0;">★</span> 2ª posição
                            </span>
                            <span class="legend-item me-3">
                                <span class="legend-star" style="color: #CD7F32;">★</span> 3ª posição
                            </span>
                            <span class="legend-item me-3">
                                <span class="legend-star" style="color: #555555;">★</span> 4ª+ posição
                            </span>
                            <span class="legend-item">
                                <i class="fas fa-info-circle me-1"></i>Primeira estrela: menor posição | Segunda estrela: maior posição
                            </span>
                        </small>
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
                    <i class="fas fa-list me-2"></i>Lista de Produtos <span class="badge bg-light text-dark ms-2">${products.length} produtos</span>
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
                </div>
                <div id="productsList">
                    ${productsHtml}
                </div>
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
    if (currentPharmacyFilter && uniquePharmacies.includes(currentPharmacyFilter)) {
        pharmacyFilter.value = currentPharmacyFilter;
        filterProductsByPharmacy(currentPharmacyFilter, products);
    }
    
    // Adicionar event listener para filtro (só se não existir)
    const existingListeners = pharmacyFilter.getAttribute('data-has-listener');
    if (!existingListeners) {
        pharmacyFilter.addEventListener('change', function() {
            const selectedPharmacy = this.value;
            currentPharmacyFilter = selectedPharmacy; // Atualizar variável global
            filterProductsByPharmacy(selectedPharmacy, products);
        });
        pharmacyFilter.setAttribute('data-has-listener', 'true');
    }
}

function filterProductsByPharmacy(selectedPharmacy, allProducts) {
    const productsList = document.getElementById('productsList');
    const productCards = productsList.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        const pharmacyLogo = card.querySelector('.pharmacy-logo');
        let pharmacyName = '';
        
        // Determinar a farmácia baseada no logo/imagem
        if (pharmacyLogo.querySelector('img[src*="raia.png"]')) {
            pharmacyName = 'Droga Raia';
        } else if (pharmacyLogo.querySelector('img[src*="sao_joao.png"]')) {
            pharmacyName = 'São João';
        } else {
            // Para outras farmácias, tentar extrair do ícone
            const icon = pharmacyLogo.querySelector('.logo-icon');
            if (icon) {
                pharmacyName = icon.getAttribute('title') || icon.getAttribute('aria-label');
            }
        }
        
        // Mostrar/ocultar baseado no filtro
        if (!selectedPharmacy || pharmacyName === selectedPharmacy) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
    
    // Atualizar contador de produtos
    const visibleProducts = productsList.querySelectorAll('.product-card[style*="display: block"], .product-card:not([style*="display: none"])');
    const badge = document.querySelector('.pharmacy-header .badge');
    if (badge) {
        badge.textContent = `${visibleProducts.length} produtos`;
    }
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
        .map(([brand, data]) => {
            const brandProducts = allProducts.filter(p => p.brand === brand);
            const discounts = brandProducts.map(p => p.discount_percentage || 0);
            const maxDiscount = discounts.length > 0 ? Math.max(...discounts) : 0;
            const minDiscount = discounts.length > 0 ? Math.min(...discounts) : 0;
            
            return {
                brand: brand,
                avgPrice: data.prices.reduce((a, b) => a + b, 0) / data.prices.length,
                count: data.prices.length,
                maxDiscount: maxDiscount,
                minDiscount: minDiscount,
                hasMultipleDiscounts: maxDiscount !== minDiscount,
                minPosition: Math.min(...allProducts.filter(p => p.brand === brand).map(p => p.position ?? Infinity))
            };
        });
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
        chartWrapper.style.minHeight = `${Math.max(60 * barCount, 200)}px`; // Altura reduzida para mobile
    } else if (isTablet) {
        chartWrapper.style.minHeight = `${Math.max(50 * barCount, 220)}px`; // Altura aumentada para tablet
    } else {
        chartWrapper.style.minHeight = `${Math.max(32 * barCount, 200)}px`;
    }

    // Espessura e espaçamento das barras
    let barThickness = isMobile ? 12 : isTablet ? 18 : 32;
    let maxBarThickness = isMobile ? 16 : isTablet ? 22 : 40;
    let barPercentage = isMobile ? 0.35 : 0.65;
    let categoryPercentage = isMobile ? 0.8 : 0.7;
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
                    selectedProduct && b.brand === selectedProduct.brand ? '#1e3a8a' : 
                    selectedProduct ? '#a8b4e6' : '#667eea'
                ),
                borderColor: sortedBrands.map(b =>
                    selectedProduct && b.brand === selectedProduct.brand ? '#1e3a8a' : 
                    selectedProduct ? '#a8b4e6' : '#667eea'
                ),
                borderWidth: isMobile ? 0 : isTablet ? 0.8 : 1,
                discounts: sortedBrands.map(b => b.maxDiscount > 0 ? b.maxDiscount : null),
                minDiscounts: sortedBrands.map(b => b.hasMultipleDiscounts ? b.minDiscount : null),
                maxDiscounts: sortedBrands.map(b => b.hasMultipleDiscounts ? b.maxDiscount : null),
                positions: sortedBrands.map(b => b.minPosition !== Infinity ? b.minPosition : null),
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
            animation: {
                duration: 0 // Desabilita todas as animações
            },
            layout: {
                padding: {
                    top: isMobile ? 5 : 20,
                    bottom: isMobile ? 5 : 20,
                    left: isMobile ? 25 : 35,
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
                            const minDiscount = context.dataset.minDiscounts ? context.dataset.minDiscounts[context.dataIndex] : null;
                            const maxDiscount = context.dataset.maxDiscounts ? context.dataset.maxDiscounts[context.dataIndex] : null;
                            let label = `Preço médio: R$ ${context.parsed.x.toFixed(2).replace('.', ',')}`;
                            
                            if (minDiscount !== null && maxDiscount !== null && minDiscount !== maxDiscount) {
                                label += ` | Desconto: até -${maxDiscount}%`;
                            } else if (discount) {
                                label += ` | Desconto: -${discount}%`;
                            }
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
                    grace: isMobile ? '5%' : '5%',
                    ticks: {
                        font: {
                            size: fontSize,
                            weight: 'bold'
                        },
                        color: '#333',
                        padding: isMobile ? 35 : 45
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
        plugins: [window.descontoBadgePlugin]
    });
    // Adicionar hover para as estrelas
    document.getElementById('priceChart').onmousemove = function(evt) {
        const rect = this.getBoundingClientRect();
        const x = evt.clientX - rect.left;
        const y = evt.clientY - rect.top;
        
        // Remover tooltip anterior
        const existingTooltip = document.getElementById('starTooltip');
        if (existingTooltip) {
            existingTooltip.remove();
        }
        
        // Verificar se está na área das estrelas (lado esquerdo do gráfico)
        const chartArea = window.priceChart.chartArea;
        if (x < chartArea.left + 15 && y > chartArea.top && y < chartArea.bottom) {
            // Encontrar a marca correspondente baseada na posição Y
            const barHeight = (chartArea.bottom - chartArea.top) / window.priceChart.data.labels.length;
            const brandIndex = Math.floor((y - chartArea.top) / barHeight);
            
            if (brandIndex >= 0 && brandIndex < window.priceChart.data.labels.length) {
                const brand = window.priceChart.data.labels[brandIndex];
                const brandProducts = allProducts.filter(p => p.brand === brand);
                
                if (brandProducts.length > 0) {
                    // Criar tooltip com informações das farmácias
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
    
    // Remover tooltip quando sair da área do gráfico
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
            // Se já está selecionada, deseleciona
            if (selectedProduct && selectedProduct.brand === brand) {
                brandSelect.value = '';
                selectedProduct = null;
                renderPriceChart(allProducts);
                document.getElementById('comparisonSection').style.display = 'none';
                // Remover destaque na lista de produtos
                document.querySelectorAll('.product-card.destaque-produto').forEach(el => {
                    el.classList.remove('destaque-produto');
                });
            } else {
                brandSelect.value = brand;
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