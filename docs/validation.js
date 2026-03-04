(function () {
  const STORAGE_KEY = 'alfatronic_validation_device_seed_num';

  function getOrCreateSeed() {
    let seed = localStorage.getItem(STORAGE_KEY);
    if (!seed || !/^\d{8,20}$/.test(seed)) {
      const now = String(Date.now());
      const rnd = String(Math.floor(Math.random() * 1e10)).padStart(10, '0');
      seed = (now + rnd).slice(-16);
      localStorage.setItem(STORAGE_KEY, seed);
    }
    return seed;
  }

  function simpleNumberHash(text) {
    let h = 2166136261;
    for (let i = 0; i < text.length; i++) {
      h ^= text.charCodeAt(i);
      h += (h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24);
    }
    return h >>> 0;
  }

  function deviceNumberFromBrowser() {
    const nav = navigator;
    const scr = window.screen || {};

    const data = {
      seed: getOrCreateSeed(),
      screen_w: String(scr.width || 0),
      screen_h: String(scr.height || 0),
      color_depth: String(scr.colorDepth || 0),
      tz_offset_min: String(new Date().getTimezoneOffset()),
      max_touch: String(nav.maxTouchPoints || 0),
      hw_threads: String(nav.hardwareConcurrency || 0),
      device_mem_gb: String(nav.deviceMemory || 0),
      lang_hash: String(simpleNumberHash(nav.language || '')),
      ua_hash: String(simpleNumberHash(nav.userAgent || '')),
      platform_hash: String(simpleNumberHash(nav.platform || ''))
    };

    const source = Object.keys(data).sort().map(function (k) {
      return k + '=' + data[k];
    }).join('|');

    const h1 = BigInt(simpleNumberHash(source + '|a'));
    const h2 = BigInt(simpleNumberHash(source + '|b'));
    const merged = (h1 << 32n) | h2;

    return (merged % 1000000000000n).toString().padStart(12, '0');
  }

  function fillFieldsOnOpen() {
    try {
      const auto6 = deviceNumberFromBrowser().slice(-6);

      ['input-contra', 'input-senha6'].forEach(function (id) {
        const el = document.getElementById(id);
        if (!el) return;
        el.value = auto6;
        el.dispatchEvent(new Event('input', { bubbles: true }));
      });
    } catch (err) {
      console.error(err);
    }
  }

  function start() {
    fillFieldsOnOpen();
    setTimeout(fillFieldsOnOpen, 400);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
