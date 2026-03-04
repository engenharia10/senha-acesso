(function () {
  const STORAGE_KEY = 'alfatronic_validation_device_seed';

  function getOrCreateSeed() {
    let seed = localStorage.getItem(STORAGE_KEY);
    if (!seed) {
      if (crypto && crypto.randomUUID) {
        seed = crypto.randomUUID();
      } else {
        seed = String(Date.now()) + '-' + String(Math.random()).slice(2);
      }
      localStorage.setItem(STORAGE_KEY, seed);
    }
    return seed;
  }

  function collectFingerprint() {
    const nav = navigator;
    const scr = window.screen || {};
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '';

    return {
      seed: getOrCreateSeed(),
      userAgent: nav.userAgent || '',
      platform: nav.platform || '',
      language: nav.language || '',
      languages: (nav.languages || []).join(','),
      maxTouchPoints: String(nav.maxTouchPoints || 0),
      hardwareConcurrency: String(nav.hardwareConcurrency || 0),
      deviceMemory: String(nav.deviceMemory || 0),
      timezone: tz,
      screen: [scr.width || 0, scr.height || 0, scr.colorDepth || 0].join('x')
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
    const fp = collectFingerprint();
    const plain = Object.keys(fp).sort().map(function (k) {
      return k + '=' + fp[k];
    }).join('|');

    const hash = await hashSha256(plain);
    const deviceNumber = deviceNumberFromHash(hash);

    return {
      app: 'Alfatronic',
      type: 'validation',
      version: 1,
      generated_at: new Date().toISOString(),
      device_number: deviceNumber,
      fingerprint_sha256: hash,
      activation_code: getCurrentActivationCode(),
      fingerprint: fp
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

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addValidationButton);
  } else {
    addValidationButton();
  }
})();
