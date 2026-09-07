// Progressive enhancement. The portrait and all content work without WebGL.
const host = document.getElementById('hero-atmosphere');
const hero = document.getElementById('home');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const compact = matchMedia('(max-width: 767px)');
const finePointer = matchMedia('(pointer: fine)');
const connection = navigator.connection;
let sceneHandle;
let importing = false;
let failed = false;
let visible = false;
let observer;

function eligible() {
    return !reducedMotion.matches && !connection?.saveData;
}

async function sync() {
    if (!host || failed) return;
    if (!eligible()) {
        sceneHandle?.dispose();
        sceneHandle = undefined;
        host.dataset.state = 'static';
        return;
    }
    if (!sceneHandle && !importing && visible && !document.hidden) {
        importing = true;
        try {
            const THREE = await import(host.dataset.threeUrl);
            if (eligible() && host.isConnected) sceneHandle = createAtmosphere(THREE);
        } catch (error) {
            // Graphics are optional; leave the static glow and usable page intact.
            failed = true;
            host.dataset.state = 'static';
            console.warn('Hero atmosphere unavailable; using static artwork.', error);
        } finally {
            importing = false;
        }
    }
    if (sceneHandle) {
        sceneHandle.setRunning(visible && !document.hidden);
    }
}

function createAtmosphere(THREE) {
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: false, powerPreference: 'low-power' });
    renderer.setClearColor(0x000000, 0);
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, 1, .1, 40);
    camera.position.z = 9;
    const group = new THREE.Group();
    scene.add(group);
    const resources = [];
    const track = resource => { resources.push(resource); return resource; };

    // Deterministic positions; one draw call for the entire particle field.
    const positions = new Float32Array(170 * 3);
    let seed = 73;
    const random = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
    for (let i = 0; i < positions.length; i += 3) {
        const angle = random() * Math.PI * 2;
        const radius = 2.1 + random() * 1.6;
        positions[i] = Math.cos(angle) * radius;
        positions[i + 1] = Math.sin(angle) * radius;
        positions[i + 2] = (random() - .5) * 3;
    }
    const geometry = track(new THREE.BufferGeometry());
    const resting = positions.slice();
    // Follow with a soft body position, then add each fly's own flight locally.
    // Keeping these separate prevents the spring from smoothing away its buzz.
    const centers = positions.slice();
    const flight = Array.from({ length: positions.length / 3 }, () => ({
        phase: random() * Math.PI * 2,
        orbit: (2.5 + random() * 5) * (random() > .5 ? 1 : -1),
        radius: .035 + random() * .09,
        flutter: 13 + random() * 12,
        eagerness: .7 + random() * .7,
    }));
    const velocity = new Float32Array(positions.length);
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const material = track(new THREE.ShaderMaterial({
        uniforms: { tint: { value: new THREE.Color(0xff5544) } },
        vertexShader: `void main() {
            vec4 p = modelViewMatrix * vec4(position, 1.0);
            gl_Position = projectionMatrix * p;
            gl_PointSize = clamp(44.0 / -p.z, 2.0, 7.0);
        }`,
        fragmentShader: `uniform vec3 tint;
        void main() {
            float d = length(gl_PointCoord - vec2(0.5));
            float glow = 1.0 - smoothstep(0.05, 0.5, d);
            gl_FragColor = vec4(tint, glow * 0.7);
        }`,
        transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    }));
    const particles = new THREE.Points(geometry, material);
    particles.frustumCulled = false;
    group.add(particles);
    const target = new THREE.Vector2();
    let following = false;
    let mode = 'drift';
    let scatterUntil = 0;
    let frame = 0;
    let running = false;
    let last = 0;
    let elapsed = 0;
    let disposed = false;
    let portrait = { x: .68, y: .47, rx: .2, ry: .38 };

    function updatePortrait() {
        const image = document.getElementById('hero-bg');
        const rect = host.getBoundingClientRect();
        if (!image?.naturalWidth || !rect.width || !rect.height) return;
        // Map the face in the source photograph through object-fit: cover,
        // including the portrait's responsive crop and existing parallax.
        const imageRect = image.getBoundingClientRect();
        const scale = Math.max(imageRect.width / image.naturalWidth, imageRect.height / image.naturalHeight);
        const width = image.naturalWidth * scale;
        const height = image.naturalHeight * scale;
        const objectPosition = getComputedStyle(image).objectPosition.split(' ').map(parseFloat);
        portrait = {
            x: (imageRect.left - rect.left + (imageRect.width - width) * objectPosition[0] / 100 + width * .65) / rect.width,
            y: (imageRect.top - rect.top + (imageRect.height - height) * objectPosition[1] / 100 + height * .47) / rect.height,
            rx: width * .18 / rect.width,
            ry: height * .36 / rect.height,
        };
        host.style.setProperty('--portrait-x', `${portrait.x * 100}%`);
        host.style.setProperty('--portrait-y', `${portrait.y * 100}%`);
        host.style.setProperty('--portrait-rx', `${portrait.rx * rect.width}px`);
        host.style.setProperty('--portrait-ry', `${portrait.ry * rect.height}px`);
    }

    function render() { renderer.render(scene, camera); }
    function resize() {
        const { width, height } = host.getBoundingClientRect();
        if (!width || !height) return;
        renderer.setPixelRatio(Math.min(devicePixelRatio || 1, compact.matches ? 1 : 1.5));
        renderer.setSize(width, height, false);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        group.position.set(compact.matches ? 0 : 1.9, compact.matches ? 1.1 : 0, 0);
        group.scale.setScalar(compact.matches ? .67 : 1);
        geometry.setDrawRange(0, compact.matches ? 65 : 170);
        updatePortrait();
        render();
    }
    function tick(now) {
        if (!running || disposed) return;
        frame = requestAnimationFrame(tick);
        const delta = now - last;
        if (delta < (compact.matches ? 1000 / 24 : 1000 / 30)) return;
        const dt = Math.min(delta, 50) / 1000;
        elapsed += dt;
        last = now;
        if (mode === 'scatter' && elapsed >= scatterUntil) mode = following ? 'follow' : 'drift';
        host.dataset.interaction = mode;
        const halfHeight = Math.tan(camera.fov * Math.PI / 360) * camera.position.z;
        const centerX = (target.x * halfHeight * camera.aspect - group.position.x) / group.scale.x;
        const centerY = (target.y * halfHeight - group.position.y) / group.scale.y;
        const attracted = following || mode === 'gather';
        const spread = mode === 'gather' ? .09 : .42;
        const spring = mode === 'scatter' ? .35 : mode === 'gather' ? 18 : 7;
        const damping = Math.exp(-(mode === 'scatter' ? 1.6 : 4.5) * dt);
        for (let i = 0; i < positions.length; i += 3) {
            const fly = flight[i / 3];
            const phase = fly.phase;
            const pulse = Math.sin(elapsed * 1.1 + phase);
            // A slow individual wander breaks up the fixed formation, while
            // small elliptical loops and faster flutter keep even a still swarm alive.
            const wander = attracted ? (mode === 'gather' ? .04 : .18) : .1;
            const destinations = [
                (attracted ? centerX + resting[i] * spread : resting[i] + pulse * .25) + Math.sin(elapsed * fly.eagerness * 2 + phase) * wander,
                (attracted ? centerY + resting[i + 1] * spread : resting[i + 1] + Math.cos(elapsed * .8 + phase) * .25) + Math.cos(elapsed * fly.eagerness * 1.7 + phase) * wander,
                resting[i + 2] * (attracted ? spread : 1),
            ];
            for (let axis = 0; axis < 3; axis++) {
                const index = i + axis;
                velocity[index] = (velocity[index] + (destinations[axis] - centers[index]) * spring * fly.eagerness * dt) * damping;
                centers[index] += velocity[index] * dt;
                positions[index] = centers[index];
            }
            const angle = elapsed * fly.orbit + phase;
            const radius = fly.radius * (mode === 'gather' ? .55 : 1);
            const buzz = radius * .35;
            positions[i] += Math.cos(angle) * radius + Math.sin(elapsed * fly.flutter + phase) * buzz;
            positions[i + 1] += Math.sin(angle) * radius * .7 + Math.cos(elapsed * fly.flutter * .83 + phase * 2) * buzz;
            // No Z flutter or point-size changes: movement never pumps dot sizes.
        }
        geometry.attributes.position.needsUpdate = true;
        updatePortrait();
        // Measure the visible dots themselves, not the mouse: scattered dots
        // continue lighting the portrait until they actually travel away.
        let proximity = 0;
        const count = compact.matches ? 65 : 170;
        for (let i = 0; i < count * 3; i += 3) {
            const depth = camera.position.z - positions[i + 2] * group.scale.z;
            const h = Math.tan(camera.fov * Math.PI / 360) * depth;
            const x = .5 + (positions[i] * group.scale.x + group.position.x) / (2 * h * camera.aspect);
            const y = .5 - (positions[i + 1] * group.scale.y + group.position.y) / (2 * h);
            if (x < 0 || x > 1 || y < 0 || y > 1) continue;
            const distance = Math.hypot((x - portrait.x) / portrait.rx, (y - portrait.y) / portrait.ry);
            proximity += Math.max(0, 1 - distance) ** 2;
        }
        host.style.setProperty('--portrait-glow', Math.min(1, proximity / count * 5).toFixed(3));
        render();
    }
    function setRunning(value) {
        host.dataset.state = value ? 'running' : 'paused';
        if (running === value) return;
        running = value;
        cancelAnimationFrame(frame);
        if (value) { last = performance.now(); frame = requestAnimationFrame(tick); }
    }
    function locate(event) {
        const rect = hero.getBoundingClientRect();
        target.set((event.clientX - rect.left) / rect.width * 2 - 1, 1 - (event.clientY - rect.top) / rect.height * 2);
    }
    function point(event) {
        if (!finePointer.matches || event.pointerType === 'touch' || !running) return;
        locate(event);
        following = true;
        if (mode === 'drift') mode = 'follow';
    }
    function leave() { following = false; if (mode !== 'scatter') mode = 'drift'; }
    function interactive(event) {
        return event.target.closest('a, button, input, textarea, select, [role="button"]');
    }
    function scatter(event) {
        if (!running || interactive(event) || event.detail > 1) return;
        locate(event);
        mode = 'scatter';
        scatterUntil = elapsed + 1.4;
        for (let i = 0; i < velocity.length; i += 3) {
            const angle = random() * Math.PI * 2;
            const speed = 8 + random() * 9;
            velocity[i] = Math.cos(angle) * speed;
            velocity[i + 1] = Math.sin(angle) * speed;
            velocity[i + 2] = (random() - .5) * 3;
        }
    }
    function gather(event) {
        if (!running || interactive(event)) return;
        locate(event);
        mode = 'gather';
        velocity.fill(0);
    }
    function contextLost(event) {
        event.preventDefault();
        failed = true;
        dispose();
        sceneHandle = undefined;
        host.dataset.state = 'static';
    }
    const resizeObserver = new ResizeObserver(resize);
    function dispose() {
        if (disposed) return;
        disposed = true;
        host.style.setProperty('--portrait-glow', '0');
        cancelAnimationFrame(frame);
        resizeObserver.disconnect();
        hero.removeEventListener('pointermove', point);
        hero.removeEventListener('pointerleave', leave);
        hero.removeEventListener('click', scatter);
        hero.removeEventListener('dblclick', gather);
        renderer.domElement.removeEventListener('webglcontextlost', contextLost);
        resources.forEach(resource => resource.dispose());
        renderer.dispose();
        renderer.domElement.remove();
    }
    renderer.domElement.setAttribute('aria-hidden', 'true');
    host.append(renderer.domElement);
    renderer.domElement.addEventListener('webglcontextlost', contextLost);
    hero.addEventListener('pointermove', point, { passive: true });
    hero.addEventListener('pointerleave', leave);
    hero.addEventListener('click', scatter);
    hero.addEventListener('dblclick', gather);
    resizeObserver.observe(host);
    resize();
    return { setRunning, dispose };
}

if (host && hero) {
    host.dataset.state = 'static';
    reducedMotion.addEventListener('change', sync);
    connection?.addEventListener('change', sync);
    document.addEventListener('visibilitychange', sync);
    window.addEventListener('pagehide', () => {
        sceneHandle?.dispose();
        sceneHandle = undefined;
    });
    window.addEventListener('pageshow', sync);
    (window.mukoPageReady || Promise.resolve()).then(() => {
        observer = new IntersectionObserver(entries => {
            visible = entries[0].isIntersecting;
            sync();
        }, { threshold: .05 });
        observer.observe(hero);
    });
}
