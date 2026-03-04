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

  function collectBrowserNumbers() {
    const nav = navigator;
    const scr = window.screen || {};

    return {
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
  }

  function deviceNumberFromBrowser() {
    const data = collectBrowserNumbers();
    const source = Object.keys(data).sort().map(function (k) {
      return k + '=' + data[k];
    }).join('|');

    const h1 = BigInt(simpleNumberHash(source + '|a'));
    const h2 = BigInt(simpleNumberHash(source + '|b'));
    const merged = (h1 << 32n) | h2;
    const device12 = (merged % 1000000000000n).toString().padStart(12, '0');

    return {
      device_number: device12,
      browser_numbers: data,
      source_hash: String(simpleNumberHash(source))
    };
  }

  function getCurrentActivationCode() {
    const el = document.getElementById('display-codigo');
    if (!el) return null;
    const value = (el.textContent || '').replace(/\D/g, '');
    return value.length ? value : null;
  }

  function buildValidationObject() {
    const dev = deviceNumberFromBrowser();
    return {
      app: 'Alfatronic',
      type: 'validation',
      version: 3,
      generated_at: new Date().toISOString(),
      device_number: dev.device_number,
      source_hash: dev.source_hash,
      activation_code: getCurrentActivationCode(),
      browser_numbers: dev.browser_numbers
    };
  }

  function downloadJsonFile(filename, obj) {
    const json = JSON.stringify(obj, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function addValidationButton() {
    const btn = document.createElement('button');
    btn.id = 'btn-validation-file';
    btn.type = 'button';
    btn.textContent = 'Baixar validacao';

    Object.assign(btn.style, {
      position: 'fixed',
      right: '16px',
      bottom: '16px',
      zIndex: '11000',
      border: 'none',
      borderRadius: '999px',
      padding: '12px 16px',
      fontSize: '12px',
      fontWeight: '700',
      letterSpacing: '0.3px',
      color: '#fff',
      background: '#E67E22',
      boxShadow: '0 8px 18px rgba(0,0,0,0.35)',
      cursor: 'pointer'
    });

    btn.addEventListener('click', function () {
      try {
        const payload = buildValidationObject();
        const filename = 'validacao-' + payload.device_number + '.json';
        downloadJsonFile(filename, payload);
      } catch (err) {
        console.error(err);
      }
    });

    document.body.appendChild(btn);
  }

  function fillFieldsOnOpen() {
    try {
      const payload = buildValidationObject();
      const auto6 = payload.device_number.slice(-6);

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
    addValidationButton();
    fillFieldsOnOpen();
    setTimeout(fillFieldsOnOpen, 400);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
