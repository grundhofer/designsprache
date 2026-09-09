  /* ---------- Explorer: pure state and render helpers ---------- */
  var EX_EN = LANG === 'en';
  function exT(de, en) { return EX_EN ? en : de; }
  function exLevel(value) { return ['styles','principles','contexts'].includes(value) ? value : 'styles'; }
  function newFeedbackState() { return { phase:'idle', saved:false, previous:false }; }
  function feedbackTransition(state, action) {
    var next = Object.assign({}, state);
    if (action === 'reset') return newFeedbackState();
    if ((action === 'save' || action === 'retry') && state.phase !== 'saving') {
      next.previous = state.saved; next.phase = 'saving';
    } else if (action === 'success' && state.phase === 'saving') {
      next.phase = 'saved'; next.saved = true;
    } else if (action === 'failure' && state.phase === 'saving') {
      next.phase = 'error';
    } else if (action === 'undo' && state.phase === 'saved') {
      next.saved = state.previous; next.phase = 'undone';
    }
    return next;
  }
  var EX_PROJECTS = ['Nexus','Autowrite Studio','Balance Ally'];
  function exNavState(mode) { return { selected:0, detail:false, mode:mode || 'split' }; }
  function exNavTransition(state, action, value) {
    var next = Object.assign({},state);
    if (action === 'open' && Number.isInteger(value) && value >= 0 && value < EX_PROJECTS.length) {
      next.selected = value; next.detail = true;
    } else if (action === 'back') next.detail = false;
    else if (action === 'mode' && ['split','pages'].includes(value)) next.mode = value;
    return next;
  }
  function exNavigationMarkup(state) {
    var split = state.mode === 'split';
    var list = '<div class="ex-project-list" aria-label="'+exT('Projekte','Projects')+'">'+EX_PROJECTS.map(function(name,index) {
      return '<button type="button" data-nav-open="'+index+'" aria-pressed="'+(state.selected === index)+'">'+esc(name)+'<span> →</span></button>';
    }).join('')+'</div>';
    var detail = '<div class="ex-project-detail"><h4 tabindex="-1">'+esc(EX_PROJECTS[state.selected])+'</h4><dl><div><dt>Status</dt><dd>'+exT(state.selected===2?'Pausiert':'Aktiv',state.selected===2?'Paused':'Active')+'</dd></div><div><dt>'+exT('Verantwortlich','Owner')+'</dt><dd>Alex</dd></div></dl><p>'+exT('Projektübersicht und nächste Aufgaben.','Project overview and next tasks.')+'</p></div>';
    if (split) return '<div class="ex-split">'+list+detail+'</div>';
    if (state.detail) return '<button type="button" data-nav-back>← '+exT('Alle Projekte','All projects')+'</button>'+detail;
    return '<h4>'+exT('Projekte','Projects')+'</h4>'+list;
  }
  function newContextState(id) { return { id:id, selected:0, detail:false, mode:id==='desktop' || id==='tablet'?'split':'pages', watch:'idle', parked:false, playing:false, custom:'', spatial:false }; }
  function exContextTransition(state, action, value) {
    var next=Object.assign({},state);
    if (action==='watch-toggle') next.watch=state.watch==='running'?'paused':'running';
    else if (action==='watch-reset') next.watch='idle';
    else if (action==='park') { next.parked=!state.parked; next.detail=false; }
    else if (action==='audio' && Number.isInteger(value) && value>=0 && value<3) { next.selected=value; next.playing=true; }
    else if (action==='audio-toggle') next.playing=!state.playing;
    else if (action==='custom' && state.parked && typeof value==='string' && value.trim()) { next.custom=value.trim().slice(0,80); next.playing=true; }
    else if (action==='spatial') next.spatial=!state.spatial;
    else if (action==='tv-move' && !state.detail && Number.isInteger(value)) next.selected=Math.max(0,Math.min(2,state.selected+value));
    else if (action==='tv-open' && Number.isInteger(value) && value>=0 && value<3) { next.selected=value; next.detail=true; }
    else if (action==='tv-back') next.detail=false;
    else if (action==='layout') next.mode=state.mode==='split'?'pages':'split';
    return next;
  }
  function exContextButton(action,label,extra) { return '<button type="button" data-context-action="'+action+'" '+(extra || '')+'>'+label+'</button>'; }
  function exContextMarkup(state) {
    var b=exContextButton;
    if (state.id==='watch') return '<div class="ex-watch"><span>Nexus · '+exT('Fokus','Focus')+'</span><strong>25:00</strong><p role="status">'+(state.watch==='idle'?exT('Bereit','Ready'):state.watch==='running'?exT('Fokus aktiv','Focus active'):exT('Pausiert','Paused'))+'</p>'+b('watch-toggle',state.watch==='running'?exT('Pause','Pause'):state.watch==='paused'?exT('Fortsetzen','Resume'):exT('Starten','Start'))+b('watch-reset',exT('Zurücksetzen','Reset'))+'</div>';
    if (state.id==='tv') {
      var titles=[exT('Nordlicht','Northern lights'),exT('Architektur','Architecture'),exT('Am Meer','By the sea')];
      if (state.detail) return '<div class="ex-tv">'+b('tv-back','← '+exT('Zur Auswahl','Back to selection'))+'<h4 tabindex="-1">'+titles[state.selected]+'</h4><p>'+exT('Sendungsdetails · 24 Minuten','Programme details · 24 minutes')+'</p><p>'+exT('Die Auswahl bleibt beim Zurückgehen erhalten.','Your selection is preserved when you go back.')+'</p></div>';
      return '<div class="ex-tv"><h4>'+exT('Heute entdecken','Discover today')+'</h4><div class="ex-tv-tiles">'+titles.map(function(title,index) {return b('tv-open','<span class="ex-tv-art ex-tv-art-'+index+'" aria-hidden="true">'+['◒','▥','≈'][index]+'</span>'+title,'data-tv-index="'+index+'" data-value="'+index+'" tabindex="'+(index===state.selected?'0':'-1')+'" class="'+(index===state.selected?'is-selected':'')+'"');}).join('')+'</div><div class="ex-controls">'+b('tv-left','←','aria-label="'+exT('Vorherige Sendung','Previous programme')+'"')+b('tv-select',exT('Öffnen','Open'))+b('tv-right','→','aria-label="'+exT('Nächste Sendung','Next programme')+'"')+'</div><p class="ex-note">'+exT('In der Auswahl: ← / → bewegen den Fokus, Enter öffnet. Tab verlässt den Bereich.','In the selection: ← / → move focus, Enter opens. Tab leaves the region.')+'</p></div>';
    }
    if (state.id==='car') return '<div class="ex-car"><div class="ex-controls">'+b('park',state.parked?exT('Fahrt simulieren','Simulate driving'):exT('Parken simulieren','Simulate parking'),'aria-pressed="'+state.parked+'"')+'<strong>'+exT(state.parked?'Geparkt':'Fahrt',state.parked?'Parked':'Driving')+'</strong></div><h4>Audio</h4><div class="ex-car-favourites">'+[exT('Nachrichten','News'),'Jazz',exT('Hörbuch','Audiobook')].map(function(name,index){return b('audio',name,'data-value="'+index+'" aria-pressed="'+(state.selected===index && !state.custom)+'"');}).join('')+'</div><p role="status">'+(state.playing?exT('Gewählt: ','Selected: '):exT('Pausiert: ','Paused: '))+esc(state.custom || [exT('Nachrichten','News'),'Jazz',exT('Hörbuch','Audiobook')][state.selected])+'</p>'+b('audio-toggle',state.playing?'Pause':exT('Fortsetzen','Resume'))+(state.parked?'<form data-context-form="car"><label>'+exT('Weiteren Titel wählen','Choose another title')+'<input name="title" required maxlength="80" value="'+esc(state.custom)+'"></label><button type="submit">'+exT('Übernehmen','Apply')+'</button></form>':'<p class="ex-note">'+exT('Die Texteingabe ist in dieser Demo nur im Parkzustand verfügbar.','Text input is available only while parked in this demo.')+'</p>')+'<small>'+exT('Auswahl-Demo · keine Audiowiedergabe','Selection demo · no audio playback')+'</small></div>';
    if (state.id==='spatial') return '<div class="ex-spatial '+(state.spatial?'is-layered':'')+'"><div class="ex-spatial-content"><span>'+exT('Inhalt','Content')+'</span><h4>Nexus</h4><p>'+exT('Drei nächste Schritte','Three next steps')+'</p></div><div class="ex-spatial-controls">'+exT('Bedienebene','Control layer')+'</div></div>'+b('spatial',state.spatial?exT('Flache Anordnung','Flat arrangement'):exT('Ebenen trennen','Separate layers'),'aria-pressed="'+state.spatial+'"');
    var prefix=state.id==='tablet'?'<div class="ex-controls">'+b('layout',state.mode==='split'?exT('Schmale Ansicht','Narrow view'):exT('Zwei Bereiche','Two panes'))+'</div>':'';
    if (state.id==='web') prefix='<p class="ex-address" aria-label="'+exT('Beispieladresse','Example address')+'">/projects'+(state.detail?'/'+['nexus','autowrite','balance'][state.selected]:'')+'</p>';
    return prefix+'<div class="ex-device ex-device-'+state.id+'">'+exNavigationMarkup(state)+'</div>';
  }

  /* ---------- Explorer: DOM wiring ---------- */
  function exLanguageLinks() {
    document.querySelectorAll('.tb-lang a').forEach(function(link) {
      var url=new URL(link.href); url.search=window.location.search; url.hash=window.location.hash; link.href=url.href;
    });
  }
  function exShowLevel(level, focus) {
    level=exLevel(level);
    if(level!=='styles') { if(!sheet.hidden)close(); if(!FI.hidden)closeFinder(); }
    document.querySelectorAll('#experience > [data-level]').forEach(function(panel) {panel.hidden=panel.dataset.level!==level;});
    document.querySelectorAll('[data-level-link]').forEach(function(link) {
      if(link.dataset.levelLink===level) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current');
      var url=new URL(window.location.href); url.searchParams.set('level',link.dataset.levelLink); url.hash=link.dataset.levelLink; link.href=url.href;
    });
    document.documentElement.dataset.explorerLevel=level;
    exLanguageLinks(); schedule();
    if(focus) document.getElementById(level+'-title').focus();
  }
  document.querySelectorAll('[data-level-link]').forEach(function(link) {
    link.addEventListener('click',function(event) {
      if(event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button!==0) return;
      event.preventDefault();
      var url=new URL(window.location.href); url.searchParams.set('level',link.dataset.levelLink); url.hash=link.dataset.levelLink;
      window.history.pushState(null,'',url.href); exShowLevel(link.dataset.levelLink,true);
    });
  });
  function exRestoreRoute() {
    var params=new URLSearchParams(window.location.search);
    exShowLevel(params.get('level'),false);
    setCatalogView(params.get('view')==='mobile'?'mobile':'desktop',params.get('screen'),false);
    var target=document.getElementById(window.location.hash.slice(1));
    if(target && !target.closest('[hidden]')) target.scrollIntoView();
  }
  window.addEventListener('popstate',exRestoreRoute);
  window.addEventListener('hashchange',exLanguageLinks);
  exShowLevel(new URLSearchParams(window.location.search).get('level'),false);
  var exInitialTarget=document.getElementById(window.location.hash.slice(1));
  if(exInitialTarget && !exInitialTarget.closest('[hidden]')) setTimeout(function(){exInitialTarget.scrollIntoView();},0);

  var exFeedback=newFeedbackState(), exFeedbackTimer=null;
  var exFeedbackLab=document.querySelector('[data-principle="feedback"]');
  function exRenderFeedback() {
    var texts={idle:exT('Bereit zum Speichern.','Ready to save.'),saving:exT('Wird gespeichert…','Saving…'),saved:exT('Gespeichert. Du kannst diese Änderung rückgängig machen.','Saved. You can undo this change.'),error:exT('Speichern fehlgeschlagen. Dein Entwurf bleibt erhalten. Versuche es erneut.','Saving failed. Your draft is preserved. Try again.'),undone:exT('Änderung rückgängig gemacht.','Change undone.')};
    exFeedbackLab.querySelector('[data-feedback-status]').textContent=texts[exFeedback.phase];
    exFeedbackLab.querySelector('[data-feedback-value]').textContent=exFeedback.saved?exT('Gespeichert','Saved'):exT('Entwurf','Draft');
    exFeedbackLab.querySelector('[data-lab-action="save"]').disabled=exFeedback.phase==='saving' || exFeedback.phase==='saved';
    exFeedbackLab.querySelector('[data-lab-action="retry"]').hidden=exFeedback.phase!=='error';
    exFeedbackLab.querySelector('[data-lab-action="undo"]').hidden=exFeedback.phase!=='saved';
  }
  var exNav=exNavState(), exAdaptive=exNavState();
  var exNavigationDemo=document.querySelector('[data-navigation-demo]');
  var exAdaptiveDemo=document.querySelector('[data-adaptive-demo]');
  exNavigationDemo.innerHTML=exNavigationMarkup(exNav); exAdaptiveDemo.innerHTML=exNavigationMarkup(exAdaptive);
  function exFocusNavigation(demo,state,back) {
    var target=demo.querySelector(back?'[data-nav-open="'+state.selected+'"]':'.ex-project-detail h4');
    if(target) target.focus();
  }
  document.getElementById('principles').addEventListener('click',function(event) {
    var lab=event.target.closest('[data-principle]'); if(!lab) return;
    var openButton=event.target.closest('[data-nav-open]'), back=event.target.closest('[data-nav-back]');
    if(openButton || back) {
      var adaptive=lab.dataset.principle==='adaptive', state=adaptive?exAdaptive:exNav;
      state=exNavTransition(state,back?'back':'open',openButton?Number(openButton.dataset.navOpen):null);
      if(adaptive)exAdaptive=state;else exNav=state;
      var demo=adaptive?exAdaptiveDemo:exNavigationDemo; demo.innerHTML=exNavigationMarkup(state); exFocusNavigation(demo,state,!!back);return;
    }
    var button=event.target.closest('[data-lab-action]'); if(!button) return;
    var action=button.dataset.labAction;
    if(lab.dataset.principle==='feedback') {
      clearTimeout(exFeedbackTimer);
      if(action==='save' || action==='retry') {
        if(exFeedback.phase==='saving')return;
        var fail=lab.querySelector('[data-lab-option="fail"]').checked;
        exFeedback=feedbackTransition(exFeedback,action); exRenderFeedback();
        exFeedbackTimer=setTimeout(function() {
          exFeedback=feedbackTransition(exFeedback,fail?'failure':'success');
          if(fail)lab.querySelector('[data-lab-option="fail"]').checked=false;
          exRenderFeedback();
        },700);
      } else {
        exFeedback=feedbackTransition(exFeedback,action==='undo'?'undo':'reset'); exRenderFeedback();
        if(action==='reset-feedback')lab.querySelector('[data-lab-option="fail"]').checked=false;
        if(action==='undo')lab.querySelector('[data-lab-action="save"]').focus();
      }
    }
    if(action==='inclusive-confirm') {
      lab.querySelector('[data-inclusive-status]').textContent=exT('Auswahl bestätigt.','Selection confirmed.');
      var demo=lab.querySelector('[data-inclusive-demo]');demo.classList.remove('is-playing');void demo.offsetWidth;demo.classList.add('is-playing');
    }
  });
  document.getElementById('principles').addEventListener('change',function(event) {
    var control=event.target.closest('[data-lab-option]'); if(!control)return;
    var lab=control.closest('[data-principle]'), key=control.dataset.labOption;
    if(key==='grouping')lab.querySelector('[data-grouping]').dataset.grouping=control.value;
    if(key==='navigation'){exNav=exNavTransition(exNav,'mode',control.value);exNavigationDemo.innerHTML=exNavigationMarkup(exNav);}
    if(key==='width'){exAdaptiveDemo.dataset.width=control.value;exAdaptive=exNavTransition(exAdaptive,'mode',control.value==='wide'?'split':'pages');exAdaptiveDemo.innerHTML=exNavigationMarkup(exAdaptive);}
    if(key==='input')exAdaptiveDemo.dataset.input=control.value;
    if(lab.dataset.principle==='inclusive') {
      var demo=lab.querySelector('[data-inclusive-demo]');demo.classList.toggle('ex-'+key,control.checked);
      if(key==='long') {
        lab.querySelector('[data-inclusive-title]').textContent=control.checked?exT('Nexus – gemeinsame Projektplanung für das gesamte Redaktionsteam','Nexus – shared project planning for the whole editorial team'):'Nexus';
        lab.querySelector('[data-inclusive-copy]').textContent=control.checked?exT('Alle Beteiligten finden hier ihre nächsten Aufgaben, ausführliche Projektbeschreibungen und den aktuellen Stand der Abstimmung.','Everyone can find their next tasks, detailed project descriptions and the current review status here.'):exT('Ein gemeinsamer Ort für Projekte.','A shared home for projects.');
      }
    }
  });
  document.querySelector('[data-lab-form="disclosure"]').addEventListener('submit',function(event) {
    event.preventDefault();var form=event.currentTarget;
    form.querySelector('[data-disclosure-status]').textContent=exT('Übernommen: ','Applied: ')+form.elements.project.value+' · '+form.elements.owner.value+' · '+form.elements.reminder.selectedOptions[0].textContent;
  });

  var exContextStates={};
  document.querySelectorAll('[data-context-demo]').forEach(function(demo){var id=demo.dataset.contextDemo;exContextStates[id]=newContextState(id);demo.innerHTML=exContextMarkup(exContextStates[id]);});
  function exRenderContext(id,focusSelector) {
    var demo=document.querySelector('[data-context-demo="'+id+'"]'); demo.innerHTML=exContextMarkup(exContextStates[id]);
    if(focusSelector){var target=demo.querySelector(focusSelector);if(target)target.focus();}
  }
  document.getElementById('contexts').addEventListener('click',function(event) {
    var article=event.target.closest('[data-context]');if(!article)return;
    var id=article.dataset.context, state=exContextStates[id], open=event.target.closest('[data-nav-open]'), back=event.target.closest('[data-nav-back]');
    if(open || back) {
      exContextStates[id]=Object.assign({},state,exNavTransition(state,back?'back':'open',open?Number(open.dataset.navOpen):null));
      exRenderContext(id,back?'[data-nav-open="'+state.selected+'"]':'.ex-project-detail h4');return;
    }
    var button=event.target.closest('[data-context-action]');if(!button)return;
    var action=button.dataset.contextAction, value=Number(button.dataset.value);
    if(action==='tv-left' || action==='tv-right') {value=action==='tv-left'?-1:1;action='tv-move';}
    if(action==='tv-select'){value=state.selected;action='tv-open';}
    exContextStates[id]=exContextTransition(state,action,value);
    if(action==='audio')exContextStates[id].custom='';
    var focus='[data-context-action="'+button.dataset.contextAction+'"]';
    if(id==='tv')focus=action==='tv-open'?'.ex-tv h4':'[data-tv-index="'+exContextStates[id].selected+'"]';
    if(action==='audio')focus='[data-context-action="audio"][data-value="'+value+'"]';
    exRenderContext(id,focus);
  });
  document.getElementById('contexts').addEventListener('keydown',function(event) {
    var tile=event.target.closest('[data-tv-index]');if(!tile || !['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
    event.preventDefault();var state=exContextStates.tv;
    var delta=event.key==='Home'?-3:event.key==='End'?3:event.key==='ArrowLeft'?-1:1;
    exContextStates.tv=exContextTransition(state,'tv-move',delta);exRenderContext('tv','[data-tv-index="'+exContextStates.tv.selected+'"]');
  });
  document.getElementById('contexts').addEventListener('submit',function(event) {
    var form=event.target.closest('[data-context-form="car"]');if(!form)return;
    event.preventDefault();exContextStates.car=exContextTransition(exContextStates.car,'custom',form.elements.title.value);exRenderContext('car','[data-context-action="audio-toggle"]');
  });
  // Context reference links open the real fact sheet and retain a useful fallback URL.
  document.querySelectorAll('[data-style-link]').forEach(function(link) {
    var slug=link.dataset.styleLink, plate=document.querySelector('.k-plate[data-slug="'+slug+'"]');
    if(!plate)return;
    link.href='?level=styles#'+plate.closest('.fam').id;
    link.addEventListener('click',function(event) {
      if(event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button!==0)return;
      event.preventDefault();var url=new URL(window.location.href);url.searchParams.set('level','styles');url.hash=plate.closest('.fam').id;
      window.history.pushState(null,'',url.href);exShowLevel('styles',false);
      lastFocus=plate.querySelector('.plate-open');lastFocus.focus();open(order.indexOf(slug));
    });
  });
