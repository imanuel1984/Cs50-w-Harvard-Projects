document.addEventListener('DOMContentLoaded', () => {
  // Buttons
  document.querySelector('#inbox').onclick = () => load_mailbox('inbox');
  document.querySelector('#sent').onclick = () => load_mailbox('sent');
  document.querySelector('#archived').onclick = () => load_mailbox('archive');
  document.querySelector('#compose').onclick = () => compose_email();

  document.querySelector('#compose-form').onsubmit = send_email;

  // Default view
  load_mailbox('inbox');
});

// Show compose form
function compose_email(prefill={}) {
  show_view('#compose-view');
  ['recipients','subject','body'].forEach(id => {
    document.querySelector(`#compose-${id}`).value = prefill[id] || '';
  });
}

// Send email
function send_email(e) {
  e.preventDefault();
  const data = ['recipients','subject','body'].reduce((obj,id)=>{
    obj[id]=document.querySelector(`#compose-${id}`).value; return obj;
  },{});

  fetch('/emails',{method:'POST',body:JSON.stringify(data)})
    .then(r=>r.json().then(body=>({status:r.status,body})))
    .then(res=>res.status===201?load_mailbox('sent'):alert('Error: '+(res.body.error||JSON.stringify(res.body))))
    .catch(console.error);
}

// Load mailbox
function load_mailbox(mailbox){
  show_view('#emails-view');
  const view=document.querySelector('#emails-view');
  view.innerHTML=`<h3>${capitalize(mailbox)}</h3>`;

  fetch(`/emails/${mailbox}`).then(r=>r.json()).then(emails=>{
    if(emails.error) return view.innerHTML+=`<div class="error">${emails.error}</div>`;
    const container=document.createElement('div'); container.id='mail-list';
    emails.forEach(email=>{
      const entry=document.createElement('div');
      entry.className=`mail-entry ${email.read?'read':'unread'}`;
      entry.innerHTML=`<div class="email-left"><strong>${escapeHtml(email.sender)}</strong> - ${escapeHtml(email.subject)}</div>
                         <div class="email-timestamp">${email.timestamp}</div>`;
      entry.onclick = ()=>load_email(email.id,mailbox);
      container.append(entry);
    });
    view.append(container);
  });
}

// Load single email
function load_email(id,from_mailbox=null){
  show_view('#email-view');
  const emailView=document.querySelector('#email-view'); emailView.innerHTML='';

  fetch(`/emails/${id}`).then(r=>r.json()).then(email=>{
    if(!email.read) fetch(`/emails/${id}`,{method:'PUT',body:JSON.stringify({read:true})});

    const header=['From','To','Subject','Timestamp'].map(f=>{
      const div=document.createElement('div');
      div.innerHTML=`<strong>${f}:</strong> ${escapeHtml(email[f.toLowerCase()] instanceof Array ? email[f.toLowerCase()].join(', ') : email[f.toLowerCase()])}`;
      return div;
    });

    const body=document.createElement('div'); body.className='email-body'; body.innerText=email.body;

    const actions=document.createElement('div'); actions.className='email-actions';
    if(from_mailbox!=='sent'){
      const archive=document.createElement('button'); archive.className='btn';
      archive.innerText=email.archived?'Unarchive':'Archive';
      archive.onclick=()=>fetch(`/emails/${id}`,{method:'PUT',body:JSON.stringify({archived:!email.archived})}).then(()=>load_mailbox('inbox'));
      actions.append(archive);
    }
    const reply=document.createElement('button'); reply.className='btn'; reply.innerText='Reply';
    reply.onclick=()=>reply_email(email);
    actions.append(reply);

    emailView.append(...header,actions,body);
  }).catch(err=>emailView.innerHTML=`<div class="error">${escapeHtml(err.message)}</div>`);
}

// Reply helper
function reply_email(email){
  compose_email({
    recipients: email.sender,
    subject: email.subject.startsWith('Re:') ? email.subject : 'Re: '+email.subject,
    body: `On ${email.timestamp} ${email.sender} wrote:\n${email.body}\n\n`
  });
}

// Helpers
function show_view(view){
  ['#emails-view','#compose-view','#email-view'].forEach(v=>document.querySelector(v).style.display=v===view?'block':'none');
}
function escapeHtml(s){return s?String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;') : '';}
function capitalize(s){return s.charAt(0).toUpperCase()+s.slice(1);}

