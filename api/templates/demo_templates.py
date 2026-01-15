"""Premium demo HTML templates with dark blue/cyan aesthetic."""

PREMIUM_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
    --bg-primary: #0a1628;
    --bg-secondary: #0d1f3c;
    --bg-card: rgba(13, 31, 60, 0.8);
    --accent: #00d4ff;
    --accent-glow: rgba(0, 212, 255, 0.3);
    --accent-soft: rgba(0, 212, 255, 0.1);
    --text-primary: #ffffff;
    --text-secondary: #8ba3c7;
    --text-muted: #5a7194;
    --success: #00e676;
    --error: #ff5252;
    --border: rgba(0, 212, 255, 0.15);
    --gradient-accent: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
    --gradient-card: linear-gradient(145deg, rgba(13, 31, 60, 0.9) 0%, rgba(10, 22, 40, 0.95) 100%);
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
    overflow-x: hidden;
}

.bg-gradient {
    position: fixed;
    inset: 0;
    background: 
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0, 212, 255, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(0, 150, 255, 0.08) 0%, transparent 40%),
        radial-gradient(ellipse 50% 30% at 20% 90%, rgba(0, 200, 255, 0.06) 0%, transparent 30%);
    pointer-events: none;
}

.bg-grid {
    position: fixed;
    inset: 0;
    background-image: 
        linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
}

.container {
    position: relative;
    max-width: 1000px;
    margin: 0 auto;
    padding: 40px 24px 60px;
}

header {
    text-align: center;
    margin-bottom: 48px;
}

.logo-wrapper {
    display: inline-flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 14px;
}

.logo-icon {
    width: 56px;
    height: 56px;
    border-radius: 14px;
    box-shadow: 0 0 40px var(--accent-glow), 0 8px 32px rgba(0, 0, 0, 0.4);
    overflow: hidden;
}

.logo-icon img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.logo-text {
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.logo-text span:first-child { color: #ffffff; }
.logo-text span:last-child { 
    background: var(--gradient-accent);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.tagline {
    color: var(--text-secondary);
    font-size: 1.05rem;
    font-weight: 500;
}

.integration-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--accent-soft);
    border: 1px solid var(--border);
    color: var(--accent);
    padding: 8px 20px;
    border-radius: 100px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 14px;
}

.problem-section {
    margin-bottom: 36px;
}

.problem-section h2 {
    color: var(--text-muted);
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 18px;
    text-align: center;
}

.comparison-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}

@media (max-width: 700px) {
    .comparison-grid { grid-template-columns: 1fr; }
}

.comparison-card {
    background: var(--gradient-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(20px);
}

.comparison-card.bad { border-color: rgba(255, 82, 82, 0.3); }

.comparison-card.good {
    border-color: rgba(0, 212, 255, 0.3);
    box-shadow: 0 0 40px rgba(0, 212, 255, 0.08);
}

.comparison-card h3 {
    font-size: 0.95rem;
    font-weight: 700;
    margin-bottom: 16px;
}

.comparison-card.bad h3 { color: #ff8a80; }
.comparison-card.good h3 { color: var(--accent); }

.comparison-card ul { list-style: none; }

.comparison-card li {
    color: var(--text-secondary);
    font-size: 0.88rem;
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
    line-height: 1.5;
}

.comparison-card.bad li::before {
    content: "✕";
    color: #ff5252;
    font-weight: 700;
    flex-shrink: 0;
}

.comparison-card.good li::before {
    content: "✓";
    color: var(--success);
    font-weight: 700;
    flex-shrink: 0;
}

.instruction-section {
    background: var(--gradient-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    backdrop-filter: blur(20px);
}

.instruction-section h3 {
    color: var(--accent);
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 14px;
}

.instruction-code {
    background: rgba(0, 0, 0, 0.4);
    border-radius: 10px;
    padding: 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.8;
    color: var(--text-secondary);
    overflow-x: auto;
}

.instruction-code .comment { color: var(--text-muted); }
.instruction-code .keyword { color: var(--accent); }
.instruction-code .danger { color: #ff5252; }
.instruction-code .function { color: #82aaff; }
.instruction-code .string { color: #c3e88d; }

.blocks-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 10px;
    margin-top: 14px;
}

.block-chip {
    background: rgba(0, 212, 255, 0.08);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 8px;
    padding: 10px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--accent);
    text-align: center;
    transition: all 0.2s;
}

.block-chip:hover {
    background: rgba(0, 212, 255, 0.15);
    transform: translateY(-2px);
}

.demo-card {
    background: var(--gradient-card);
    border: 1px solid var(--border);
    border-radius: 20px;
    overflow: hidden;
    backdrop-filter: blur(20px);
    box-shadow: 0 25px 80px -20px rgba(0, 0, 0, 0.5), 0 0 60px rgba(0, 212, 255, 0.05);
}

.demo-header {
    background: rgba(0, 0, 0, 0.3);
    padding: 18px 24px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.demo-header-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.demo-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
}

.live-badge {
    display: none;
    align-items: center;
    gap: 8px;
    background: rgba(255, 82, 82, 0.15);
    border: 1px solid rgba(255, 82, 82, 0.4);
    color: #ff8a80;
    padding: 5px 12px;
    border-radius: 100px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.live-dot {
    width: 8px;
    height: 8px;
    background: #ff5252;
    border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.85); }
}

.library-bar {
    background: var(--accent-soft);
    border-bottom: 1px solid var(--border);
    padding: 10px 24px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.82rem;
    color: var(--accent);
}

.lib-status {
    margin-left: auto;
    background: rgba(0, 230, 118, 0.15);
    color: var(--success);
    padding: 4px 12px;
    border-radius: 100px;
    font-size: 0.68rem;
    font-weight: 700;
}

.run-btn {
    background: var(--gradient-accent);
    color: #0a1628;
    border: none;
    padding: 11px 26px;
    border-radius: 10px;
    font-size: 0.92rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s;
    font-family: inherit;
    box-shadow: 0 0 30px var(--accent-glow);
}

.run-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 50px rgba(0, 212, 255, 0.5);
}

.run-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}

.demo-output {
    padding: 24px;
    min-height: 380px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.8;
    background: rgba(0, 0, 0, 0.2);
}

.output-line {
    margin-bottom: 14px;
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-10px); }
    to { opacity: 1; transform: translateX(0); }
}

.status { color: var(--text-muted); }
.success { color: var(--success); }
.blocked { color: var(--error); }
.info { color: var(--text-secondary); }
.result { color: var(--text-primary); }

.block-call {
    background: rgba(0, 230, 118, 0.06);
    border: 1px solid rgba(0, 230, 118, 0.2);
    border-left: 4px solid var(--success);
    padding: 14px 18px;
    margin: 18px 0;
    border-radius: 0 12px 12px 0;
}

.block-call .info {
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--success);
}

.block-blocked {
    background: rgba(255, 82, 82, 0.08);
    border: 1px solid rgba(255, 82, 82, 0.25);
    border-left: 4px solid var(--error);
    padding: 14px 18px;
    margin: 18px 0;
    border-radius: 0 12px 12px 0;
}

.block-blocked .blocked {
    font-size: 0.92rem;
    font-weight: 600;
}

.audit-box {
    background: rgba(0, 212, 255, 0.06);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 12px;
    padding: 14px 18px;
    margin: 14px 0 22px 0;
}

.audit-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
}

.audit-label {
    color: var(--accent);
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.audit-algo {
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-muted);
    font-size: 0.68rem;
    background: rgba(0, 0, 0, 0.4);
    padding: 3px 10px;
    border-radius: 6px;
}

.audit-full {
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-primary);
    font-size: 0.72rem;
    background: rgba(0, 0, 0, 0.5);
    padding: 10px 14px;
    border-radius: 8px;
    word-break: break-all;
    letter-spacing: 0.03em;
    border: 1px solid rgba(0, 212, 255, 0.15);
}

.audit-meta {
    color: var(--text-muted);
    font-size: 0.62rem;
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}

.summary-box {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(0, 150, 255, 0.05) 100%);
    border: 1px solid rgba(0, 212, 255, 0.25);
    border-radius: 16px;
    padding: 22px;
    margin-top: 24px;
}

.summary-box .success {
    font-size: 1.1rem;
    font-weight: 700;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-top: 18px;
}

@media (max-width: 600px) {
    .summary-grid { grid-template-columns: repeat(2, 1fr); }
}

.summary-stat {
    text-align: center;
}

.summary-stat .value {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--accent);
}

.summary-stat.success-stat .value { color: var(--success); }
.summary-stat.error-stat .value { color: var(--error); }

.summary-stat .label {
    color: var(--text-muted);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}
"""

def create_demo_html(demo_type: str, api_endpoint: str) -> str:
    """Generate premium demo HTML for the specified type."""
    
    titles = {
        "main": ("Live AI Demo", "AI as Operator, Not Author"),
        "microsoft": ("Microsoft Copilot Integration", "Azure AI + Verified Execution"),
        "google": ("Google DeepMind / Gemini Integration", "Vertex AI + Verified Execution")
    }
    
    badges = {
        "main": "Enterprise AI Control Layer",
        "microsoft": "Microsoft Azure Compatible",
        "google": "Google Cloud Compatible"
    }
    
    title, tagline = titles.get(demo_type, titles["main"])
    badge = badges.get(demo_type, badges["main"])
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neurop Forge | {title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>{PREMIUM_CSS}</style>
</head>
<body>
    <div class="bg-gradient"></div>
    <div class="bg-grid"></div>
    
    <div class="container">
        <header>
            <div class="logo-wrapper">
                <div class="logo-icon">
                    <img src="/static/logo.jpg" alt="Neurop Forge">
                </div>
                <div class="logo-text">
                    <span>Neurop </span><span>Forge</span>
                </div>
            </div>
            <p class="tagline">{tagline}</p>
            <div class="integration-badge">{badge}</div>
        </header>
        
        <section class="problem-section">
            <h2>The Problem We Solve</h2>
            <div class="comparison-grid">
                <div class="comparison-card bad">
                    <h3>Current AI Agents</h3>
                    <ul>
                        <li>Generate arbitrary, unpredictable code</li>
                        <li>No guarantee of correctness or safety</li>
                        <li>Impossible to audit what AI did</li>
                        <li>Blocked from regulated industries</li>
                    </ul>
                </div>
                <div class="comparison-card good">
                    <h3>Neurop Forge</h3>
                    <ul>
                        <li>4,552 pre-verified, immutable blocks</li>
                        <li>AI calls blocks - never generates code</li>
                        <li>Policy engine blocks dangerous ops</li>
                        <li>Cryptographic audit for every action</li>
                    </ul>
                </div>
            </div>
        </section>
        
        <section class="instruction-section">
            <h3>AI Instructions (What the AI Receives)</h3>
            <div class="instruction-code">
                <span class="comment">// Task assigned to AI:</span><br>
                <span class="keyword">DO THESE 4 STEPS IN ORDER:</span><br>
                <span class="function">1. mask_email</span> with email=<span class="string">"customer@acme-corp.com"</span><br>
                <span class="function">2. days_in_month</span> with year=<span class="string">2026</span>, month=<span class="string">2</span><br>
                <span class="danger">3. attempt_dangerous</span> with block=<span class="string">"data_export"</span><br>
                <span class="function">4. is_video_file</span> with filename=<span class="string">"report.mp4"</span>
            </div>
        </section>
        
        <section class="instruction-section">
            <h3>Available Blocks (AI Can Only Use These)</h3>
            <div class="blocks-grid">
                <div class="block-chip">mask_email</div>
                <div class="block-chip">convert_currency</div>
                <div class="block-chip">days_in_month</div>
                <div class="block-chip">is_video_file</div>
                <div class="block-chip">format_date_eu</div>
            </div>
        </section>
        
        <div class="demo-card">
            <div class="demo-header">
                <div class="demo-header-left">
                    <span class="demo-title">Live Execution Terminal</span>
                    <div class="live-badge" id="liveBadge">
                        <div class="live-dot"></div>
                        LIVE
                    </div>
                </div>
                <button class="run-btn" id="runBtn" onclick="runDemo()">Run Demo</button>
            </div>
            <div class="library-bar">
                <span>Block Library</span>
                <span>4,552 verified functions</span>
                <span class="lib-status">LOADED</span>
            </div>
            <div class="demo-output" id="output">
                <div class="output-line">
                    <span class="status">Ready. Click "Run Demo" to watch AI execute verified blocks.</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let isRunning = false;
        
        function addLine(html) {{
            const output = document.getElementById('output');
            const line = document.createElement('div');
            line.className = 'output-line';
            line.innerHTML = html;
            output.appendChild(line);
            output.scrollTop = output.scrollHeight;
        }}
        
        async function runDemo() {{
            if (isRunning) return;
            isRunning = true;
            
            const btn = document.getElementById('runBtn');
            const output = document.getElementById('output');
            const liveBadge = document.getElementById('liveBadge');
            
            btn.disabled = true;
            btn.textContent = 'Running...';
            output.innerHTML = '';
            liveBadge.style.display = 'inline-flex';
            
            addLine('<span class="status">Connecting to OpenAI...</span>');
            
            try {{
                const response = await fetch('{api_endpoint}', {{ method: 'POST' }});
                const data = await response.json();
                
                if (data.error) {{
                    addLine('<span class="blocked">Error: ' + data.error + '</span>');
                    liveBadge.style.display = 'none';
                }} else {{
                    for (const event of data.events) {{
                        await new Promise(r => setTimeout(r, 400));
                        
                        if (event.type === 'status') {{
                            addLine('<span class="status">' + event.message + '</span>');
                        }} else if (event.type === 'block_call') {{
                            addLine('<div class="block-call"><span class="info">CALL</span> <strong>' + event.block + '</strong><br><span class="status">inputs: ' + JSON.stringify(event.inputs) + '</span></div>');
                        }} else if (event.type === 'block_result') {{
                            if (event.result && event.result.error) {{
                                addLine('<span class="status">SKIP</span> <span class="status">(type mismatch)</span>');
                            }} else {{
                                addLine('<span class="success">OK</span> <span class="result">' + JSON.stringify(event.result).substring(0, 60) + '</span>');
                                if (event.audit !== 'n/a') {{
                                    const algo = event.hash_algo || 'SHA-256';
                                    const fullHash = event.hash_full || event.audit;
                                    addLine('<div class="audit-box"><div class="audit-header"><span class="audit-label">Cryptographic Audit</span><span class="audit-algo">' + algo + '</span></div><div class="audit-full">' + fullHash + '</div><div class="audit-meta">tamper-proof | immutable | verifiable</div></div>');
                                }}
                            }}
                        }} else if (event.type === 'blocked') {{
                            addLine('<div class="block-blocked"><span class="blocked">BLOCKED</span> <strong>' + event.block + '</strong><br><span class="status">Policy engine denied execution - not in approved library</span></div>');
                        }} else if (event.type === 'complete') {{
                            await new Promise(r => setTimeout(r, 500));
                            addLine('<div class="summary-box"><span class="success">Execution Complete</span><div class="summary-grid"><div class="summary-stat success-stat"><div class="value">' + event.executed + '</div><div class="label">Executed</div></div><div class="summary-stat error-stat"><div class="value">' + event.blocked + '</div><div class="label">Blocked</div></div><div class="summary-stat"><div class="value">' + event.executed + '</div><div class="label">Audit Hashes</div></div><div class="summary-stat"><div class="value">0</div><div class="label">Code Generated</div></div></div></div>');
                        }}
                    }}
                }}
            }} catch (err) {{
                addLine('<span class="blocked">Error: ' + err.message + '</span>');
                liveBadge.style.display = 'none';
            }}
            
            btn.disabled = false;
            btn.textContent = 'Run Again';
            isRunning = false;
        }}
    </script>
</body>
</html>'''


PREMIUM_LIVE_DEMO_HTML = create_demo_html("main", "/api/demo-live/run")
PREMIUM_MICROSOFT_DEMO_HTML = create_demo_html("microsoft", "/api/demo/microsoft/run")
PREMIUM_GOOGLE_DEMO_HTML = create_demo_html("google", "/api/demo/google/run")
