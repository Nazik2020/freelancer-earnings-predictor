/**
 * API base resolver — tries Azure backend first, falls back to localhost for dev.
 */
window.probeApiBase = async function () {
    // Azure App Service backend (production)
    const azureBase = 'https://freelance-salary-api.azurewebsites.net';
    // Local dev fallback
    const localPorts = [5001, 5000];

    // Try Azure first
    try {
        const r = await fetch(azureBase + '/health', { cache: 'no-store' });
        if (r.ok) {
            const health = await r.json();
            return { base: azureBase, health: health };
        }
    } catch (e) { /* fall through to local */ }

    // Fallback: local dev server
    for (const port of localPorts) {
        const base = 'http://127.0.0.1:' + port;
        try {
            const r = await fetch(base + '/health', { cache: 'no-store' });
            if (!r.ok) continue;
            const health = await r.json();
            return { base: base, health: health };
        } catch (e) { /* try next port */ }
    }
    return null;
};
