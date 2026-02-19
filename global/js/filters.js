// filters.js — Global filter state and logic

const Filters = (() => {
    let state = {
        regions: new Set(),
        orgs: new Set(),
        indices: new Set(['unesco-ram']),
    };

    const listeners = [];

    const REGIONS = ['MENA', 'Africa', 'Asia-Pacific', 'Europe', 'Americas', 'SIDS'];
    const ORGS = [
        { id: 'oecd', label: 'OECD' },
        { id: 'oic', label: 'ICESCO/OIC' },
        { id: 'eu', label: 'EU' },
        { id: 'g20', label: 'G20' },
        { id: 'g7', label: 'G7' },
        { id: 'gpai', label: 'GPAI' },
        { id: 'brics', label: 'BRICS+' },
        { id: 'gcc', label: 'GCC' },
        { id: 'asean', label: 'ASEAN' },
        { id: 'au', label: 'AU' },
        { id: 'arabLeague', label: 'Arab League' },
    ];

    function onChange(fn) { listeners.push(fn); }
    function notify() { listeners.forEach(fn => fn(state)); }

    function toggleRegion(r) {
        state.regions.has(r) ? state.regions.delete(r) : state.regions.add(r);
        notify();
    }
    function toggleOrg(o) {
        state.orgs.has(o) ? state.orgs.delete(o) : state.orgs.add(o);
        notify();
    }
    function toggleIndex(idx) {
        state.indices.has(idx) ? state.indices.delete(idx) : state.indices.add(idx);
        notify();
    }

    function matchesCountry(country) {
        // If no filters, show all
        const regionMatch = state.regions.size === 0 || state.regions.has(country.region) ||
            (state.regions.has('SIDS') && country.memberships?.sids);
        const orgMatch = state.orgs.size === 0 || [...state.orgs].some(o => country.memberships?.[o]);
        return regionMatch && orgMatch;
    }

    function filterCountries(countries) {
        return countries.filter(matchesCountry);
    }

    function renderFilterBars(container) {
        container.innerHTML = '';

        // Region filters
        const regionRow = document.createElement('div');
        regionRow.className = 'filters-row';
        const regionLabel = document.createElement('span');
        regionLabel.className = 'filter-group-label';
        regionLabel.textContent = 'Region';
        regionRow.appendChild(regionLabel);
        REGIONS.forEach(r => {
            const btn = document.createElement('button');
            btn.className = 'filter-pill' + (state.regions.has(r) ? ' active' : '');
            btn.textContent = r;
            btn.onclick = () => { toggleRegion(r); renderFilterBars(container); };
            regionRow.appendChild(btn);
        });
        container.appendChild(regionRow);

        // Org filters
        const orgRow = document.createElement('div');
        orgRow.className = 'filters-row';
        const orgLabel = document.createElement('span');
        orgLabel.className = 'filter-group-label';
        orgLabel.textContent = 'Org';
        orgRow.appendChild(orgLabel);
        ORGS.forEach(({ id, label }) => {
            const btn = document.createElement('button');
            btn.className = 'filter-pill' + (state.orgs.has(id) ? ' active' : '');
            btn.textContent = label;
            btn.onclick = () => { toggleOrg(id); renderFilterBars(container); };
            orgRow.appendChild(btn);
        });
        container.appendChild(orgRow);
    }

    function renderIndexSelector(container, indicesMeta) {
        container.innerHTML = '';
        const row = document.createElement('div');
        row.className = 'filters-row';
        const lbl = document.createElement('span');
        lbl.className = 'filter-group-label';
        lbl.textContent = 'Index';
        row.appendChild(lbl);
        indicesMeta.forEach(idx => {
            const btn = document.createElement('button');
            btn.className = 'filter-pill' + (state.indices.has(idx.id) ? ' active' : '');
            btn.textContent = idx.name;
            btn.style.borderColor = state.indices.has(idx.id) ? idx.color : '';
            btn.style.color = state.indices.has(idx.id) ? idx.color : '';
            btn.onclick = () => { toggleIndex(idx.id); renderIndexSelector(container, indicesMeta); };
            row.appendChild(btn);
        });
        container.appendChild(row);
    }

    return { state, onChange, toggleRegion, toggleOrg, toggleIndex, matchesCountry, filterCountries, renderFilterBars, renderIndexSelector, REGIONS, ORGS };
})();
