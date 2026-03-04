(function () {
  const ACT_CODE_KEY = 'alfatronic_activation_code_manual';
  let userEditedActivationCode = false;

  function sanitize6(value) {
    return (value || '').replace(/\D/g, '').slice(0, 6);
  }

  function saveActivationCode(value) {
    const digits = sanitize6(value);
    if (digits) {
      localStorage.setItem(ACT_CODE_KEY, digits);
    } else {
      localStorage.removeItem(ACT_CODE_KEY);
    }
  }

  function forceBlankActivationCode() {
    const el = document.getElementById('display-codigo');
    if (!el || userEditedActivationCode) return;
    el.textContent = '      ';
  }

  function clearInputValues() {
    ['input-contra', 'input-senha6'].forEach(function (id) {
      const el = document.getElementById(id);
      if (!el) return;
      if (el.value !== '') {
        el.value = '';
        el.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
  }

  function enableEditableActivationCode() {
    const el = document.getElementById('display-codigo');
    if (!el) return;

    el.contentEditable = 'true';
    el.setAttribute('role', 'textbox');
    el.setAttribute('aria-label', 'Codigo de ativacao editavel');

    if (el.dataset.editableReady === '1') return;
    el.dataset.editableReady = '1';

    el.addEventListener('input', function () {
      const digits = sanitize6(el.textContent);
      userEditedActivationCode = digits.length > 0;
      el.textContent = digits ? digits.padStart(6, '0') : '      ';
      saveActivationCode(digits);
    });

    el.addEventListener('focus', function () {
      if (!userEditedActivationCode) {
        el.textContent = '';
      }
    });

    el.addEventListener('blur', function () {
      const digits = sanitize6(el.textContent);
      userEditedActivationCode = digits.length > 0;
      el.textContent = digits ? digits.padStart(6, '0') : '      ';
      saveActivationCode(digits);
    });
  }

  function installAntiAutofillWatcher() {
    const target = document.getElementById('display-codigo');
    if (!target) return;

    const obs = new MutationObserver(function () {
      if (userEditedActivationCode) return;
      const digits = sanitize6(target.textContent);
      if (digits) {
        target.textContent = '      ';
      }
    });

    obs.observe(target, { childList: true, characterData: true, subtree: true });
  }

  function applyBlankState() {
    enableEditableActivationCode();
    forceBlankActivationCode();
    clearInputValues();
  }

  function start() {
    applyBlankState();
    installAntiAutofillWatcher();

    // app.js ainda tenta preencher após init; reaplica blank por alguns ciclos.
    [120, 350, 700, 1200, 2000, 3000].forEach(function (ms) {
      setTimeout(applyBlankState, ms);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
