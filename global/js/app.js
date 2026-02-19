// app.js — Main application logic for ICAIRE Global AI Readiness Monitor

const App = (() => {
    // ── STATE ──
    let countries = [];
    let indicesMeta = [];
    let dataSources = {};
    let selectedForRadar = []; // [{iso, name, ...}]

    const DATA_FILES = {
        'countries':     'data/countries.json',
        'indices-meta':  'data/indices-meta.json',
        'unesco-ram':    'data/unesco-ram.json',
        'imf-aipi':      'data/imf-aipi.json',
        'oxford':        'data/oxford-insights.json',
        'tortoise':      'data/tortoise.json',
        'girai':         'data/girai.json',
        'stanford-hai':  'data/stanford-hai.json',
        'world-bank':    'data/world-bank.json',
        'icesco':        'data/icesco.json',
        'oecd':          'data/oecd.json',
    };

    // ── LOAD DATA ──
    async function loadAll() {
        const entries = Object.entries(DATA_FILES);
        const results = await Promise.all(entries.map(([, url]) => fetch(url).then(r => r.json())));
        entries.forEach(([key], i) => { dataSources[key] = results[i]; });
        countries = dataSources['countries'];
        indicesMeta = dataSources['indices-meta'];
    }

    // ── INIT ──
    async function init() {
        await loadAll();

        // Hero stat
        document.getElementById('stat-countries').textContent = countries.length;

        // Index selector
        Filters.renderIndexSelector(document.getElementById('index-selector-bar'), indicesMeta);

        // Filter bars
        Filters.renderFilterBars(document.getElementById('filter-bar'));

        // Map
        MapView.init('map-container');
        renderMap();

        // Wire filter changes
        Filters.onChange(() => {
            renderMap();
            renderBarChart();
            renderScatterChart();
            Filters.renderFilterBars(document.getElementById('filter-bar'));
            Filters.renderIndexSelector(document.getElementById('index-selector-bar'), indicesMeta);
        });

        // Populate dimension selects
        populateDimensionSelects();

        // Bar chart default
        renderBarChart();

        // Scatter chart default
        renderScatterChart();

        // Country search
        setupSearch();

        // Sources grid
        renderSources();

        // Gap analysis
        renderGapAnalysis();

        // Modal close
        document.getElementById('modal-close').onclick = closeModal;
        document.getElementById('country-modal').onclick = e => { if (e.target === e.currentTarget) closeModal(); };

        // Scroll nav + scroll-top
        setupScroll();
    }

    // ── MAP ──
    function getFilteredCountries() {
        return Filters.filterCountries(countries);
    }

    function renderMap() {
        const filtered = getFilteredCountries();
        MapView.render(filtered, dataSources['unesco-ram'], openCountryModal);
    }

    // ── COUNTRY MODAL ──
    function openCountryModal(country) {
        const modal = document.getElementById('country-modal');
        document.getElementById('modal-country-name').textContent = country.name;
        document.getElementById('modal-country-name-ar').textContent = country.nameAr || '';

        const body = document.getElementById('modal-body');
        let html = '';

        // Region & memberships
        html += `<div class="modal-section"><h4>Region & Memberships</h4>
            <div class="modal-badges"><span class="modal-badge">${country.region}</span>`;
        if (country.memberships) {
            Object.keys(country.memberships).forEach(m => {
                if (country.memberships[m]) html += `<span class="modal-badge">${m.toUpperCase()}</span>`;
            });
        }
        html += `</div></div>`;

        // UNESCO RAM
        const ram = dataSources['unesco-ram']?.countries?.find(c => c.iso === country.iso);
        if (ram) {
            const statusCls = `status-${ram.status}`;
            const statusLabel = ram.status === 'completed' ? 'Completed' : ram.status === 'inProcess' ? 'In Process' : 'In Preparation';
            html += `<div class="modal-section"><h4>UNESCO RAM Assessment</h4>
                <div class="modal-badges"><span class="modal-badge ${statusCls}">${statusLabel}</span></div>`;
            if (ram.dimensions) {
                html += `<div style="margin-top:12px;">`;
                Charts.DIMENSION_KEYS.forEach((k, i) => {
                    const val = ram.dimensions[k];
                    if (val != null) {
                        const pct = (val / 5) * 100;
                        html += `<div style="margin-bottom:8px;"><div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:3px;"><span>${Charts.DIMENSION_LABELS[i]}</span><span>${val}/5</span></div>
                        <div style="background:rgba(13,61,42,0.08);border-radius:4px;height:8px;"><div style="background:var(--accent);height:100%;border-radius:4px;width:${pct}%"></div></div></div>`;
                    }
                });
                html += `</div>`;
            }
            if (ram.keyFindings?.length) {
                html += `<ul class="findings-list" style="margin-top:12px;">`;
                ram.keyFindings.forEach(f => { html += `<li>${f}</li>`; });
                html += `</ul>`;
            }
            html += `</div>`;
        }

        // Other indices presence
        const otherIndices = [];
        indicesMeta.forEach(idx => {
            if (idx.id === 'unesco-ram') return;
            const src = dataSources[idx.id];
            if (!src) return;
            const arr = src.countries || src.data || [];
            const found = arr.find(c => c.iso === country.iso);
            if (found) {
                let score = found.score ?? found.overall ?? found.composite ?? null;
                otherIndices.push({ name: idx.name, color: idx.color, score });
            }
        });
        if (otherIndices.length) {
            html += `<div class="modal-section"><h4>Other Index Coverage</h4><div class="modal-badges">`;
            otherIndices.forEach(oi => {
                const scoreStr = oi.score != null ? ` (${oi.score})` : '';
                html += `<span class="modal-badge" style="border-left:3px solid ${oi.color}">${oi.name}${scoreStr}</span>`;
            });
            html += `</div></div>`;
        }

        body.innerHTML = html;
        modal.classList.add('show');
    }

    function closeModal() {
        document.getElementById('country-modal').classList.remove('show');
    }

    // ── DIMENSION SELECTS ──
    function populateDimensionSelects() {
        const barSel = document.getElementById('bar-dimension-select');
        const scatterX = document.getElementById('scatter-x-select');
        const scatterY = document.getElementById('scatter-y-select');

        Charts.DIMENSION_KEYS.forEach((k, i) => {
            const lbl = Charts.DIMENSION_LABELS[i];
            [barSel, scatterX, scatterY].forEach(sel => {
                const opt = document.createElement('option');
                opt.value = k;
                opt.textContent = lbl;
                sel.appendChild(opt);
            });
        });

        // Defaults: scatter Y = second dimension
        if (scatterY.options.length > 1) scatterY.selectedIndex = 1;

        barSel.onchange = renderBarChart;
        scatterX.onchange = renderScatterChart;
        scatterY.onchange = renderScatterChart;
    }

    // ── BAR CHART ──
    function renderBarChart() {
        const dimKey = document.getElementById('bar-dimension-select').value || Charts.DIMENSION_KEYS[0];
        const filtered = getFilteredCountries();
        Charts.renderBar('bar-chart', filtered, dataSources['unesco-ram'], dimKey);
    }

    // ── SCATTER ──
    function renderScatterChart() {
        const dimX = document.getElementById('scatter-x-select').value || Charts.DIMENSION_KEYS[0];
        const dimY = document.getElementById('scatter-y-select').value || Charts.DIMENSION_KEYS[1];
        const filtered = getFilteredCountries();
        Charts.renderScatter('scatter-chart', filtered, dataSources['unesco-ram'], dimX, dimY);
    }

    // ── RADAR SEARCH ──
    function setupSearch() {
        const input = document.getElementById('country-search');
        const results = document.getElementById('search-results');

        input.addEventListener('input', () => {
            const q = input.value.trim().toLowerCase();
            if (q.length < 1) { results.classList.remove('show'); return; }
            // Filter countries with RAM data that aren't already selected
            const ramCountries = dataSources['unesco-ram'].countries.map(r => r.iso);
            const matches = countries.filter(c =>
                ramCountries.includes(c.iso) &&
                !selectedForRadar.find(s => s.iso === c.iso) &&
                (c.name.toLowerCase().includes(q) || c.nameAr?.includes(q) || c.iso.toLowerCase().includes(q))
            ).slice(0, 8);

            if (matches.length === 0) { results.classList.remove('show'); return; }
            results.innerHTML = matches.map(c =>
                `<div class="search-result-item" data-iso="${c.iso}"><span>${c.name}</span><span class="region-tag">${c.region}</span></div>`
            ).join('');
            results.classList.add('show');

            results.querySelectorAll('.search-result-item').forEach(el => {
                el.onclick = () => {
                    const iso = el.dataset.iso;
                    const country = countries.find(c => c.iso === iso);
                    if (country && selectedForRadar.length < 10) {
                        selectedForRadar.push(country);
                        input.value = '';
                        results.classList.remove('show');
                        renderRadarSection();
                    }
                };
            });
        });

        // Close on outside click
        document.addEventListener('click', e => {
            if (!e.target.closest('.search-box')) results.classList.remove('show');
        });
    }

    function renderRadarSection() {
        const container = document.getElementById('selected-countries');
        const emptyEl = document.getElementById('radar-empty');

        container.innerHTML = selectedForRadar.map((c, i) => {
            const color = Charts.COLORS[i % Charts.COLORS.length].border;
            return `<span class="selected-tag" style="background:${color}" data-iso="${c.iso}">${c.name} <span class="remove">&times;</span></span>`;
        }).join('');

        container.querySelectorAll('.selected-tag .remove').forEach(btn => {
            btn.onclick = () => {
                const iso = btn.parentElement.dataset.iso;
                selectedForRadar = selectedForRadar.filter(c => c.iso !== iso);
                renderRadarSection();
            };
        });

        if (selectedForRadar.length === 0) {
            emptyEl.style.display = 'block';
        } else {
            emptyEl.style.display = 'none';
            Charts.renderRadar('radar-chart', selectedForRadar, dataSources['unesco-ram']);
        }
    }

    // ── GAP ANALYSIS ──
    function renderGapAnalysis() {
        const cardsEl = document.getElementById('gap-cards');
        const matrixEl = document.getElementById('gap-matrix');
        const totalCountries = countries.length;

        // Cards
        cardsEl.innerHTML = indicesMeta.map(idx => {
            const pct = Math.round((idx.coverage / totalCountries) * 100);
            return `<div class="gap-card">
                <h4>${idx.name}</h4>
                <div class="coverage">${idx.coverage}</div>
                <div class="desc">${pct}% of ${totalCountries} countries covered</div>
            </div>`;
        }).join('');

        // Matrix: sample countries (those with RAM data) × indices
        const ramISOs = dataSources['unesco-ram'].countries.map(c => c.iso);
        const sampleCountries = countries.filter(c => ramISOs.includes(c.iso)).slice(0, 20);

        let tableHTML = `<table><thead><tr><th>Country</th>`;
        indicesMeta.forEach(idx => { tableHTML += `<th>${idx.name}</th>`; });
        tableHTML += `</tr></thead><tbody>`;

        sampleCountries.forEach(c => {
            tableHTML += `<tr><td style="text-align:left;color:var(--white);font-weight:500;">${c.name}</td>`;
            indicesMeta.forEach(idx => {
                const src = dataSources[idx.id];
                const arr = src?.countries || src?.data || [];
                const found = arr.find(r => r.iso === c.iso);
                tableHTML += `<td><span class="dot ${found ? 'yes' : 'no'}"></span></td>`;
            });
            tableHTML += `</tr>`;
        });

        tableHTML += `</tbody></table>`;
        matrixEl.innerHTML = tableHTML;
    }

    // ── SOURCES ──
    function renderSources() {
        const grid = document.getElementById('sources-grid');
        const icons = { 'unesco-ram': '🏛️', 'stanford-hai': '🎓', 'tortoise': '🐢', 'oxford': '📊', 'girai': '⚖️', 'imf-aipi': '💰', 'world-bank': '🌍', 'icesco': '🕌', 'oecd': '📈' };
        grid.innerHTML = indicesMeta.map(idx =>
            `<div class="source-card"><a href="${idx.url}" target="_blank" rel="noopener">
                <div class="source-icon">${icons[idx.id] || '📋'}</div>
                <div class="source-info"><h4>${idx.fullName}</h4><span>${idx.org} · ${idx.year} · ${idx.coverage} countries</span></div>
            </a></div>`
        ).join('');
    }

    // ── SCROLL ──
    function setupScroll() {
        const nav = document.getElementById('navbar');
        const scrollBtn = document.getElementById('scroll-top');
        window.addEventListener('scroll', () => {
            nav.classList.toggle('scrolled', window.scrollY > 80);
            scrollBtn.classList.toggle('visible', window.scrollY > 400);
        }, { passive: true });
    }

    // ── BOOT ──
    document.addEventListener('DOMContentLoaded', init);

    return { init };
})();
