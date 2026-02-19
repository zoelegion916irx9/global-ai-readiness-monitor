// charts.js — Chart.js configurations

const Charts = (() => {
    const COLORS = [
        { bg: 'rgba(26,92,58,0.2)', border: '#1A5C3A' },
        { bg: 'rgba(77,200,142,0.2)', border: '#4DC88E' },
        { bg: 'rgba(13,61,42,0.2)', border: '#0D3D2A' },
        { bg: 'rgba(0,180,216,0.2)', border: '#00B4D8' },
        { bg: 'rgba(99,102,241,0.2)', border: '#6366F1' },
        { bg: 'rgba(245,158,11,0.2)', border: '#F59E0B' },
        { bg: 'rgba(239,68,68,0.2)', border: '#EF4444' },
        { bg: 'rgba(168,85,247,0.2)', border: '#A855F7' },
        { bg: 'rgba(236,72,153,0.2)', border: '#EC4899' },
        { bg: 'rgba(20,184,166,0.2)', border: '#14B8A6' },
    ];

    let radarChart = null;
    let barChart = null;
    let scatterChart = null;

    const DIMENSION_LABELS = [
        'Legal & Regulatory',
        'Social & Cultural',
        'Economic',
        'Scientific & Educational',
        'Technological & Infrastructural'
    ];
    const DIMENSION_KEYS = ['legalRegulatory', 'socialCultural', 'economic', 'scientificEducational', 'technologicalInfrastructural'];

    // ── RADAR ──
    function renderRadar(canvasId, selectedCountries, ramData) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;
        if (radarChart) radarChart.destroy();

        const datasets = selectedCountries.map((c, i) => {
            const ram = ramData.countries.find(r => r.iso === c.iso);
            if (!ram || !ram.dimensions) return null;
            const color = COLORS[i % COLORS.length];
            return {
                label: c.name,
                data: DIMENSION_KEYS.map(k => ram.dimensions[k]),
                backgroundColor: color.bg,
                borderColor: color.border,
                borderWidth: 2,
                pointBackgroundColor: color.border,
                pointBorderColor: '#fff',
                pointRadius: 4,
            };
        }).filter(Boolean);

        radarChart = new Chart(ctx, {
            type: 'radar',
            data: { labels: DIMENSION_LABELS, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                animation: { duration: 400 },
                scales: {
                    r: {
                        min: 0, max: 5,
                        ticks: { stepSize: 1, backdropColor: 'transparent', color: '#5a6d64', font: { size: 10 } },
                        pointLabels: { font: { size: 11, weight: '500' }, color: '#0D3D2A' },
                        grid: { color: 'rgba(13,61,42,0.1)' },
                        angleLines: { color: 'rgba(13,61,42,0.1)' }
                    }
                },
                plugins: {
                    legend: { display: true, position: 'bottom', labels: { usePointStyle: true, padding: 16, font: { size: 12 } } },
                    tooltip: {
                        callbacks: {
                            label: ctx => `${ctx.dataset.label}: ${ctx.raw}/5`
                        }
                    }
                }
            }
        });
    }

    // ── BAR ──
    function renderBar(canvasId, countries, ramData, dimensionKey) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;
        if (barChart) barChart.destroy();

        const dimLabel = DIMENSION_LABELS[DIMENSION_KEYS.indexOf(dimensionKey)] || dimensionKey;

        // Get countries with RAM data for this dimension
        const items = countries.map(c => {
            const ram = ramData.countries.find(r => r.iso === c.iso);
            return ram?.dimensions ? { name: c.name, value: ram.dimensions[dimensionKey] } : null;
        }).filter(Boolean).sort((a, b) => b.value - a.value);

        barChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: items.map(i => i.name),
                datasets: [{
                    label: dimLabel,
                    data: items.map(i => i.value),
                    backgroundColor: items.map((_, i) => COLORS[i % COLORS.length].bg),
                    borderColor: items.map((_, i) => COLORS[i % COLORS.length].border),
                    borderWidth: 1.5,
                    borderRadius: 4,
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                scales: {
                    x: { min: 0, max: 5, ticks: { stepSize: 1 }, grid: { color: 'rgba(13,61,42,0.06)' } },
                    y: { grid: { display: false } }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { label: ctx => `${dimLabel}: ${ctx.raw}/5` } }
                }
            }
        });
    }

    // ── SCATTER ──
    function renderScatter(canvasId, countries, ramData, dimX, dimY) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;
        if (scatterChart) scatterChart.destroy();

        const xLabel = DIMENSION_LABELS[DIMENSION_KEYS.indexOf(dimX)];
        const yLabel = DIMENSION_LABELS[DIMENSION_KEYS.indexOf(dimY)];

        const points = countries.map(c => {
            const ram = ramData.countries.find(r => r.iso === c.iso);
            if (!ram?.dimensions) return null;
            return { x: ram.dimensions[dimX], y: ram.dimensions[dimY], label: c.name };
        }).filter(Boolean);

        scatterChart = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: `${xLabel} vs ${yLabel}`,
                    data: points,
                    backgroundColor: COLORS.map(c => c.border),
                    pointRadius: 8,
                    pointHoverRadius: 12,
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: { min: 0, max: 5, title: { display: true, text: xLabel, font: { weight: '600' } }, grid: { color: 'rgba(13,61,42,0.06)' } },
                    y: { min: 0, max: 5, title: { display: true, text: yLabel, font: { weight: '600' } }, grid: { color: 'rgba(13,61,42,0.06)' } }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => {
                                const pt = ctx.raw;
                                return `${pt.label}: (${pt.x}, ${pt.y})`;
                            }
                        }
                    }
                }
            }
        });
    }

    return { renderRadar, renderBar, renderScatter, COLORS, DIMENSION_LABELS, DIMENSION_KEYS };
})();
