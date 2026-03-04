(function () {
  const STORAGE_KEY = 'alfatronic_validation_device_seed_num';

  function generateNumericSeed() {
    const arr = new Uint32Array(2);
    crypto.getRandomValues(arr);
    const a = String(arr[0]).padStart(10, '0');
    const b = String(arr[1]).padStart(10, '0');
    return (a + b).slice(0, 16);
  }

  function getOrCreateSeed() {
    let seed = localStorage.getItem(STORAGE_KEY);
    if (!seed || !/^\d{8,20}$/.test(seed)) {
      seed = generateNumericSeed();
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
    return String(h >>> 0);
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
      language_num: simpleNumberHash(nav.language || ''),
      ua_num: simpleNumberHash(nav.userAgent || ''),
      platform_num: simpleNumberHash(nav.platform || '')
    };
  }

  function toHex(bytes) {
    return Array.from(bytes).map(function (b) {
      return b.toString(16).padStart(2, '0');
    }).join('');
  }

  async function hashSha256(text) {
    const data = new TextEncoder().encode(text);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    return toHex(new Uint8Array(hashBuffer));
  }

  function deviceNumberFromHash(hashHex) {
    const n = BigInt('0x' + hashHex.slice(0, 16));
    const mod = n % 1000000000000n;
    return mod.toString().padStart(12, '0');
  }

  function getCurrentActivationCode() {
    const el = document.getElementById('display-codigo');
    if (!el) return null;
    const value = (el.textContent || '').replace(/\D/g, '');
    return value.length ? value : null;
  }

  async function buildValidationObject() {
    const browserNumbers = collectBrowserNumbers();
    const source = Object.keys(browserNumbers).sort().map(function (k) {
      return k + '=' + browserNumbers[k];
    }).join('|');

    const hash = await hashSha256(source);
    const deviceNumber = deviceNumberFromHash(hash);

    return {
      app: 'Alfatronic',
      type: 'validation',
      version: 2,
      generated_at: new Date().toISOString(),
      device_number: deviceNumber,
      fingerprint_sha256: hash,
      activation_code: getCurrentActivationCode(),
      browser_numbers: browserNumbers
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

    btn.addEventListener('click', async function () {
      btn.disabled = true;
      const old = btn.textContent;
      btn.textContent = 'Gerando...';
      try {
        const payload = await buildValidationObject();
        const filename = 'validacao-' + payload.device_number + '.json';
        downloadJsonFile(filename, payload);
        btn.textContent = 'Arquivo gerado';
        setTimeout(function () {
          btn.textContent = old;
          btn.disabled = false;
        }, 1200);
      } catch (err) {
        console.error(err);
        btn.textContent = 'Falha ao gerar';
        setTimeout(function () {
          btn.textContent = old;
          btn.disabled = false;
        }, 1400);
      }
    });

    document.body.appendChild(btn);
  }

  async function fillFieldsOnOpen() {
    try {
      const payload = await buildValidationObject();
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
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
