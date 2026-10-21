
const D=JSON.parse(document.querySelector('#site-data').textContent),byId=Object.fromEntries(D.documents.map(d=>[d.id,d]));
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function anchor(file,id=''){return file+(id?'#'+id:'')}
function readLink(file,part,label){const t=anchor(file,part);return `<a href="${esc(t)}" data-read="${esc(t)}">${esc(label)}</a>`}
const topic=document.querySelector('#topic'),subject=document.querySelector('#subject'),priority=document.querySelector('#priority'),query=document.querySelector('#search');
topic.innerHTML+=D.categories.map(c=>`<option value="${c.id}">${esc(c.title)}</option>`).join('');
subject.innerHTML+=D.categories[0].groups.map(g=>`<option>${esc(g.title)}</option>`).join('');
let limit=20,currentMatches=[],showAnswers=true;
function update(reset=true){
 if(reset)limit=20;
 const terms=query.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
 currentMatches=D.questions.filter(q=>(!topic.value||q.category===topic.value)&&(!subject.value||q.subject===subject.value)&&(!priority.value||q.priority===priority.value)&&terms.every(t=>/^q\d{3}$/.test(t)?q.id.toLowerCase()===t:(q.title+' '+q.section+' '+q.search).toLowerCase().includes(t)));
 document.querySelector('#result-count').textContent=`${currentMatches.length} / ${D.questions.length}道题目`;
 document.querySelector('#results').innerHTML=currentMatches.slice(0,limit).map(q=>{const preferred=byId[q.preferred];return `<article class="result"><span class="badge">${q.id}</span><span class="badge">${esc(q.subject||q.topic)}</span><span class="badge">${q.priority}</span><h3>${readLink(preferred.file,q.id,q.title)}</h3><p class="oral-preview">${esc(q.oral)}</p><div class="links">${readLink(preferred.file,q.id,'在本板块阅读')}${readLink(byId.master.file,q.id,'主手册原文')}</div></article>`}).join('');
 document.querySelector('#empty').hidden=currentMatches.length>0;document.querySelector('#more').hidden=currentMatches.length<=limit;
}
query.addEventListener('input',()=>update());priority.addEventListener('change',()=>update());
topic.addEventListener('change',()=>{if(topic.value&&topic.value!=='knowledge')subject.value='';update()});
subject.addEventListener('change',()=>{if(subject.value)topic.value='knowledge';update()});
document.querySelector('#more').addEventListener('click',()=>{limit+=20;update(false)});
document.querySelector('#preview-toggle').addEventListener('click',()=>{showAnswers=!showAnswers;document.querySelector('#results').classList.toggle('hide-answers',!showAnswers);document.querySelector('#preview-toggle').textContent=showAnswers?'隐藏口头答案':'显示口头答案';document.querySelector('#preview-toggle').setAttribute('aria-pressed',String(!showAnswers))});
document.querySelector('#reset').addEventListener('click',()=>{query.value='';topic.value='';subject.value='';priority.value='';update()});
document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{query.value='';subject.value='';priority.value='';topic.value=b.dataset.filter;update();document.querySelector('#question-bank').scrollIntoView({block:'start'})}));
const home=document.querySelector('#home'),reader=document.querySelector('#reader'),frame=document.querySelector('#reader-frame');let previousScroll=0;
function validTarget(t){return typeof t==='string'&&D.documents.some(d=>d.file===t.split('#')[0])}
function openReader(t,changeHash=true){if(!validTarget(t))return;if(!home.hidden)previousScroll=scrollY;home.hidden=true;reader.hidden=false;const doc=D.documents.find(d=>d.file===t.split('#')[0]);document.querySelector('#reader-title').textContent=doc.title;document.querySelector('#reader-standalone').href=t;frame.src=t;if(changeHash)history.pushState(null,'','#read='+encodeURIComponent(t));window.scrollTo(0,0);document.title=doc.label+' · 面经聚合';}
function homeView(changeHash=true){reader.hidden=true;home.hidden=false;frame.removeAttribute('src');if(changeHash)history.pushState(null,'',location.pathname);document.title='面经聚合 · 机械结构工程师面试手册';window.scrollTo(0,previousScroll);}
document.addEventListener('click',e=>{const a=e.target.closest('[data-read]');if(!a||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;e.preventDefault();openReader(a.dataset.read)});
document.querySelector('#back-home').addEventListener('click',()=>homeView());
document.querySelectorAll('[data-home]').forEach(a=>a.addEventListener('click',()=>{if(!reader.hidden)homeView(false)}));
function route(){if(location.hash.startsWith('#read=')){try{const t=decodeURIComponent(location.hash.slice(6));if(validTarget(t)){openReader(t,false);return}}catch(e){}}if(!reader.hidden)homeView(false)}
window.addEventListener('popstate',route);window.addEventListener('hashchange',()=>{if(location.hash.startsWith('#read='))route()});
window.addEventListener('message',e=>{if(e.source!==frame.contentWindow||e.data?.type!=='handbook-loaded')return;const d=D.documents.find(d=>d.file===e.data.file);if(!d)return;const fragment=typeof e.data.fragment==='string'&&e.data.fragment.startsWith('#')?e.data.fragment:'';const t=d.file+fragment;document.querySelector('#reader-title').textContent=d.title;document.querySelector('#reader-standalone').href=t;document.title=d.label+' · 面经聚合';history.replaceState(null,'','#read='+encodeURIComponent(t))});
update();route();
