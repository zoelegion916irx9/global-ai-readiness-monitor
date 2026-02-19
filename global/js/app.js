// app.js — ICAIRE Global AI Readiness Monitor

const App = (() => {
    // State
    let countries = [];
    let indicesMeta = [];
    let dataSources = {};
    let activeTab = 'ram';
    let ramSelected = new Set();    // ISO codes selected on RAM map
    let indicesSelected = new Set(); // ISO codes selected on Indices map
    let activeIndex = 'oxford';     // Currently displayed index
    let ramMap = null;
    let indicesMap = null;
    let ramRadarChart = null;
    let ramBarChart = null;
    let indicesBarChart = null;
    let indicesScatterChart = null;

    const DATA_FILES = {
        'countries': 'data/countries.json',
        'indices-meta': 'data/indices-meta.json',
        'unesco-ram': 'data/unesco-ram.json',
        'imf-aipi': 'data/imf-aipi.json',
        'oxford': 'data/oxford-insights.json',
        'tortoise': 'data/tortoise.json',
        'girai': 'data/girai.json',
        'stanford-hai': 'data/stanford-hai.json',
        'world-bank': 'data/world-bank.json',
        'icesco': 'data/icesco.json',
        'oecd': 'data/oecd.json',
    };

    const RAM_DIMS = ['legalRegulatory', 'socialCultural', 'economic', 'scientificEducational', 'technologicalInfrastructural'];
    const RAM_DIM_LABELS = ['Legal & Regulatory', 'Social & Cultural', 'Economic', 'Scientific & Educational', 'Tech & Infrastructure'];
    const CHART_COLORS = [
        '#1A5C3A', '#4DC88E', '#0D3D2A', '#00B4D8', '#6366F1',
        '#F59E0B', '#EF4444', '#A855F7', '#EC4899', '#14B8A6'
    ];

    // ─── LOAD ───
    async function loadAll() {
        const entries = Object.entries(DATA_FILES);
        const results = await Promise.all(entries.map(([, url]) => fetch(url).then(r => r.json()).catch(() => null)));
        entries.forEach(([key], i) => { dataSources[key] = results[i]; });
        countries = dataSources['countries'] || [];
        indicesMeta = dataSources['indices-meta'] || [];
    }

    // ─── INIT ───
    async function init() {
        await loadAll();
        await MapView.loadBoundaries();

        // Hero stats
        const ram = dataSources['unesco-ram'];
        const ramCountries = ram?.countries || [];
        document.getElementById('stat-countries').textContent = countries.length;
        document.getElementById('stat-completed').textContent = ramCountries.filter(c => c.status === 'completed').length;
        document.getElementById('stat-inprocess').textContent = ramCountries.filter(c => c.status === 'inProcess' || c.status === 'inPreparation').length;
        document.getElementById('stat-indices').textContent = indicesMeta.length || 9;

        // Tab switching
        document.querySelectorAll('.nav-tab:not(.disabled)').forEach(tab => {
            tab.addEventListener('click', () => switchTab(tab.dataset.tab));
        });

        // Init RAM tab
        initRAMTab();

        // Populate RAM dim select
        const ramDimSel = document.getElementById('ram-dim-select');
        RAM_DIMS.forEach((d, i) => {
            const opt = document.createElement('option');
            opt.value = d; opt.textContent = RAM_DIM_LABELS[i];
            ramDimSel.appendChild(opt);
        });
        ramDimSel.addEventListener('change', renderRAMBar);

        // RAM stats
        renderRAMStats();

        // Sources
        renderSources();
    }

    function switchTab(tab) {
        activeTab = tab;
        document.querySelectorAll('.nav-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.toggle('active', c.id === `tab-${tab}`));

        // Lazy init indices tab
        if (tab === 'indices' && !indicesMap) {
            initIndicesTab();
        }

        // Leaflet needs invalidateSize after tab show
        setTimeout(() => {
            if (tab === 'ram') document.getElementById('ram-map')?._leaflet_id && null;
            if (tab === 'indices') document.getElementById('indices-map')?._leaflet_id && null;
        }, 100);
    }

    // ─── RAM TAB ───
    function initRAMTab() {
        MapView.init('ram-map');

        const ram = dataSources['unesco-ram'];
        const ramCountryMap = {};
        (ram?.countries || []).forEach(c => { ramCountryMap[c.iso] = c; });

        MapView.render(
            // Color function
            (iso) => {
                const rc = ramCountryMap[iso];
                return rc ? MapView.ramStatusColor(rc.status) : MapView.STATUS_COLORS.none;
            },
            // Tooltip function
            (iso, name, nameAr) => {
                const rc = ramCountryMap[iso];
                const status = rc ? rc.status.replace('inProcess', 'In Process').replace('inPreparation', 'In Preparation').replace('completed', 'Completed') : 'Not Assessed';
                const color = rc ? MapView.ramStatusColor(rc.status) : '#999';
                return `<strong>${name}</strong><br><span style="font-family:Cairo">${nameAr}</span><br><span style="color:${color}">● ${status}</span>`;
            },
            // Click handler
            (iso, name, nameAr) => {
                if (ramSelected.has(iso)) {
                    ramSelected.delete(iso);
                } else {
                    if (ramSelected.size >= 8) return; // Max 8
                    ramSelected.add(iso);
                }
                MapView.setSelected(ramSelected);
                renderRAMSelectedBar();
                renderRAMRadar();
                renderRAMBar();
                renderRAMCountryCards();
            }
        );
    }

    function renderRAMSelectedBar() {
        const bar = document.getElementById('ram-selected-bar');
        if (ramSelected.size === 0) {
            bar.innerHTML = '<p class="empty-msg">Click countries on the map to select them for comparison</p>';
            return;
        }
        const ram = dataSources['unesco-ram'];
        bar.innerHTML = Array.from(ramSelected).map(iso => {
            const c = countries.find(x => x.iso === iso);
            const name = c?.name || iso;
            return `<span class="selected-country-chip" onclick="App.deselectRAM('${iso}')">${name} <span class="remove">✕</span></span>`;
        }).join('');
    }

    function renderRAMRadar() {
        const el = document.getElementById('ram-radar');
        const empty = document.getElementById('ram-radar-empty');
        if (ramSelected.size === 0) {
            empty.style.display = 'block';
            if (ramRadarChart) { ramRadarChart.destroy(); ramRadarChart = null; }
            return;
        }
        empty.style.display = 'none';

        const ram = dataSources['unesco-ram'];
        const datasets = [];
        let i = 0;
        ramSelected.forEach(iso => {
            const rc = ram?.countries?.find(c => c.iso === iso);
            if (!rc?.dimensions) return;
            const c = countries.find(x => x.iso === iso);
            const color = CHART_COLORS[i % CHART_COLORS.length];
            datasets.push({
                label: c?.name || iso,
                data: RAM_DIMS.map(d => rc.dimensions[d] || 0),
                backgroundColor: color + '22',
                borderColor: color,
                borderWidth: 2,
                pointBackgroundColor: color,
                pointBorderColor: '#fff',
            });
            i++;
        });

        if (ramRadarChart) ramRadarChart.destroy();
        ramRadarChart = new Chart(el, {
            type: 'radar',
            data: { labels: RAM_DIM_LABELS, datasets },
            options: {
                responsive: true, maintainAspectRatio: true,
                animation: { duration: 300 },
                scales: { r: { min: 0, max: 5, ticks: { stepSize: 1, backdropColor: 'transparent', color: '#5a6d64' }, pointLabels: { font: { size: 11 }, color: '#0D3D2A' }, grid: { color: 'rgba(13,61,42,0.1)' } } },
                plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, padding: 16, color: '#0D3D2A', font: { size: 11 } } } }
            }
        });
    }

    function renderRAMBar() {
        const el = document.getElementById('ram-bar');
        const dim = document.getElementById('ram-dim-select')?.value || RAM_DIMS[0];
        const ram = dataSources['unesco-ram'];
        const completed = (ram?.countries || []).filter(c => c.status === 'completed' && c.dimensions);
        const dimIdx = RAM_DIMS.indexOf(dim);

        const sorted = completed.map(c => ({
            name: countries.find(x => x.iso === c.iso)?.name || c.iso,
            iso: c.iso,
            value: c.dimensions[dim] || 0
        })).sort((a, b) => b.value - a.value);

        if (ramBarChart) ramBarChart.destroy();
        ramBarChart = new Chart(el, {
            type: 'bar',
            data: {
                labels: sorted.map(s => s.name),
                datasets: [{
                    data: sorted.map(s => s.value),
                    backgroundColor: sorted.map(s => ramSelected.has(s.iso) ? '#1A5C3A' : '#4DC88E'),
                    borderRadius: 4,
                }]
            },
            options: {
                responsive: true, indexAxis: 'y',
                animation: { duration: 300 },
                scales: { x: { min: 0, max: 5, ticks: { stepSize: 1 } } },
                plugins: { legend: { display: false } }
            }
        });
    }

    function renderRAMCountryCards() {
        const container = document.getElementById('ram-country-cards');
        if (ramSelected.size === 0) {
            container.innerHTML = '<p class="empty-msg">Select countries on the map to see their assessment details</p>';
            return;
        }
        const ram = dataSources['unesco-ram'];
        let html = '';
        ramSelected.forEach(iso => {
            const rc = ram?.countries?.find(c => c.iso === iso);
            const c = countries.find(x => x.iso === iso);
            if (!rc || !c) return;

            const statusColors = { completed: '#10b981', inProcess: '#f59e0b', inPreparation: '#6366f1' };
            const statusLabel = rc.status.replace('inProcess', 'In Process').replace('inPreparation', 'In Preparation').replace('completed', 'Completed');
            const statusColor = statusColors[rc.status] || '#999';

            html += `<div class="country-card">
                <h3>${c.name}</h3>
                <p class="name-ar">${c.nameAr || ''}</p>
                <span class="status-badge" style="background:${statusColor}22;color:${statusColor}">${statusLabel}</span>`;

            if (rc.dimensions) {
                RAM_DIMS.forEach((d, i) => {
                    const val = rc.dimensions[d];
                    if (val != null) {
                        const pct = (val / 5) * 100;
                        html += `<div class="dim-bar"><div class="dim-bar-label"><span>${RAM_DIM_LABELS[i]}</span><span>${val}/5</span></div><div class="dim-bar-track"><div class="dim-bar-fill" style="width:${pct}%"></div></div></div>`;
                    }
                });
            }

            if (rc.keyFindings?.length) {
                html += `<ul class="findings-list">`;
                rc.keyFindings.slice(0, 5).forEach(f => { html += `<li>${f}</li>`; });
                html += `</ul>`;
            }

            if (rc.ramUrl) {
                html += `<p style="margin-top:12px"><a href="${rc.ramUrl}" target="_blank" style="font-size:0.82rem">View full UNESCO RAM profile →</a></p>`;
            }
            html += `</div>`;
        });
        container.innerHTML = html;
    }

    function renderRAMStats() {
        const ram = dataSources['unesco-ram'];
        const rc = ram?.countries || [];
        const completed = rc.filter(c => c.status === 'completed').length;
        const inProcess = rc.filter(c => c.status === 'inProcess').length;
        const inPrep = rc.filter(c => c.status === 'inPreparation').length;
        const total = rc.length;

        const grid = document.getElementById('ram-stats-grid');
        grid.innerHTML = `
            <div class="stat-card"><div class="stat-num" style="color:#10b981">${completed}</div><div class="stat-label">Completed</div></div>
            <div class="stat-card"><div class="stat-num" style="color:#f59e0b">${inProcess}</div><div class="stat-label">In Process</div></div>
            <div class="stat-card"><div class="stat-num" style="color:#6366f1">${inPrep}</div><div class="stat-label">In Preparation</div></div>
            <div class="stat-card"><div class="stat-num" style="color:var(--primary)">${total}</div><div class="stat-label">Total Countries</div></div>
            <div class="stat-card"><div class="stat-num" style="color:var(--text-muted)">${countries.length - total}</div><div class="stat-label">Not Yet Assessed</div></div>
        `;
    }

    // ─── INDICES TAB ───
    function initIndicesTab() {
        // Create second map instance
        const mapEl = document.getElementById('indices-map');
        indicesMap = L.map(mapEl, {
            center: [25, 20], zoom: 2, minZoom: 2, maxZoom: 7,
            worldCopyJump: true, scrollWheelZoom: true,
        });
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
            attribution: '© CARTO', subdomains: 'abcd', maxZoom: 19
        }).addTo(indicesMap);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png', {
            subdomains: 'abcd', maxZoom: 19, pane: 'overlayPane'
        }).addTo(indicesMap);

        // Index selector buttons
        renderIndexSelector();

        // Scatter selects
        const scatterX = document.getElementById('scatter-x-select');
        const scatterY = document.getElementById('scatter-y-select');
        indicesMeta.forEach(idx => {
            [scatterX, scatterY].forEach(sel => {
                const opt = document.createElement('option');
                opt.value = idx.id; opt.textContent = idx.name;
                sel.appendChild(opt);
            });
        });
        if (scatterY.options.length > 1) scatterY.selectedIndex = 1;
        scatterX.addEventListener('change', renderIndicesScatter);
        scatterY.addEventListener('change', renderIndicesScatter);

        // Render map with default index
        renderIndicesMap();

        // Coverage
        renderCoverage();
    }

    function renderIndexSelector() {
        const container = document.getElementById('index-selector-bar');
        container.innerHTML = indicesMeta.map(idx => {
            const cls = idx.id === activeIndex ? 'index-btn active' : 'index-btn';
            return `<button class="${cls}" data-idx="${idx.id}" onclick="App.selectIndex('${idx.id}')">${idx.name}</button>`;
        }).join('');
    }

    function selectIndex(id) {
        activeIndex = id;
        renderIndexSelector();
        renderIndicesMap();
    }

    function getIndexScore(indexId, iso) {
        const src = dataSources[indexId];
        if (!src) return null;
        const arr = src.countries || src.data || [];
        const found = arr.find(c => c.iso === iso);
        if (!found) return null;
        return found.score ?? found.overall ?? found.composite ?? null;
    }

    function renderIndicesMap() {
        if (!indicesMap) return;

        // Remove old geo layer
        indicesMap.eachLayer(layer => {
            if (layer instanceof L.GeoJSON) indicesMap.removeLayer(layer);
        });

        fetch('data/world-boundaries.json').then(r => r.json()).then(geo => {
            L.geoJSON(geo, {
                style: (feature) => {
                    const iso = feature.properties.iso;
                    const score = getIndexScore(activeIndex, iso);
                    const isSelected = indicesSelected.has(iso);
                    return {
                        fillColor: MapView.scoreToGreen(score),
                        weight: isSelected ? 3 : 0.8,
                        color: isSelected ? '#4DC88E' : '#fff',
                        fillOpacity: isSelected ? 0.9 : 0.7,
                    };
                },
                onEachFeature: (feature, layer) => {
                    const iso = feature.properties.iso;
                    const name = feature.properties.name;
                    const nameAr = feature.properties.nameAr;
                    const score = getIndexScore(activeIndex, iso);
                    const scoreStr = score != null ? `Score: ${(score * 100).toFixed(0)}` : 'No data';
                    const idxMeta = indicesMeta.find(m => m.id === activeIndex);

                    layer.bindTooltip(`<strong>${name}</strong><br><span style="font-family:Cairo">${nameAr}</span><br>${idxMeta?.name || ''}: ${scoreStr}`, { sticky: true });

                    layer.on('click', () => {
                        if (indicesSelected.has(iso)) {
                            indicesSelected.delete(iso);
                        } else {
                            if (indicesSelected.size >= 10) return;
                            indicesSelected.add(iso);
                        }
                        renderIndicesMap(); // Re-render for selection highlight
                        renderIndicesSelectedBar();
                        renderIndicesBar();
                        renderIndicesScatter();
                    });

                    layer.on('mouseover', e => { e.target.setStyle({ weight: 2, color: '#1A5C3A', fillOpacity: 0.85 }); e.target.bringToFront(); });
                    layer.on('mouseout', e => { if (!indicesSelected.has(iso)) layer.setStyle({ weight: 0.8, color: '#fff', fillOpacity: 0.7 }); });
                }
            }).addTo(indicesMap);
        });
    }

    function renderIndicesSelectedBar() {
        const bar = document.getElementById('indices-selected-bar');
        if (indicesSelected.size === 0) {
            bar.innerHTML = '<p class="empty-msg">Click countries on the map to select them for comparison</p>';
            return;
        }
        bar.innerHTML = Array.from(indicesSelected).map(iso => {
            const c = countries.find(x => x.iso === iso);
            return `<span class="selected-country-chip" onclick="App.deselectIndex('${iso}')">${c?.name || iso} <span class="remove">✕</span></span>`;
        }).join('');
    }

    function renderIndicesBar() {
        const el = document.getElementById('indices-bar');
        const empty = document.getElementById('indices-bar-empty');

        if (indicesSelected.size === 0) {
            if (empty) empty.style.display = 'block';
            if (indicesBarChart) { indicesBarChart.destroy(); indicesBarChart = null; }
            return;
        }
        if (empty) empty.style.display = 'none';

        // For each selected country, show scores across all indices
        const selectedArr = Array.from(indicesSelected);
        const indexIds = indicesMeta.map(m => m.id);
        const datasets = selectedArr.map((iso, i) => {
            const c = countries.find(x => x.iso === iso);
            return {
                label: c?.name || iso,
                data: indexIds.map(idx => {
                    const score = getIndexScore(idx, iso);
                    return score != null ? +(score * 100).toFixed(1) : null;
                }),
                backgroundColor: CHART_COLORS[i % CHART_COLORS.length] + 'CC',
                borderRadius: 4,
            };
        });

        if (indicesBarChart) indicesBarChart.destroy();
        indicesBarChart = new Chart(el, {
            type: 'bar',
            data: { labels: indexIds.map(id => { const m = indicesMeta.find(x => x.id === id); return m?.name || id; }), datasets },
            options: {
                responsive: true, animation: { duration: 300 },
                scales: { y: { min: 0, max: 100, title: { display: true, text: 'Score (0-100)' } } },
                plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, font: { size: 11 } } } }
            }
        });
    }

    function renderIndicesScatter() {
        const el = document.getElementById('indices-scatter');
        const xIdx = document.getElementById('scatter-x-select')?.value;
        const yIdx = document.getElementById('scatter-y-select')?.value;
        if (!xIdx || !yIdx) return;

        // Get all countries with both scores
        const points = countries.map(c => {
            const x = getIndexScore(xIdx, c.iso);
            const y = getIndexScore(yIdx, c.iso);
            if (x == null || y == null) return null;
            return { x: +(x * 100).toFixed(1), y: +(y * 100).toFixed(1), name: c.name, iso: c.iso };
        }).filter(Boolean);

        const xMeta = indicesMeta.find(m => m.id === xIdx);
        const yMeta = indicesMeta.find(m => m.id === yIdx);

        if (indicesScatterChart) indicesScatterChart.destroy();
        indicesScatterChart = new Chart(el, {
            type: 'scatter',
            data: {
                datasets: [{
                    data: points,
                    backgroundColor: points.map(p => indicesSelected.has(p.iso) ? '#1A5C3A' : '#4DC88E88'),
                    pointRadius: points.map(p => indicesSelected.has(p.iso) ? 7 : 4),
                }]
            },
            options: {
                responsive: true, animation: { duration: 300 },
                scales: {
                    x: { min: 0, max: 100, title: { display: true, text: xMeta?.name || xIdx } },
                    y: { min: 0, max: 100, title: { display: true, text: yMeta?.name || yIdx } },
                },
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { label: (ctx) => `${ctx.raw.name}: (${ctx.raw.x}, ${ctx.raw.y})` } }
                }
            }
        });
    }

    function renderCoverage() {
        const cards = document.getElementById('coverage-cards');
        const matrix = document.getElementById('coverage-matrix');

        // Cards
        cards.innerHTML = indicesMeta.map(idx => {
            const src = dataSources[idx.id];
            const count = (src?.countries || src?.data || []).length;
            return `<div class="coverage-card"><div class="cov-num" style="color:${idx.color || 'var(--primary)'}">${count}</div><div class="cov-label">${idx.name}</div></div>`;
        }).join('');

        // Matrix (top 40 countries by coverage)
        const countryCoverage = countries.map(c => {
            let covered = 0;
            indicesMeta.forEach(idx => {
                const src = dataSources[idx.id];
                const arr = src?.countries || src?.data || [];
                if (arr.find(x => x.iso === c.iso)) covered++;
            });
            return { ...c, covered };
        }).filter(c => c.covered > 0).sort((a, b) => b.covered - a.covered).slice(0, 50);

        let tableHtml = `<table><thead><tr><th>Country</th>`;
        indicesMeta.forEach(idx => { tableHtml += `<th style="font-size:0.7rem">${idx.name?.split(' ')[0] || idx.id}</th>`; });
        tableHtml += `</tr></thead><tbody>`;

        countryCoverage.forEach(c => {
            tableHtml += `<tr><td><strong>${c.name}</strong></td>`;
            indicesMeta.forEach(idx => {
                const src = dataSources[idx.id];
                const arr = src?.countries || src?.data || [];
                const found = arr.find(x => x.iso === c.iso);
                if (found) {
                    const score = found.score ?? found.overall ?? found.composite ?? null;
                    const display = score != null ? (score * 100).toFixed(0) : '✓';
                    const bg = score != null ? MapView.scoreToGreen(score) : '#d1fae5';
                    tableHtml += `<td style="text-align:center;background:${bg}20;font-size:0.75rem;font-weight:600">${display}</td>`;
                } else {
                    tableHtml += `<td style="text-align:center;color:#ccc">—</td>`;
                }
            });
            tableHtml += `</tr>`;
        });
        tableHtml += `</tbody></table>`;
        matrix.innerHTML = tableHtml;
    }

    // ─── SOURCES ───
    function renderSources() {
        const grid = document.getElementById('sources-grid');
        const sources = [
            { name: 'UNESCO RAM', org: 'UNESCO', url: 'https://www.unesco.org/ethics-ai/en/global-hub', desc: 'Readiness Assessment Methodology — qualitative country assessments across 5 dimensions' },
            { name: 'Oxford Insights', org: 'Oxford Insights', url: 'https://oxfordinsights.com/ai-readiness/', desc: 'Government AI Readiness Index — 188 countries, 40 indicators' },
            { name: 'IMF AIPI', org: 'IMF', url: 'https://www.imf.org/external/datamapper/datasets/AIPI', desc: 'AI Preparedness Index — 174 economies, 4 dimensions' },
            { name: 'Tortoise Global AI', org: 'Tortoise Media', url: 'https://www.tortoisemedia.com/data/global-ai', desc: '83 countries, 122 indicators, 7 pillars' },
            { name: 'GIRAI', org: 'Global Center on AI Governance', url: 'https://www.global-index.ai/', desc: 'Global Index on Responsible AI — 138 countries, human rights benchmarks' },
            { name: 'Stanford HAI', org: 'Stanford University', url: 'https://aiindex.stanford.edu/', desc: 'AI Index Report + Global AI Vibrancy Tool' },
            { name: 'World Bank', org: 'World Bank', url: 'https://www.worldbank.org/en/publication/dptr2025-ai-foundations', desc: 'Digital Progress & Trends — 4Cs framework for AI foundations' },
            { name: 'ICESCO', org: 'ICESCO', url: 'https://icesco.org', desc: 'AI Index for the Islamic World — Riyadh Charter implementation' },
            { name: 'OECD AI', org: 'OECD', url: 'https://oecd.ai', desc: 'AI Policy Observatory — policy tracking & AI incidents' },
        ];

        grid.innerHTML = sources.map(s => `
            <div class="source-card">
                <h4>${s.name}</h4>
                <p>${s.desc}</p>
                <a href="${s.url}" target="_blank">${s.org} →</a>
            </div>
        `).join('');
    }

    // ─── PUBLIC API ───
    function deselectRAM(iso) {
        ramSelected.delete(iso);
        MapView.setSelected(ramSelected);
        renderRAMSelectedBar();
        renderRAMRadar();
        renderRAMBar();
        renderRAMCountryCards();
    }

    function deselectIndex(iso) {
        indicesSelected.delete(iso);
        renderIndicesMap();
        renderIndicesSelectedBar();
        renderIndicesBar();
        renderIndicesScatter();
    }

    // Start
    document.addEventListener('DOMContentLoaded', init);

    return { deselectRAM, deselectIndex, selectIndex };
})();
