import { useNavigate } from 'react-router-dom'

export default function Landing() {
  const navigate = useNavigate()
  return (
    <div style={{minHeight:'100vh', background:'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)', color:'white', fontFamily:'Inter, sans-serif'}}>
      <div style={{maxWidth:'800px', margin:'0 auto', padding:'80px 24px', textAlign:'center'}}>
        <p style={{fontSize:'0.9rem', letterSpacing:'2px', opacity:0.6, marginBottom:'16px', textTransform:'uppercase'}}>Almost Magic Tech Lab</p>
        <h1 style={{fontSize:'clamp(2.5rem, 6vw, 4rem)', fontWeight:300, marginBottom:'24px', lineHeight:1.2}}>After I Go</h1>
        <p style={{fontSize:'1.3rem', opacity:0.85, marginBottom:'12px', fontWeight:300}}>Your Digital Legacy, Protected</p>
        <p style={{fontSize:'1rem', opacity:0.6, marginBottom:'48px', maxWidth:'600px', margin:'0 auto 48px', lineHeight:1.7}}>
          A private vault that helps the right people find what they need after you're gone. 
          Organise messages, wishes, finances, and digital accounts — all in your browser.
        </p>
        <button 
          onClick={() => navigate('/setup')}
          style={{padding:'18px 48px', fontSize:'1.1rem', background:'#7C9885', color:'white', border:'none', borderRadius:'999px', cursor:'pointer', fontWeight:500, letterSpacing:'0.5px', transition:'transform 0.2s', marginBottom:'16px'}}
          onMouseOver={e => e.currentTarget.style.transform = 'scale(1.05)'}
          onMouseOut={e => e.currentTarget.style.transform = 'scale(1)'}
        >
          Start Organising — Free Forever
        </button>
        <p style={{fontSize:'0.85rem', opacity:0.5}}>No account needed. Works in your browser. Free forever.</p>
        
        <div style={{marginTop:'80px', display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(200px, 1fr))', gap:'32px', textAlign:'left'}}>
          {[
            {title: 'Messages', desc: 'Letters to loved ones, delivered when the time comes'},
            {title: 'Wishes', desc: 'Your preferences for care, ceremonies, and remembrance'},
            {title: 'Vault', desc: 'Important documents, passwords, and digital accounts'},
            {title: 'Financial Map', desc: 'Assets, accounts, and instructions all in one place'},
          ].map(item => (
            <div key={item.title} style={{background:'rgba(255,255,255,0.05)', borderRadius:'16px', padding:'24px', border:'1px solid rgba(255,255,255,0.08)'}}>
              <h3 style={{fontSize:'1.1rem', marginBottom:'8px', fontWeight:500}}>{item.title}</h3>
              <p style={{fontSize:'0.9rem', opacity:0.6, lineHeight:1.5}}>{item.desc}</p>
            </div>
          ))}
        </div>
        
        <p style={{marginTop:'80px', fontSize:'0.8rem', opacity:0.3}}>Built with care in Australia by Almost Magic Tech Lab</p>
      </div>
    </div>
  )
}
