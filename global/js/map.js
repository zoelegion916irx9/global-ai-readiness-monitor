// map.js — Choropleth world map with Leaflet

const MapView = (() => {
    let map = null;
    let geoLayer = null;
    let boundariesData = null;
    let currentColorFn = null;
    let onCountryClickFn = null;
    let selectedCountries = new Set();

    const STATUS_COLORS = {
        completed: '#10b981',
        inProcess: '#f59e0b',
        inPreparation: '#6366f1',
        none: '#d1d5db'
    };

    // Color scales for index scores (0-1 range)
    function scoreToColor(score) {
        if (score == null) return '#e5e7eb';
        // Green gradient: light → dark
        const r = Math.round(230 - score * 200);
        const g = Math.round(240 - score * 80);
        const b = Math.round(230 - score * 180);
        return `rgb(${r},${g},${b})`;
    }

    function scoreToGreen(score) {
        if (score == null) return '#e5e7eb';
        if (score >= 0.8) return '#065f46';
        if (score >= 0.6) return '#10b981';
        if (score >= 0.4) return '#4DC88E';
        if (score >= 0.2) return '#a7f3d0';
        return '#d1fae5';
    }

    // RAM status color
    function ramStatusColor(status) {
        return STATUS_COLORS[status] || STATUS_COLORS.none;
    }

    async function loadBoundaries() {
        const resp = await fetch('data/world-boundaries.json');
        boundariesData = await resp.json();
    }

    function init(containerId) {
        map = L.map(containerId, {
            center: [25, 20],
            zoom: 2,
            minZoom: 2,
            maxZoom: 7,
            worldCopyJump: true,
            scrollWheelZoom: true,
            zoomControl: true,
        });

        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
            attribution: '© <a href="https://carto.com/">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(map);

        // Labels on top
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png', {
            subdomains: 'abcd',
            maxZoom: 19,
            pane: 'overlayPane'
        }).addTo(map);
    }

    function render(colorFn, tooltipFn, onCountryClick) {
        currentColorFn = colorFn;
        onCountryClickFn = onCountryClick;

        if (geoLayer) {
            map.removeLayer(geoLayer);
        }

        if (!boundariesData) return;

        geoLayer = L.geoJSON(boundariesData, {
            style: (feature) => {
                const iso = feature.properties.iso;
                const isSelected = selectedCountries.has(iso);
                return {
                    fillColor: colorFn(iso),
                    weight: isSelected ? 3 : 0.8,
                    opacity: 1,
                    color: isSelected ? '#4DC88E' : '#fff',
                    fillOpacity: isSelected ? 0.9 : 0.7,
                };
            },
            onEachFeature: (feature, layer) => {
                const iso = feature.properties.iso;
                const name = feature.properties.name;
                const nameAr = feature.properties.nameAr;

                // Tooltip
                const tip = tooltipFn ? tooltipFn(iso, name, nameAr) : `<strong>${name}</strong>`;
                layer.bindTooltip(tip, { sticky: true, direction: 'top' });

                // Click handler
                layer.on('click', () => {
                    if (onCountryClick) onCountryClick(iso, name, nameAr);
                });

                // Hover
                layer.on('mouseover', (e) => {
                    e.target.setStyle({ weight: 2, color: '#1A5C3A', fillOpacity: 0.85 });
                    e.target.bringToFront();
                });
                layer.on('mouseout', (e) => {
                    geoLayer.resetStyle(e.target);
                });
            }
        }).addTo(map);
    }

    function setSelected(isoSet) {
        selectedCountries = isoSet;
        if (geoLayer && currentColorFn) {
            geoLayer.eachLayer(layer => {
                const iso = layer.feature?.properties?.iso;
                if (iso) {
                    const isSelected = selectedCountries.has(iso);
                    layer.setStyle({
                        weight: isSelected ? 3 : 0.8,
                        color: isSelected ? '#4DC88E' : '#fff',
                        fillOpacity: isSelected ? 0.9 : 0.7,
                    });
                }
            });
        }
    }

    function fitToRegion(bounds) {
        if (map && bounds) map.fitBounds(bounds, { padding: [30, 30], maxZoom: 5 });
    }

    function resetView() {
        if (map) map.setView([25, 20], 2);
    }

    return {
        init, loadBoundaries, render, setSelected, fitToRegion, resetView,
        STATUS_COLORS, ramStatusColor, scoreToColor, scoreToGreen
    };
})();
