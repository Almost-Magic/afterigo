"""
Elaine v4 — Mobile Web UI
Served at /mobile — no app install needed.
AMTL Design System, dark/light toggle, full Elaine access.
Almost Magic Tech Lab
"""

MOBILE_HTML = '''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#0A0E14">
<title>Elaine</title>
<link rel="manifest" href="data:application/json,{&quot;name&quot;:&quot;Elaine&quot;,&quot;short_name&quot;:&quot;Elaine&quot;,&quot;display&quot;:&quot;standalone&quot;,&quot;background_color&quot;:&quot;%230A0E14&quot;,&quot;theme_color&quot;:&quot;%230A0E14&quot;}">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#0A0E14;--sf:#151B26;--sf2:#1E2536;--sf3:#283044;--bd:#1E2536;--bd2:#283044;--tx:#E8E4DC;--txe:#F5F2ED;--txm:#9A968C;--gold:#C9944A;--amber:#B37D3A;--glow:rgba(201,148,74,0.08);--ok:#4A9B7F;--warn:#D4A04A;--err:#C75D5D;--info:#5A8FC9;--r:8px}
[data-theme="light"]{--bg:#F8F7F5;--sf:#EFEEE9;--sf2:#E0DED6;--sf3:#fff;--bd:#E0DED6;--bd2:#C4C1B8;--tx:#2D2B27;--txe:#1A1917;--txm:#6E6A62;--glow:rgba(201,148,74,0.12)}
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{font-family:'Sora',system-ui,sans-serif;background:var(--bg);color:var(--tx);min-height:100vh;min-height:100dvh;transition:background .3s,color .3s;font-size:14px;line-height:1.5;overflow-x:hidden}

/* Header */
.hdr{position:sticky;top:0;z-index:50;background:var(--sf);border-bottom:1px solid var(--bd);padding:14px 16px;display:flex;align-items:center;justify-content:space-between;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
.hdr-left{display:flex;align-items:center;gap:10px}
.hdr-logo{width:28px;height:28px;border-radius:50%;background:var(--gold);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;color:var(--bg)}
.hdr-name{font-weight:600;font-size:15px;color:var(--gold);letter-spacing:.3px}
.hdr-right{display:flex;align-items:center;gap:10px}
.hdr-dot{width:8px;height:8px;border-radius:50%;background:var(--ok);animation:pulse 2.5s ease-in-out infinite}
.hdr-dot.off{background:var(--err);animation:none}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.hdr-toggle{background:var(--sf2);border:1px solid var(--bd);border-radius:6px;padding:5px 10px;font-family:inherit;font-size:12px;color:var(--txm);cursor:pointer}

/* Tabs */
.tabs{display:flex;gap:0;background:var(--sf);border-bottom:1px solid var(--bd);padding:0 8px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}
.tabs::-webkit-scrollbar{display:none}
.tab{padding:10px 14px;font-size:12px;color:var(--txm);cursor:pointer;white-space:nowrap;border-bottom:2px solid transparent;transition:all .15s;font-weight:500}
.tab.on{color:var(--gold);border-bottom-color:var(--gold)}

/* Pages */
.pages{padding-bottom:80px}
.page{display:none;padding:16px}
.page.on{display:block}

/* Cards */
.cd{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:16px;margin-bottom:12px}
.cd-lbl{font-size:10px;text-transform:uppercase;letter-spacing:1.8px;color:var(--txm);margin-bottom:8px;font-weight:500}
.cd-big{font-size:32px;font-weight:700;color:var(--txe);line-height:1}
.cd-med{font-size:20px;font-weight:600;color:var(--txe)}
.cd-sub{font-size:12px;color:var(--txm);margin-top:6px}
.cd-txt{font-size:14px;line-height:1.7}
.cd-em{font-size:13px;color:var(--gold);font-style:italic;margin-top:8px}

/* Stats Row */
.stats{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px}

/* Wellbeing */
.wb{height:5px;border-radius:3px;background:var(--bd);margin-top:10px}
.wb-f{height:100%;border-radius:3px;transition:width .5s}
.wb-f.thriving{background:var(--ok);width:100%}.wb-f.steady{background:var(--ok);width:75%}
.wb-f.stretched{background:var(--warn);width:50%}.wb-f.strained{background:var(--err);width:25%}
.wb-f.depleted{background:var(--err);width:10%}

/* Gravity */
.gi{display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid var(--bd)}
.gi:last-child{border-bottom:none}
.gi-f{font-size:22px;font-weight:700;min-width:42px;text-align:center}
.gi-f.red{color:var(--err)}.gi-f.amber{color:var(--warn)}.gi-f.green{color:var(--ok)}
.gi-n{flex:1;font-size:13px}

/* Gate */
.gr{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--bd)}
.gr:last-child{border-bottom:none}
.gr-l{color:var(--txm);font-size:13px}.gr-v{font-weight:600;font-size:13px}

/* Chat */
.chat{display:flex;flex-direction:column;height:calc(100vh - 110px);height:calc(100dvh - 110px)}
.chat-msgs{flex:1;overflow-y:auto;padding:16px}
.msg{margin-bottom:14px;max-width:82%;animation:msgIn .2s ease}
@keyframes msgIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
.msg.u{margin-left:auto}.msg.e{margin-right:auto}
.msg-w{font-size:10px;color:var(--txm);margin-bottom:3px;padding:0 6px}
.msg.u .msg-w{text-align:right}
.msg-b{padding:12px 16px;border-radius:16px;font-size:13px;line-height:1.6}
.msg.u .msg-b{background:var(--gold);color:var(--bg);border-bottom-right-radius:4px}
.msg.e .msg-b{background:var(--sf2);border:1px solid var(--bd);border-bottom-left-radius:4px}
.chat-bar{padding:12px 16px;border-top:1px solid var(--bd);display:flex;gap:8px;background:var(--sf);flex-shrink:0}
.chat-in{flex:1;background:var(--sf2);border:1px solid var(--bd);border-radius:22px;color:var(--tx);font-family:inherit;font-size:14px;padding:10px 16px;outline:none}
.chat-in:focus{border-color:var(--gold)}
.chat-in::placeholder{color:var(--txm)}
.chat-b{width:42px;height:42px;border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0}
.chat-b.send{background:var(--gold);color:var(--bg);font-weight:700}
.chat-b.mic{background:var(--sf2);border:1px solid var(--bd);color:var(--txm)}
.chat-b.mic.rec{background:var(--err);color:#fff;border-color:var(--err);animation:pulse 1s infinite}

/* Quick Check */
.chk-ta{width:100%;background:var(--sf2);border:1px solid var(--bd);border-radius:var(--r);color:var(--tx);font-family:inherit;font-size:14px;padding:14px;min-height:140px;outline:none;resize:vertical}
.chk-ta:focus{border-color:var(--gold)}
.chk-btn{background:var(--gold);color:var(--bg);border:none;border-radius:6px;padding:12px 24px;font-family:inherit;font-weight:600;font-size:14px;cursor:pointer;margin-top:10px;width:100%}
.chk-r{margin-top:14px;padding:14px;background:var(--sf2);border-radius:var(--r);font-size:13px;line-height:1.6;display:none}
.chk-r.clear{border-left:3px solid var(--ok)}.chk-r.review{border-left:3px solid var(--warn)}.chk-r.hold{border-left:3px solid var(--err)}

/* Modules */
.mod-g{display:flex;flex-wrap:wrap;gap:6px}
.mod-c{display:flex;align-items:center;gap:5px;padding:5px 10px;background:var(--sf2);border-radius:4px;font-size:11px}
.mod-d{width:5px;height:5px;border-radius:50%;background:var(--ok)}

/* Pull to refresh hint */
.ptr{text-align:center;padding:12px;font-size:12px;color:var(--txm);display:none}
</style>
</head>
<body>

<div class="hdr">
  <div class="hdr-left"><div class="hdr-logo">E</div><span class="hdr-name">ELAINE</span></div>
  <div class="hdr-right">
    <div class="hdr-dot" id="hDot"></div>
    <button class="hdr-toggle" onclick="togTheme()" id="tBtn">&#9788; Light</button>
  </div>
</div>

<div class="tabs">
  <div class="tab on" data-p="dash">Dashboard</div>
  <div class="tab" data-p="chat">Chat</div>
  <div class="tab" data-p="gravity">Gravity</div>
  <div class="tab" data-p="gate">Gate</div>
  <div class="tab" data-p="check">Check</div>
</div>

<div class="pages">
  <!-- Dashboard -->
  <div class="page on" id="pg-dash">
    <div class="stats">
      <div class="cd"><div class="cd-lbl">Wellbeing</div><div class="cd-big" id="mWb">&mdash;</div><div class="wb"><div class="wb-f" id="mWbBar"></div></div></div>
      <div class="cd"><div class="cd-lbl">Modules</div><div class="cd-big" id="mMod">&mdash;</div><div class="cd-sub">active</div></div>
    </div>
    <div class="stats">
      <div class="cd"><div class="cd-lbl">Checked</div><div class="cd-big" id="mChk">0</div></div>
      <div class="cd"><div class="cd-lbl">Held</div><div class="cd-big" id="mHeld" style="color:var(--err)">0</div></div>
    </div>
    <div class="cd"><div class="cd-lbl">This Morning</div><div class="cd-txt" id="mBrief">Connecting...</div><div class="cd-em" id="mBriefC"></div></div>
    <div class="cd"><div class="cd-lbl">Top Priorities</div><div id="mGrav">&mdash;</div></div>
    <div class="cd"><div class="cd-lbl">Active Modules</div><div class="mod-g" id="mModG"></div></div>
  </div>

  <!-- Chat -->
  <div class="page" id="pg-chat">
    <div class="chat">
      <div class="chat-msgs" id="cMsgs">
        <div class="msg e"><div class="msg-w">Elaine</div><div class="msg-b" id="cHi">Connecting...</div></div>
      </div>
      <div class="chat-bar">
        <button class="chat-b mic" id="micB" onclick="togMic()">&#127908;</button>
        <input class="chat-in" id="cIn" placeholder="Talk to Elaine..." enterkeyhint="send">
        <button class="chat-b send" onclick="sendC()">&#10132;</button>
      </div>
    </div>
  </div>

  <!-- Gravity -->
  <div class="page" id="pg-gravity">
    <div class="cd"><div class="cd-lbl">Gravity Field</div><div id="gAll">Loading...</div></div>
  </div>

  <!-- Gatekeeper -->
  <div class="page" id="pg-gate">
    <div class="cd"><div class="cd-lbl">Gatekeeper Status</div><div id="gStats">Loading...</div></div>
    <div class="cd"><div class="cd-lbl">Outlook Rules</div><div id="gRules">Loading...</div></div>
    <div class="cd"><div class="cd-lbl">Watched Folders</div><div id="gFolders">Loading...</div></div>
  </div>

  <!-- Quick Check -->
  <div class="page" id="pg-check">
    <div class="cd">
      <div class="cd-lbl">Quick Check</div>
      <p style="color:var(--txm);font-size:12px;margin-bottom:10px">Paste content. Elaine scans through Sentinel, Compassion, and Communication before you send.</p>
      <textarea class="chk-ta" id="qC" placeholder="Paste email or message..."></textarea>
      <button class="chk-btn" onclick="runQ()">Check Before Sending</button>
      <div class="chk-r" id="qR"></div>
    </div>
  </div>
</div>

<script>
/* Theme */
function togTheme(){var h=document.documentElement,b=document.getElementById('tBtn');if(h.dataset.theme==='dark'){h.dataset.theme='light';b.innerHTML='&#9790; Dark';document.querySelector('meta[name=theme-color]').content='#F8F7F5'}else{h.dataset.theme='dark';b.innerHTML='&#9788; Light';document.querySelector('meta[name=theme-color]').content='#0A0E14'}try{localStorage.setItem('et',h.dataset.theme)}catch(e){}}
try{var sv=localStorage.getItem('et');if(sv==='light'){document.documentElement.dataset.theme='light';document.getElementById('tBtn').innerHTML='&#9790; Dark'}}catch(e){}

/* Tabs */
document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));document.querySelectorAll('.page').forEach(x=>x.classList.remove('on'));t.classList.add('on');document.getElementById('pg-'+t.dataset.p).classList.add('on')}));

/* API */
async function api(m,p,b){var o={method:m,headers:{'Content-Type':'application/json'}};if(b)o.body=JSON.stringify(b);var r=await fetch(p,o);return r.json()}

/* Load */
async function load(){try{
  var s=await api('GET','/api/status');if(s.error)throw s;
  document.getElementById('hDot').classList.remove('off');
  var mods=Object.keys(s.modules||{});
  document.getElementById('mMod').textContent=mods.length;
  document.getElementById('mModG').innerHTML=mods.map(m=>'<div class="mod-c"><div class="mod-d"></div>'+m+'</div>').join('');
  document.getElementById('cHi').innerHTML="Good morning, Mani.<br><br><small style='color:var(--txm)'>Try: priorities &middot; wellbeing &middot; briefing &middot; status &middot; check this</small>";

  try{var c=await api('GET','/api/compassion/wellbeing');var lv=c.wellbeing_level||'steady';var lvc=lv[0].toUpperCase()+lv.slice(1);document.getElementById('mWb').textContent=lvc;document.getElementById('mWbBar').className='wb-f '+lv;document.getElementById('mBrief').textContent=c.opening||"Here's what's on the radar.";document.getElementById('mBriefC').textContent=c.closing||''}catch(e){}
  try{var g=await api('GET','/api/gravity/top?limit=5');document.getElementById('mGrav').innerHTML=(g.items||[]).map(x=>{var m=x.mass||x.force||0,cl=m>=80?'red':m>=50?'amber':'green';return'<div class="gi"><div class="gi-f '+cl+'">'+Math.round(m)+'</div><div class="gi-n">'+(x.title||x.name||'')+'</div></div>'}).join('')||'<span style="color:var(--txm)">Clear</span>';
    document.getElementById('gAll').innerHTML=(g.items||[]).map(x=>{var m=x.mass||x.force||0,cl=m>=80?'red':m>=50?'amber':'green';return'<div class="gi"><div class="gi-f '+cl+'">'+Math.round(m)+'</div><div class="gi-n">'+(x.title||x.name||'')+'</div></div>'}).join('')||'<span style="color:var(--txm)">Field clear</span>'}catch(e){}
  try{var gt=await api('GET','/api/gatekeeper/status');document.getElementById('mChk').textContent=gt.items_checked||0;document.getElementById('mHeld').textContent=gt.items_held||0;
    document.getElementById('gStats').innerHTML=[['Checked',gt.items_checked||0],['Held',gt.items_held||0,'var(--err)'],['Overrides',gt.overrides||0],['Folders',gt.watched_folders||0],['Rules',gt.outlook_rules||0]].map(r=>'<div class="gr"><span class="gr-l">'+r[0]+'</span><span class="gr-v"'+(r[2]?' style="color:'+r[2]+'"':'')+'>'+r[1]+'</span></div>').join('')}catch(e){}
  try{var ru=await api('GET','/api/gatekeeper/outlook-rules');document.getElementById('gRules').innerHTML=(ru.rules||[]).map(r=>'<div class="gr"><span class="gr-l">'+r.name+'</span><span class="gr-v">'+r.priority+'</span></div>').join('')||'None'}catch(e){}
  try{var fo=await api('GET','/api/gatekeeper/folders');document.getElementById('gFolders').innerHTML=(fo.folders||[]).map(f=>'<div class="gr"><span class="gr-l" style="font-size:11px;word-break:break-all">'+f.path+'</span><span class="gr-v">'+f.priority+'</span></div>').join('')||'None'}catch(e){}
}catch(e){document.getElementById('hDot').classList.add('off');document.getElementById('mBrief').textContent='Server offline'}}

/* Chat */
var cMsgs=document.getElementById('cMsgs'),cIn=document.getElementById('cIn');
function addM(t,s){var d=document.createElement('div');d.className='msg '+(s==='user'?'u':'e');d.innerHTML='<div class="msg-w">'+(s==='user'?'You':'Elaine')+'</div><div class="msg-b">'+t+'</div>';cMsgs.appendChild(d);cMsgs.scrollTop=cMsgs.scrollHeight}
cIn.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();sendC()}});

async function sendC(){var t=cIn.value.trim();if(!t)return;cIn.value='';addM(t,'user');var l=t.toLowerCase();
try{var r;
  if(l.match(/gravit|priorit|what should|top/)){r=await api('GET','/api/gravity/top?limit=5');addM(r.items&&r.items.length?'Gravity field:<br><br>'+r.items.map((x,i)=>(i+1)+'. <b>'+(x.title||x.name)+'</b> ('+Math.round(x.mass||x.force||0)+')').join('<br>'):'Field clear.','e')}
  else if(l.match(/how am|wellbeing|feeling|energy/)){r=await api('GET','/api/compassion/wellbeing');addM((r.opening||'Steady.')+'<br><br>Wellbeing: <b>'+(r.wellbeing_level||'steady')+'</b><br><br><em>'+(r.closing||'')+'</em>','e')}
  else if(l.match(/check|review|before i send|scan/)){r=await api('POST','/api/gatekeeper/check',{content:t,title:'Chat'});var v=r.verdict||'clear',ic=v==='clear'?'🟢':v==='review'?'🟡':'🔴';addM(ic+' <b>'+v.toUpperCase()+'</b> ('+Math.round((r.score||1)*100)+'%)<br>'+(r.summary||''),'e');load()}
  else if(l.match(/gate/)){r=await api('GET','/api/gatekeeper/status');addM((r.items_checked||0)+' checked, '+(r.items_held||0)+' held.','e')}
  else if(l.match(/morning|briefing|good morning/)){r=await api('GET','/api/compassion/wellbeing');addM((r.opening||'Morning.')+'<br><em>'+(r.closing||'')+'</em>','e')}
  else if(l.match(/status|module|system/)){r=await api('GET','/api/status');addM('<b>'+Object.keys(r.modules||{}).length+'</b> modules active.','e')}
  else if(l.match(/learn|interest|read/)){r=await api('GET','/api/learning/interests');addM(r.interests&&r.interests.length?r.interests.map(i=>'• '+i.topic).join('<br>'):'No interests yet.','e')}
  else{addM("Try: <b>priorities</b>, <b>wellbeing</b>, <b>briefing</b>, <b>status</b>, <b>learning</b>, or <b>check this</b> + content.",'e')}
}catch(e){addM("Server unreachable.",'e')}}

/* Mic */
var rec=null,isR=false;
if('webkitSpeechRecognition' in window||'SpeechRecognition' in window){var SR=window.SpeechRecognition||window.webkitSpeechRecognition;rec=new SR();rec.continuous=false;rec.interimResults=false;rec.lang='en-AU';rec.onresult=function(e){cIn.value=e.results[0][0].transcript;sendC()};rec.onend=function(){isR=false;document.getElementById('micB').classList.remove('rec')};rec.onerror=rec.onend}
function togMic(){if(!rec){addM('Speech not available.','e');return}if(isR){rec.stop()}else{rec.start();isR=true;document.getElementById('micB').classList.add('rec')}}

/* Quick Check */
async function runQ(){var c=document.getElementById('qC').value;if(!c.trim())return;var b=document.getElementById('qR');b.style.display='block';b.className='chk-r';b.textContent='Checking...';try{var r=await api('POST','/api/gatekeeper/check',{content:c,title:'Mobile check'});var v=r.verdict||'clear';b.className='chk-r '+v;b.innerHTML='<b>'+v.toUpperCase()+'</b> ('+Math.round((r.score||1)*100)+'%)<br>'+(r.summary||'');load()}catch(e){b.textContent='Error'}}

load();setInterval(load,30000);
</script>
</body>
</html>'''
