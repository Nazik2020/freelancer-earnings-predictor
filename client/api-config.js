/**
 * Finds a running Flask API (prefers port 5001 — fixed build 3.0.0).
 */
window.probeApiBase = async function () {
    for (const port of [5001, 5000]) {
        const base = 'http://127.0.0.1:' + port;
        try {
            const r = await fetch(base + '/health', { cache: 'no-store' });
            if (!r.ok) continue;
            const health = await r.json();
            return { base: base, health: health };
        } catch (e) {
            /* try next port */
        }
    }
    return null;
};
