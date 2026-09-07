const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const vm = require('node:vm');
const source = readFileSync(require('node:path').join(__dirname, '../static/js/hero-atmosphere.js'), 'utf8');

async function boot({ reduced = false, saveData = false, hidden = false, visible = true } = {}) {
    const host = { dataset: { threeUrl: '/three.js' }, isConnected: true };
    const toggle = { hidden: true, addEventListener() {} };
    let imports = 0;
    const warnings = [];
    const context = vm.createContext({
        document: {
            hidden,
            getElementById: id => id === 'hero-atmosphere' ? host : toggle,
            addEventListener() {},
        },
        window: { addEventListener() {}, mukoPageReady: Promise.resolve() },
        navigator: { connection: { saveData, addEventListener() {} } },
        matchMedia: query => ({ matches: query.includes('reduced-motion') && reduced, addEventListener() {} }),
        IntersectionObserver: class { constructor(callback) { this.callback = callback; } observe() { this.callback([{ isIntersecting: visible }]); } },
        console: { warn: (...args) => warnings.push(args) },
        // Only the optional module boundary is substituted; browser/GPU rendering
        // is covered in the local preview, while these tests check loading policy.
        loadThree: async () => { imports++; throw new Error('Simulated unsupported graphics'); },
    });
    vm.runInContext(source.replace('import(host.dataset.threeUrl)', 'loadThree()'), context);
    await new Promise(resolve => setImmediate(resolve));
    return { host, toggle, imports, warnings };
}

for (const [name, options] of [
    ['reduced-motion preference', { reduced: true }],
    ['data-saving preference', { saveData: true }],
    ['offscreen hero', { visible: false }],
    ['background tab', { hidden: true }],
]) {
    test(`does not download Three.js for ${name}`, async () => {
        const result = await boot(options);
        assert.equal(result.imports, 0);
        assert.equal(result.host.dataset.state, 'static');
        assert.equal(result.toggle.hidden, true);
        assert.equal(result.warnings.length, 0);
    });
}

test('graphics failure leaves static artwork and hides the motion control', async () => {
    const result = await boot();
    assert.equal(result.imports, 1);
    assert.equal(result.host.dataset.state, 'static');
    assert.equal(result.toggle.hidden, true);
    assert.equal(result.warnings.length, 1);
});
