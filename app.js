// minimal interactivity: could be expanded later
document.addEventListener('DOMContentLoaded', function(){
  // future: AJAX posting, confirmations, etc.
  const forms = document.querySelectorAll('.form-inline');
  forms.forEach(f=> f.addEventListener('submit', ()=> {
    // small UX: disable submit for a moment
    const btn = f.querySelector('button');
    if(btn){ btn.disabled = true; setTimeout(()=>btn.disabled=false,500); }
  }));
});
