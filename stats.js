/* Statistiques GoatCounter : clics (événements) sur ledahudelatania.fr */
(function(){
  function send(name){try{if(window.goatcounter&&window.goatcounter.count)window.goatcounter.count({path:name,title:name,event:true});}catch(_){}}
  function home(){var h=document.querySelector('.home[aria-pressed="true"]');return h?h.dataset.home:'?';}
  var calSeen={};
  document.addEventListener('click',function(e){
    var t=e.target,c;
    if(!t||!t.closest)return;
    if((c=t.closest('#guides a'))){send('guide-'+(c.getAttribute('href')||'').split('/').pop().replace('.pdf',''));return;}
    if((c=t.closest('.cta'))){send('demande-'+home());return;}
    if(t.closest('#cFb')){send('facebook');return;}
    if((c=t.closest('#vids a'))){send('video-facebook-'+home());return;}
    if((c=t.closest('[data-ph]'))){send('photos-'+home());return;}
    if((c=t.closest('[data-lang]'))){send('langue-'+c.dataset.lang);return;}
    if((c=t.closest('[data-home]'))){send('logement-'+c.dataset.home);return;}
    if(t.closest('.d[data-d]')){var h=home();if(!calSeen[h]){calSeen[h]=1;send('calendrier-'+h);}return;}
    if(t.id==='promoBtn'){send('code-promo');return;}
    if(t.id==='copy'){send('recap-copie');return;}
  },true);
  document.addEventListener('play',function(e){if(e.target&&e.target.tagName==='VIDEO'&&!e.target.dataset.gc){e.target.dataset.gc=1;if(!e.target.autoplay||e.isTrusted)send('video-drone-'+home());}},true);
})();
