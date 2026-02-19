// map.js — Leaflet world map

const MapView = (() => {
    let map = null;
    let markers = [];
    let geoLayer = null;

    const STATUS_COLORS = {
        completed: '#10b981',
        inProcess: '#f59e0b',
        inPreparation: '#6366f1',
        none: '#94a3b8'
    };

    function init(containerId) {
        map = L.map(containerId, {
            center: [20, 20],
            zoom: 2,
            minZoom: 2,
            maxZoom: 6,
            worldCopyJump: true,
            scrollWheelZoom: true,
        });

        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(map);

        // Add labels layer on top
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png', {
            subdomains: 'abcd',
            maxZoom: 19,
            pane: 'overlayPane'
        }).addTo(map);
    }

    function getRAMStatus(iso, ramData) {
        if (!ramData) return null;
        const entry = ramData.countries.find(c => c.iso === iso);
        return entry ? entry.status : null;
    }

    function render(countries, ramData, onCountryClick) {
        clearMarkers();

        countries.forEach(c => {
            const status = getRAMStatus(c.iso, ramData);
            const color = STATUS_COLORS[status] || STATUS_COLORS.none;

            const marker = L.circleMarker([c.lat, c.lng], {
                radius: status === 'completed' ? 8 : 6,
                fillColor: color,
                color: '#fff',
                weight: 1.5,
                opacity: 1,
                fillOpacity: 0.85
            }).addTo(map);

            const statusLabel = status ? status.replace('inProcess', 'In Process').replace('inPreparation', 'In Preparation') : 'Not assessed';

            marker.bindTooltip(`
                <strong>${c.name}</strong><br>
                <span style="font-family:Cairo,sans-serif">${c.nameAr}</span><br>
                <span style="color:${color}">● ${statusLabel}</span><br>
                <em>${c.region}</em>
            `, { direction: 'top', offset: [0, -8] });

            marker.on('click', () => onCountryClick(c));
            markers.push(marker);
        });
    }

    function clearMarkers() {
        markers.forEach(m => m.remove());
        markers = [];
    }

    function fitToCountries(countries) {
        if (!map || countries.length === 0) return;
        const bounds = L.latLngBounds(countries.map(c => [c.lat, c.lng]));
        map.fitBounds(bounds, { padding: [30, 30], maxZoom: 5 });
    }

    function resetView() {
        if (map) map.setView([20, 20], 2);
    }

    return { init, render, fitToCountries, resetView, STATUS_COLORS };
})();
