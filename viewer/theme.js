(function () {
  'use strict';
  var KEY = 'designsprache.theme';
  var preference = 'system';
  function normalize(value) { return ['light','dark'].includes(value) ? value : 'system'; }
  function readPreference() {
    try { return normalize(window.localStorage.getItem(KEY)); }
    catch (error) { return preference; }
  }
  function apply(value) {
    preference = normalize(value);
    // CSS follows live system changes while this attribute is "system".
    document.documentElement.dataset.theme = preference;
    document.querySelectorAll('[data-theme-choice]').forEach(function(button) {
      button.setAttribute('aria-pressed',String(button.dataset.themeChoice === preference));
    });
  }
  // Run in the head, before the first paint, on every entry page.
  apply(readPreference());
  document.addEventListener('DOMContentLoaded',function() {
    document.querySelectorAll('[data-theme-controls]').forEach(function(group) { group.hidden = false; });
    document.querySelectorAll('[data-theme-choice]').forEach(function(button) {
      button.addEventListener('click',function() {
        apply(button.dataset.themeChoice);
        try { window.localStorage.setItem(KEY,preference); } catch (error) { /* Switching still works. */ }
      });
    });
    apply(preference);
  });
  // Keep open tabs and pages restored from the back/forward cache in sync.
  window.addEventListener('storage',function(event) {
    if (event.key !== KEY && event.key !== null) return;
    if (event.storageArea && event.storageArea !== window.localStorage) return;
    apply(event.newValue);
  });
  window.addEventListener('pageshow',function(event) {
    if (event.persisted) apply(readPreference());
  });
})();
