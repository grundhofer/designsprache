  /* ---------- Mobile reference: renderer and session-only demo state ---------- */
  var MT = LANG === 'de' ? {
    projects:'Projekte', project:'Projekt', search:'Suchen', searchHint:'Projekt suchen …',
    active:'Aktiv', paused:'Pausiert', times:['vor 2 Std.','gestern','vor 4 Tagen'], now:'gerade eben',
    newProject:'Neues Projekt', create:'Projekt anlegen', import:'Importieren', back:'Zurück',
    name:'Projektname', nameHint:'Zum Beispiel: Atlas', status:'Status', updated:'Zuletzt geändert',
    description:'Beschreibung', descriptionText:'Ein gemeinsamer Ort für Aufgaben, Notizen und den nächsten Schritt.',
    optional:'Beschreibung (optional)', empty:'Keine Projekte gefunden.', cancel:'Abbrechen',
    demo:'Demo', local:'Änderungen gelten nur für diese Demo und werden beim Schließen zurückgesetzt.',
    shown:'sichtbar von', created:'Projekt angelegt.', imported:'Projekte importiert.',
    names:'Projektnamen, einer pro Zeile', importHint:'Atlas\nStudio', required:'Bitte einen Projektnamen eingeben.',
    reset:'Demo zurücksetzen', noteTitle:'Mobile Adaption', preview:'Mobile Demo',
    values:'Basiswerte der mobilen Demo', palette:'Palette des Stil-Faktenblatts',
    prompt:'Mobile Umsetzung', promptText:'Erstelle eine mobile Projektverwaltung mit Liste, eigener Detailansicht und Formular zum Anlegen. Nutze ein einspaltiges Layout, beschriftete Navigation und sichtbare Zurück-Aktionen. Diese Demo verwendet mindestens 48 CSS-px hohe Hauptaktionen und 16 CSS-px große Eingabeschrift als eigene Entwurfswerte, nicht als plattformübergreifende Norm. Übertrage diese Werte in die Einheiten und Konventionen der Zielplattform. Berücksichtige Bildschirmtastatur, Safe Areas, Textvergrößerung und schmale Displays. Verkleinere kein Desktop-Layout als Ganzes. Die folgenden mobilen Anpassungen haben bei Widersprüchen Vorrang vor den Desktop-Demowerten.'
  } : {
    projects:'Projects', project:'Project', search:'Search', searchHint:'Search projects …',
    active:'Active', paused:'Paused', times:['2 hrs ago','yesterday','4 days ago'], now:'just now',
    newProject:'New project', create:'Create project', import:'Import', back:'Back',
    name:'Project name', nameHint:'For example: Atlas', status:'Status', updated:'Last updated',
    description:'Description', descriptionText:'One shared place for tasks, notes and the next step.',
    optional:'Description (optional)', empty:'No projects found.', cancel:'Cancel',
    demo:'Demo', local:'Changes apply only to this demo and reset when you close the entry.',
    shown:'shown of', created:'Project created.', imported:'Projects imported.',
    names:'Project names, one per line', importHint:'Atlas\nStudio', required:'Please enter a project name.',
    reset:'Reset demo', noteTitle:'Mobile adaptation', preview:'Mobile demo',
    values:'Mobile demo base values', palette:'Fact-sheet palette',
    prompt:'Mobile implementation', promptText:'Build a mobile project manager with a list, a separate detail view and a creation form. Use a single-column layout, labeled navigation and visible back actions. This demo uses primary actions at least 48 CSS px high and 16 CSS px input text as authored design values, not a cross-platform standard. Translate these values into the target platform’s units and conventions. Account for the on-screen keyboard, safe areas, enlarged text and narrow displays. Do not shrink an entire desktop layout. Where they conflict, the following mobile adaptations take precedence over the desktop demo values.'
  };
  var mobileMode = false, mobileScreen = 'list', mobileState = null;

  function newMobileState(screen) {
    return { screen:screen || 'list', selected:0, query:'', message:'', projects:[
      {name:'Nexus', time:MT.times[0], status:'active', description:MT.descriptionText},
      {name:'Autowrite Studio', time:MT.times[1], status:'active', description:MT.descriptionText},
      {name:'Balance Ally', time:MT.times[2], status:'paused', description:MT.descriptionText}
    ] };
  }
  function mobileRows(state) {
    var rows = state.projects.map(function(p, i) { return {p:p, i:i}; }).filter(function(row) {
      return row.p.name.toLocaleLowerCase(LANG).includes(state.query.toLocaleLowerCase(LANG).trim());
    });
    return { count:rows.length, html:rows.map(function(row) {
      var p = row.p;
      return '<li><button type="button" class="m-project" data-m-project="' + row.i + '">'
        + '<b>' + esc(p.name) + '</b><span class="m-meta"><span>' + esc(p.time) + '</span>'
        + '<span class="m-status m-' + p.status + '">' + esc(MT[p.status]) + '</span></span>'
        + '<span class="m-chevron" aria-hidden="true">›</span></button></li>';
    }).join('') };
  }
  function mobileMarkup(slug, state) {
    var screen = state.screen, p = state.projects[state.selected], rows = mobileRows(state);
    var title = screen === 'list' ? MT.projects : screen === 'detail' ? p.name : screen === 'new' ? MT.newProject : MT.import;
    var button = function(action, text, cls) {
      return '<button type="button" class="' + cls + '" data-m-action="' + action + '">' + esc(text) + '</button>';
    };
    var out = '<div class="m-app m-' + slug + ' m-' + MOBILE_DATA[slug].layout + '" role="group" aria-label="'
      + esc(MT.preview + ': ' + DATA[slug].name) + '"><div class="m-top">'
      + (screen === 'list' ? '<span>' + esc(MT.projects) + ' / 01</span>' : button('list', '‹ ' + MT.back, 'm-back'))
      + '<span>' + esc(MT.demo) + '</span></div><div class="m-head"><h3 class="m-title" data-m-heading tabindex="-1">'
      + esc(title) + '</h3>' + (screen === 'list' ? '<span class="m-count">' + (state.projects.length + 9) + '</span>' : '') + '</div>';
    if (state.message) out += '<p class="m-message" role="status">' + esc(state.message) + '</p>';
    if (screen === 'list') {
      out += '<label class="m-search">' + esc(MT.search) + '<input type="search" name="mobile-search" value="'
        + esc(state.query) + '" placeholder="' + esc(MT.searchHint) + '" autocomplete="off"></label>'
        + '<ul class="m-list">' + rows.html + '</ul><p class="m-empty"' + (rows.count ? ' hidden' : '') + '>' + esc(MT.empty) + '</p>'
        + '<p class="m-caption" data-m-count aria-live="polite">' + rows.count + ' ' + esc(MT.shown) + ' ' + (state.projects.length + 9) + '</p>'
        + '<div class="m-actions">' + button('new', '+ ' + MT.newProject, 'm-primary') + button('import', MT.import, 'm-secondary') + '</div>';
    } else if (screen === 'detail') {
      out += '<dl class="m-detail"><div><dt>' + esc(MT.status) + '</dt><dd>' + esc(MT[p.status])
        + '</dd></div><div><dt>' + esc(MT.updated) + '</dt><dd>' + esc(p.time) + '</dd></div></dl>'
        + '<h4>' + esc(MT.description) + '</h4><p class="m-description">' + esc(p.description || '—') + '</p>'
        + '<div class="m-actions">' + button('list', MT.projects, 'm-primary') + button('new', '+ ' + MT.newProject, 'm-secondary') + '</div>';
    } else {
      out += '<form class="m-form" data-m-form="' + screen + '">';
      if (screen === 'new') {
        out += '<label>' + esc(MT.name) + '<input name="name" required maxlength="80" autocomplete="off" placeholder="'
          + esc(MT.nameHint) + '"></label><label>' + esc(MT.status) + '<select name="status"><option value="active">'
          + esc(MT.active) + '</option><option value="paused">' + esc(MT.paused) + '</option></select></label>'
          + '<label>' + esc(MT.optional) + '<textarea name="description" maxlength="500"></textarea></label>';
      } else out += '<label>' + esc(MT.names) + '<textarea name="names" required maxlength="800" placeholder="' + esc(MT.importHint) + '"></textarea></label>';
      out += '<p class="m-caption">' + esc(MT.local) + '</p><div class="m-actions"><button class="m-primary" type="submit">'
        + esc(screen === 'new' ? MT.create : MT.import) + '</button>' + button('list', MT.cancel, 'm-secondary') + '</div></form>';
    }
    return out + '<nav class="m-tabs" aria-label="' + esc(MT.preview) + '"><button type="button" data-m-action="list"'
      + (screen === 'list' || screen === 'detail' ? ' aria-current="page"' : '') + '>' + esc(MT.projects)
      + '</button><button type="button" data-m-action="new"' + (screen === 'new' ? ' aria-current="page"' : '')
      + '>' + esc(MT.newProject) + '</button></nav></div>';
  }
  function mobileAdd(state, names, status, description) {
    var clean = names.map(function(name) { return name.trim().slice(0,80); }).filter(Boolean).slice(0,10);
    if (!clean.length) return false;
    var start = state.projects.length;
    clean.forEach(function(name) { state.projects.push({ name:name, status:status === 'paused' ? 'paused' : 'active',
      description:description.slice(0,500), time:MT.now }); });
    state.selected = start; state.query = ''; state.screen = clean.length === 1 ? 'detail' : 'list';
    state.message = clean.length === 1 ? MT.created : MT.imported;
    return true;
  }
  function mobilePrompt(slug) {
    return '\n\n## ' + MT.prompt + '\n' + MT.promptText + '\n\n' + MOBILE_DATA[slug].note
      + '\n\n' + MT.values + ':\n' + Object.entries(MOBILE_DATA[slug].tokens).map(function(pair) {
        return '- ' + pair[0] + ': ' + pair[1];
      }).join('\n');
  }

  /* ---------- Mobile reference: catalog integration ---------- */
  function renderMobilePreviews() {
    if (!mobileMode) return;
    document.querySelectorAll('.mobile-preview').forEach(function(host) {
      host.innerHTML = '<div inert>' + mobileMarkup(host.dataset.mobileSlug, newMobileState(mobileScreen)) + '</div>';
    });
  }
  function mountMobileResults() {
    fiRes.querySelectorAll('.fi-frame').forEach(function(frame) {
      var host = frame.querySelector('.fi-host');
      if (mobileMode) {
        host.innerHTML = mobileMarkup(frame.dataset.demo, newMobileState(mobileScreen));
        host.style.width = '100%'; host.style.transform = 'none'; frame.style.height = 'auto';
        frame.style.maxWidth = '390px'; frame.style.marginInline = 'auto';
      } else {
        var src = document.querySelector('.k-plate[data-slug="' + frame.dataset.demo + '"] .demo-host');
        host.textContent = ''; host.appendChild(cloneDemo(src.firstElementChild, 'finder'));
        host.style.width = ''; frame.style.maxWidth = ''; frame.style.marginInline = '';
      }
    });
  }
  function renderMobileSheet(focus) {
    var host = document.getElementById('mobile-sheet');
    if (!mobileState || cur < 0) return;
    host.innerHTML = mobileMarkup(order[cur], mobileState);
    if (focus) {
      var target = host.querySelector(focus === true ? '[data-m-heading]' : focus);
      if (target) target.focus();
    }
  }
  function mountMobileSheet() {
    document.getElementById('mobile-sheet').hidden = !mobileMode;
    document.getElementById('mobile-help').hidden = !mobileMode;
    document.getElementById('mobile-palette-label').hidden = !mobileMode;
    sHost.parentElement.hidden = mobileMode; sCap.hidden = mobileMode;
    if (mobileMode && cur >= 0) {
      mobileState = newMobileState(mobileScreen);
      renderMobileSheet(false);
      document.getElementById('mobile-note').textContent = MOBILE_DATA[order[cur]].note;
      document.getElementById('mobile-values').textContent = JSON.stringify(MOBILE_DATA[order[cur]].tokens, null, 2);
    } else mobileState = null;
  }
  function setCatalogView(view, screen, updateURL) {
    mobileMode = view === 'mobile';
    mobileScreen = ['list','detail','new'].includes(screen) ? screen : 'list';
    document.documentElement.dataset.catalogView = mobileMode ? 'mobile' : 'desktop';
    document.querySelectorAll('[data-view]').forEach(function(button) {
      button.setAttribute('aria-pressed', String(button.dataset.view === (mobileMode ? 'mobile' : 'desktop')));
    });
    document.querySelectorAll('.mobile-states, .mobile-intro').forEach(function(el) { el.hidden = !mobileMode; });
    document.querySelectorAll('[data-mobile-screen]').forEach(function(el) { el.value = mobileScreen; });
    renderMobilePreviews(); mountMobileSheet(); mountMobileResults();
    // An already displayed export must never describe the previously selected format.
    fiRes.querySelectorAll('.fi-pre, .fi-hint').forEach(function(el) { el.remove(); });
    schedule();
    if (updateURL) {
      var url = new URL(window.location.href);
      if (mobileMode) { url.searchParams.set('view','mobile'); url.searchParams.set('screen',mobileScreen); }
      else { url.searchParams.delete('view'); url.searchParams.delete('screen'); }
      try { window.history.replaceState(null,'',url.href); } catch (e) { /* Embedded artifact. */ }
    }
    document.querySelectorAll('.tb-lang a').forEach(function(link) {
      var url = new URL(link.href);
      if (mobileMode) { url.searchParams.set('view','mobile'); url.searchParams.set('screen',mobileScreen); }
      else { url.searchParams.delete('view'); url.searchParams.delete('screen'); }
      link.href = url.href;
    });
  }
  document.querySelectorAll('[data-view-controls]').forEach(function(el) { el.hidden = false; });
  document.querySelectorAll('[data-view]').forEach(function(button) {
    button.addEventListener('click', function() { setCatalogView(button.dataset.view,mobileScreen,true); });
  });
  document.querySelectorAll('[data-mobile-screen]').forEach(function(select) {
    select.addEventListener('change', function() { setCatalogView('mobile',select.value,true); });
  });
  var mobileHost = document.getElementById('mobile-sheet');
  mobileHost.addEventListener('click', function(event) {
    if (!mobileState) return;
    var project = event.target.closest('[data-m-project]'), action = event.target.closest('[data-m-action]');
    if (project) {
      mobileState.selected = +project.dataset.mProject; mobileState.screen = 'detail'; mobileState.message = '';
      renderMobileSheet(true);
    } else if (action) {
      var previous = mobileState.screen;
      mobileState.screen = action.dataset.mAction; mobileState.message = '';
      renderMobileSheet(mobileState.screen === 'list' && previous === 'detail'
        ? '[data-m-project="' + mobileState.selected + '"]' : true);
    }
  });
  mobileHost.addEventListener('input', function(event) {
    if (!mobileState) return;
    if (event.target.setCustomValidity) event.target.setCustomValidity('');
    if (event.target.name !== 'mobile-search') return;
    mobileState.query = event.target.value;
    var rows = mobileRows(mobileState);
    mobileHost.querySelector('.m-list').innerHTML = rows.html;
    mobileHost.querySelector('.m-empty').hidden = rows.count !== 0;
    mobileHost.querySelector('[data-m-count]').textContent = rows.count + ' ' + MT.shown + ' ' + (mobileState.projects.length + 9);
  });
  mobileHost.addEventListener('submit', function(event) {
    var form = event.target.closest('[data-m-form]');
    if (!form || !mobileState) return;
    event.preventDefault();
    var field = form.elements.namedItem(form.dataset.mForm === 'new' ? 'name' : 'names');
    var names = form.dataset.mForm === 'new' ? [field.value] : field.value.split('\n');
    var status = form.elements.namedItem('status'), description = form.elements.namedItem('description');
    if (!mobileAdd(mobileState,names,status ? status.value : 'active',description ? description.value : '')) {
      field.setCustomValidity(MT.required); field.reportValidity(); return;
    }
    renderMobileSheet(true);
  });
  document.getElementById('mobile-reset').addEventListener('click', function() {
    mobileState = newMobileState(mobileScreen); renderMobileSheet(true);
  });
  var initialMobileParams = new URLSearchParams(window.location.search);
  setCatalogView(initialMobileParams.get('view'),initialMobileParams.get('screen'),false);
