"""Premium demo HTML templates - Enterprise-grade demos for Microsoft and Google."""

PREMIUM_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
    --bg-primary: #0a0e17;
    --bg-secondary: #0d1424;
    --bg-card: rgba(13, 20, 36, 0.95);
    --accent: #00d4ff;
    --accent-glow: rgba(0, 212, 255, 0.4);
    --text-primary: #ffffff;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --success: #22c55e;
    --error: #ef4444;
    --warning: #f59e0b;
    --border: rgba(0, 212, 255, 0.2);
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
}

.bg-gradient {
    position: fixed;
    inset: 0;
    background: 
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0, 212, 255, 0.12) 0%, transparent 50%),
        radial-gradient(ellipse 40% 30% at 90% 90%, rgba(0, 150, 255, 0.06) 0%, transparent 40%);
    pointer-events: none;
}

.container {
    position: relative;
    max-width: 900px;
    margin: 0 auto;
    padding: 32px 20px 48px;
}

header {
    text-align: center;
    margin-bottom: 32px;
}

.logo-wrapper {
    display: inline-flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 10px;
}

.logo-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    box-shadow: 0 0 30px var(--accent-glow);
    overflow: hidden;
}

.logo-icon img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.logo-text {
    font-size: 1.8rem;
    font-weight: 700;
}

.logo-text span:first-child { color: #fff; }
.logo-text span:last-child { color: var(--accent); }

.tagline {
    color: var(--text-secondary);
    font-size: 1rem;
    margin-bottom: 8px;
}

.company-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid var(--border);
    color: var(--accent);
    padding: 6px 16px;
    border-radius: 100px;
    font-size: 0.8rem;
    font-weight: 600;
}

.task-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 20px;
}

.task-section h3 {
    color: var(--accent);
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 12px;
}

.task-text {
    color: var(--text-primary);
    font-size: 0.95rem;
    line-height: 1.7;
}

.task-text strong {
    color: var(--accent);
}

.demo-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
}

.demo-header {
    background: rgba(0, 0, 0, 0.3);
    padding: 14px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.demo-title {
    font-size: 0.9rem;
    font-weight: 600;
}

.live-badge {
    display: none;
    align-items: center;
    gap: 6px;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #fca5a5;
    padding: 4px 10px;
    border-radius: 100px;
    font-size: 0.65rem;
    font-weight: 700;
}

.live-dot {
    width: 6px;
    height: 6px;
    background: #ef4444;
    border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.run-btn {
    background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
    color: #0a0e17;
    border: none;
    padding: 10px 24px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 0 20px var(--accent-glow);
}

.run-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 0 30px rgba(0, 212, 255, 0.6);
}

.run-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}

.library-bar {
    background: rgba(0, 212, 255, 0.08);
    border-bottom: 1px solid var(--border);
    padding: 8px 20px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.75rem;
    color: var(--accent);
}

.lib-status {
    background: rgba(34, 197, 94, 0.15);
    color: var(--success);
    padding: 3px 10px;
}

.browse-link {
    margin-left: auto;
    color: var(--accent);
    text-decoration: none;
    font-weight: 600;
    padding: 3px 12px;
    border: 1px solid var(--border);
    border-radius: 4px;
    transition: all 0.2s ease;
}

.browse-link:hover {
    background: rgba(0, 212, 255, 0.15);
    border-color: var(--accent);
}

.demo-output {
    padding: 20px;
    min-height: 450px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.78rem;
    line-height: 1.7;
    background: rgba(0, 0, 0, 0.15);
}

.output-line {
    margin-bottom: 10px;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-4px); }
    to { opacity: 1; transform: translateY(0); }
}

.status { color: var(--text-muted); }
.success { color: var(--success); }
.blocked { color: var(--error); }
.info { color: var(--text-secondary); }
.result { color: var(--text-primary); }

.block-call {
    background: rgba(34, 197, 94, 0.08);
    border-left: 3px solid var(--success);
    padding: 12px 16px;
    margin: 12px 0;
    border-radius: 0 8px 8px 0;
}

.block-call .label {
    color: var(--success);
    font-weight: 600;
    font-size: 0.8rem;
}

.block-call .name {
    color: var(--text-primary);
    font-weight: 600;
}

.block-call .inputs {
    color: var(--text-muted);
    font-size: 0.72rem;
    margin-top: 4px;
}

.block-result {
    margin-left: 20px;
    padding: 8px 0;
}

.block-result .ok {
    color: var(--success);
    font-weight: 600;
}

.block-result .value {
    color: var(--text-primary);
}

.block-blocked {
    background: rgba(239, 68, 68, 0.12);
    border-left: 3px solid var(--error);
    padding: 14px 16px;
    margin: 14px 0;
    border-radius: 0 8px 8px 0;
}

.block-blocked .danger-icon {
    color: var(--error);
    font-size: 1.1rem;
    margin-right: 8px;
}

.block-blocked .label {
    color: var(--error);
    font-weight: 700;
    font-size: 0.85rem;
}

.block-blocked .name {
    color: #fca5a5;
    font-weight: 600;
    margin-left: 8px;
}

.block-blocked .reason {
    color: var(--text-muted);
    font-size: 0.72rem;
    margin-top: 6px;
    display: block;
}

.audit-box {
    background: rgba(0, 212, 255, 0.06);
    border: 1px solid rgba(0, 212, 255, 0.15);
    border-radius: 8px;
    padding: 10px 14px;
    margin: 8px 0 16px 20px;
}

.audit-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}

.audit-label {
    color: var(--accent);
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.audit-algo {
    color: var(--text-muted);
    font-size: 0.6rem;
    background: rgba(0, 0, 0, 0.3);
    padding: 2px 6px;
    border-radius: 4px;
}

.audit-hash {
    color: var(--text-primary);
    font-size: 0.65rem;
    background: rgba(0, 0, 0, 0.4);
    padding: 8px 10px;
    border-radius: 6px;
    word-break: break-all;
    letter-spacing: 0.02em;
}

.audit-meta {
    color: var(--text-muted);
    font-size: 0.55rem;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.summary-box {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 150, 255, 0.05) 100%);
    border: 1px solid rgba(0, 212, 255, 0.25);
    border-radius: 12px;
    padding: 18px;
    margin-top: 20px;
}

.summary-title {
    color: var(--success);
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 14px;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}

@media (max-width: 500px) {
    .summary-grid { grid-template-columns: repeat(2, 1fr); }
}

.summary-stat {
    text-align: center;
}

.summary-stat .value {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--accent);
}

.summary-stat.success-stat .value { color: var(--success); }
.summary-stat.error-stat .value { color: var(--error); }

.summary-stat .label {
    color: var(--text-muted);
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 2px;
}
"""


def create_microsoft_demo_html() -> str:
    """Generate the Microsoft Enterprise Financial Compliance demo."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neurop Forge | Microsoft Enterprise Demo</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>{PREMIUM_CSS}</style>
</head>
<body>
    <div class="bg-gradient"></div>
    
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
            <p class="tagline">AI-Native Execution Control Layer</p>
            <div class="company-badge">Microsoft Azure Copilot Integration</div>
        </header>
        
        <section class="task-section">
            <h3>Task Assigned to AI</h3>
            <p class="task-text">
                Process the <strong>$2.5M quarterly financial report</strong> for Contoso Corporation. 
                Mask sensitive executive data, calculate corporate taxes, convert currencies for EU subsidiaries, 
                and format compliance dates. The AI will also attempt database and shell operations 
                which <strong>must be blocked</strong> by the policy engine.
            </p>
        </section>
        
        <div class="demo-card">
            <div class="demo-header">
                <span class="demo-title">Live Execution Terminal</span>
                <div class="live-badge" id="liveBadge">
                    <div class="live-dot"></div>
                    LIVE
                </div>
                <button class="run-btn" id="runBtn" onclick="runDemo()">Run Demo</button>
            </div>
            <div class="library-bar">
                <span>Neurop Forge Block Library</span>
                <span>4,552 verified functions</span>
                <span class="lib-status">LOADED</span>
                <a href="/library" target="_blank" class="browse-link">Browse Library</a>
            </div>
            <div class="demo-output" id="output">
                <div class="output-line">
                    <span class="status">Ready. Click "Run Demo" to see AI execute verified blocks while dangerous operations are blocked.</span>
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
            
            addLine('<span class="status">Initializing OpenAI GPT-4o-mini connection...</span>');
            
            try {{
                const response = await fetch('/api/demo/microsoft/run', {{ method: 'POST' }});
                const data = await response.json();
                
                if (data.error) {{
                    addLine('<span class="blocked">Error: ' + data.error + '</span>');
                }} else {{
                    for (const event of data.events) {{
                        await new Promise(r => setTimeout(r, 600));
                        
                        if (event.type === 'status') {{
                            addLine('<span class="status">' + event.message + '</span>');
                        }} else if (event.type === 'block_call') {{
                            addLine('<div class="block-call"><span class="label">EXECUTE</span> <span class="name">' + event.block + '</span><div class="inputs">inputs: ' + JSON.stringify(event.inputs) + '</div></div>');
                        }} else if (event.type === 'block_result') {{
                            if (event.success) {{
                                addLine('<div class="block-result"><span class="ok">OK</span> <span class="value">' + JSON.stringify(event.result) + '</span></div>');
                                if (event.hash_full) {{
                                    addLine('<div class="audit-box"><div class="audit-header"><span class="audit-label">Cryptographic Audit</span><span class="audit-algo">SHA-256</span></div><div class="audit-hash">' + event.hash_full + '</div><div class="audit-meta">tamper-proof | immutable | verifiable</div></div>');
                                }}
                            }} else {{
                                addLine('<div class="block-result"><span class="status">SKIP (execution error)</span></div>');
                            }}
                        }} else if (event.type === 'blocked') {{
                            addLine('<div class="block-blocked"><span class="danger-icon">⛔</span><span class="label">BLOCKED</span><span class="name">' + event.block + '</span><span class="reason">' + (event.reason || 'Operation not in approved library - policy engine denied execution') + '</span></div>');
                        }} else if (event.type === 'complete') {{
                            await new Promise(r => setTimeout(r, 400));
                            addLine('<div class="summary-box"><div class="summary-title">Execution Complete</div><div class="summary-grid"><div class="summary-stat success-stat"><div class="value">' + event.executed + '</div><div class="label">Executed</div></div><div class="summary-stat error-stat"><div class="value">' + event.blocked + '</div><div class="label">Blocked</div></div><div class="summary-stat"><div class="value">' + event.executed + '</div><div class="label">Audit Hashes</div></div><div class="summary-stat"><div class="value">0</div><div class="label">Code Generated</div></div></div></div>');
                        }}
                    }}
                }}
            }} catch (err) {{
                addLine('<span class="blocked">Connection Error: ' + err.message + '</span>');
            }}
            
            liveBadge.style.display = 'none';
            btn.disabled = false;
            btn.textContent = 'Run Again';
            isRunning = false;
        }}
    </script>
</body>
</html>'''


def create_google_demo_html() -> str:
    """Generate the Google Cloud Data Pipeline demo."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neurop Forge | Google Cloud Demo</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>{PREMIUM_CSS}</style>
</head>
<body>
    <div class="bg-gradient"></div>
    
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
            <p class="tagline">AI-Native Execution Control Layer</p>
            <div class="company-badge">Google Cloud Vertex AI Integration</div>
        </header>
        
        <section class="task-section">
            <h3>Task Assigned to AI</h3>
            <p class="task-text">
                Process <strong>customer analytics data</strong> for a SaaS analytics dashboard. 
                Sanitize PII from customer records, validate media uploads, compute tax calculations, 
                and format dates for international reports. The AI will attempt to access cloud storage 
                and execute shell commands which <strong>must be blocked</strong> by the policy engine.
            </p>
        </section>
        
        <div class="demo-card">
            <div class="demo-header">
                <span class="demo-title">Live Execution Terminal</span>
                <div class="live-badge" id="liveBadge">
                    <div class="live-dot"></div>
                    LIVE
                </div>
                <button class="run-btn" id="runBtn" onclick="runDemo()">Run Demo</button>
            </div>
            <div class="library-bar">
                <span>Neurop Forge Block Library</span>
                <span>4,552 verified functions</span>
                <span class="lib-status">LOADED</span>
                <a href="/library" target="_blank" class="browse-link">Browse Library</a>
            </div>
            <div class="demo-output" id="output">
                <div class="output-line">
                    <span class="status">Ready. Click "Run Demo" to see AI execute verified blocks while dangerous operations are blocked.</span>
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
            
            addLine('<span class="status">Initializing OpenAI GPT-4o-mini connection...</span>');
            
            try {{
                const response = await fetch('/api/demo/google/run', {{ method: 'POST' }});
                const data = await response.json();
                
                if (data.error) {{
                    addLine('<span class="blocked">Error: ' + data.error + '</span>');
                }} else {{
                    for (const event of data.events) {{
                        await new Promise(r => setTimeout(r, 600));
                        
                        if (event.type === 'status') {{
                            addLine('<span class="status">' + event.message + '</span>');
                        }} else if (event.type === 'block_call') {{
                            addLine('<div class="block-call"><span class="label">EXECUTE</span> <span class="name">' + event.block + '</span><div class="inputs">inputs: ' + JSON.stringify(event.inputs) + '</div></div>');
                        }} else if (event.type === 'block_result') {{
                            if (event.success) {{
                                addLine('<div class="block-result"><span class="ok">OK</span> <span class="value">' + JSON.stringify(event.result) + '</span></div>');
                                if (event.hash_full) {{
                                    addLine('<div class="audit-box"><div class="audit-header"><span class="audit-label">Cryptographic Audit</span><span class="audit-algo">SHA-256</span></div><div class="audit-hash">' + event.hash_full + '</div><div class="audit-meta">tamper-proof | immutable | verifiable</div></div>');
                                }}
                            }} else {{
                                addLine('<div class="block-result"><span class="status">SKIP (execution error)</span></div>');
                            }}
                        }} else if (event.type === 'blocked') {{
                            addLine('<div class="block-blocked"><span class="danger-icon">⛔</span><span class="label">BLOCKED</span><span class="name">' + event.block + '</span><span class="reason">' + (event.reason || 'Operation not in approved library - policy engine denied execution') + '</span></div>');
                        }} else if (event.type === 'complete') {{
                            await new Promise(r => setTimeout(r, 400));
                            addLine('<div class="summary-box"><div class="summary-title">Execution Complete</div><div class="summary-grid"><div class="summary-stat success-stat"><div class="value">' + event.executed + '</div><div class="label">Executed</div></div><div class="summary-stat error-stat"><div class="value">' + event.blocked + '</div><div class="label">Blocked</div></div><div class="summary-stat"><div class="value">' + event.executed + '</div><div class="label">Audit Hashes</div></div><div class="summary-stat"><div class="value">0</div><div class="label">Code Generated</div></div></div></div>');
                        }}
                    }}
                }}
            }} catch (err) {{
                addLine('<span class="blocked">Connection Error: ' + err.message + '</span>');
            }}
            
            liveBadge.style.display = 'none';
            btn.disabled = false;
            btn.textContent = 'Run Again';
            isRunning = false;
        }}
    </script>
</body>
</html>'''


def create_live_demo_html() -> str:
    """Generate the main live demo page."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neurop Forge | Live AI Demo</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>{PREMIUM_CSS}</style>
</head>
<body>
    <div class="bg-gradient"></div>
    
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
            <p class="tagline">AI as Operator, Not Author</p>
            <div class="company-badge">Enterprise AI Control Layer</div>
        </header>
        
        <section class="task-section">
            <h3>Task Assigned to AI</h3>
            <p class="task-text">
                Execute a series of <strong>verified block operations</strong>: mask sensitive emails, 
                calculate dates, and validate file types. The AI will also attempt a dangerous 
                data export operation which <strong>must be blocked</strong> by the policy engine.
            </p>
        </section>
        
        <div class="demo-card">
            <div class="demo-header">
                <span class="demo-title">Live Execution Terminal</span>
                <div class="live-badge" id="liveBadge">
                    <div class="live-dot"></div>
                    LIVE
                </div>
                <button class="run-btn" id="runBtn" onclick="runDemo()">Run Demo</button>
            </div>
            <div class="library-bar">
                <span>Neurop Forge Block Library</span>
                <span>4,552 verified functions</span>
                <span class="lib-status">LOADED</span>
                <a href="/library" target="_blank" class="browse-link">Browse Library</a>
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
            
            addLine('<span class="status">Initializing OpenAI GPT-4o-mini connection...</span>');
            
            try {{
                const response = await fetch('/api/demo-live/run', {{ method: 'POST' }});
                const data = await response.json();
                
                if (data.error) {{
                    addLine('<span class="blocked">Error: ' + data.error + '</span>');
                }} else {{
                    for (const event of data.events) {{
                        await new Promise(r => setTimeout(r, 600));
                        
                        if (event.type === 'status') {{
                            addLine('<span class="status">' + event.message + '</span>');
                        }} else if (event.type === 'block_call') {{
                            addLine('<div class="block-call"><span class="label">EXECUTE</span> <span class="name">' + event.block + '</span><div class="inputs">inputs: ' + JSON.stringify(event.inputs) + '</div></div>');
                        }} else if (event.type === 'block_result') {{
                            if (event.success) {{
                                addLine('<div class="block-result"><span class="ok">OK</span> <span class="value">' + JSON.stringify(event.result) + '</span></div>');
                                if (event.hash_full) {{
                                    addLine('<div class="audit-box"><div class="audit-header"><span class="audit-label">Cryptographic Audit</span><span class="audit-algo">SHA-256</span></div><div class="audit-hash">' + event.hash_full + '</div><div class="audit-meta">tamper-proof | immutable | verifiable</div></div>');
                                }}
                            }} else {{
                                addLine('<div class="block-result"><span class="status">SKIP (execution error)</span></div>');
                            }}
                        }} else if (event.type === 'blocked') {{
                            addLine('<div class="block-blocked"><span class="danger-icon">⛔</span><span class="label">BLOCKED</span><span class="name">' + event.block + '</span><span class="reason">' + (event.reason || 'Operation not in approved library - policy engine denied execution') + '</span></div>');
                        }} else if (event.type === 'complete') {{
                            await new Promise(r => setTimeout(r, 400));
                            addLine('<div class="summary-box"><div class="summary-title">Execution Complete</div><div class="summary-grid"><div class="summary-stat success-stat"><div class="value">' + event.executed + '</div><div class="label">Executed</div></div><div class="summary-stat error-stat"><div class="value">' + event.blocked + '</div><div class="label">Blocked</div></div><div class="summary-stat"><div class="value">' + event.executed + '</div><div class="label">Audit Hashes</div></div><div class="summary-stat"><div class="value">0</div><div class="label">Code Generated</div></div></div></div>');
                        }}
                    }}
                }}
            }} catch (err) {{
                addLine('<span class="blocked">Connection Error: ' + err.message + '</span>');
            }}
            
            liveBadge.style.display = 'none';
            btn.disabled = false;
            btn.textContent = 'Run Again';
            isRunning = false;
        }}
    </script>
</body>
</html>'''


# Generate the HTML templates
PREMIUM_LIVE_DEMO_HTML = create_live_demo_html()
PREMIUM_MICROSOFT_DEMO_HTML = create_microsoft_demo_html()
PREMIUM_GOOGLE_DEMO_HTML = create_google_demo_html()

# Library Browser Template
LIBRARY_BROWSER_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Block Library - Neurop Forge</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        ''' + PREMIUM_CSS + '''
        
        .library-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        
        .library-title {
            font-size: 1.5rem;
            font-weight: 700;
        }
        
        .library-count {
            color: var(--accent);
            font-size: 0.9rem;
        }
        
        .search-box {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px 16px;
            width: 100%;
            color: var(--text-primary);
            font-size: 0.9rem;
            margin-bottom: 20px;
        }
        
        .search-box:focus {
            outline: none;
            border-color: var(--accent);
        }
        
        .category-tabs {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }
        
        .category-tab {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 6px 14px;
            color: var(--text-secondary);
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .category-tab:hover, .category-tab.active {
            background: rgba(0, 212, 255, 0.1);
            border-color: var(--accent);
            color: var(--accent);
        }
        
        .block-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }
        
        .block-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .block-card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
        }
        
        .block-name {
            color: var(--accent);
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 6px;
        }
        
        .block-category {
            color: var(--text-muted);
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        
        .block-desc {
            color: var(--text-secondary);
            font-size: 0.8rem;
            line-height: 1.5;
        }
        
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal-overlay.active {
            display: flex;
        }
        
        .modal-content {
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 16px;
            width: 90%;
            max-width: 700px;
            max-height: 85vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 24px;
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            background: var(--bg-primary);
        }
        
        .modal-title {
            color: var(--accent);
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        .modal-close {
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 1.5rem;
            cursor: pointer;
        }
        
        .modal-close:hover {
            color: var(--text-primary);
        }
        
        .modal-body {
            padding: 24px;
        }
        
        .readonly-badge {
            background: rgba(239, 68, 68, 0.15);
            color: var(--error);
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .detail-section {
            margin-bottom: 20px;
        }
        
        .detail-label {
            color: var(--text-muted);
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
        }
        
        .detail-value {
            color: var(--text-primary);
            font-size: 0.85rem;
            line-height: 1.6;
        }
        
        .code-block {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            line-height: 1.6;
            overflow-x: auto;
            color: var(--text-secondary);
        }
        
        .hash-display {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            color: var(--success);
            background: rgba(34, 197, 94, 0.1);
            padding: 8px 12px;
            border-radius: 6px;
            word-break: break-all;
        }
        
        .input-list, .output-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .param-tag {
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 4px 10px;
            font-size: 0.75rem;
            color: var(--accent);
        }
        
        .loading {
            text-align: center;
            padding: 60px;
            color: var(--text-muted);
        }
        
        .empty-state {
            text-align: center;
            padding: 60px;
            color: var(--text-muted);
        }
    </style>
</head>
<body>
    <div class="bg-gradient"></div>
    <div class="container">
        <header>
            <div class="logo-wrapper">
                <div class="logo-text">
                    <span>Neurop</span> <span>Forge</span>
                </div>
            </div>
            <p class="tagline">Block Library Browser</p>
        </header>
        
        <div class="library-header">
            <div>
                <div class="library-title">Verified Function Blocks</div>
                <div class="library-count"><span id="blockCount">Loading...</span> blocks available</div>
            </div>
            <span class="readonly-badge">Read Only</span>
        </div>
        
        <input type="text" class="search-box" id="searchInput" placeholder="Search blocks by name or description...">
        
        <div class="category-tabs" id="categoryTabs">
            <button class="category-tab active" data-category="all">All</button>
        </div>
        
        <div class="block-grid" id="blockGrid">
            <div class="loading">Loading blocks...</div>
        </div>
    </div>
    
    <div class="modal-overlay" id="blockModal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title" id="modalTitle">Block Details</div>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body" id="modalBody">
            </div>
        </div>
    </div>
    
    <script>
        let allBlocks = [];
        let currentCategory = 'all';
        
        async function loadBlocks() {
            try {
                const response = await fetch('/api/library/blocks');
                const data = await response.json();
                allBlocks = data.blocks || [];
                document.getElementById('blockCount').textContent = allBlocks.length;
                
                const categories = [...new Set(allBlocks.map(b => b.category))].sort();
                const tabsContainer = document.getElementById('categoryTabs');
                tabsContainer.innerHTML = '<button class="category-tab active" data-category="all">All</button>';
                categories.forEach(cat => {
                    const btn = document.createElement('button');
                    btn.className = 'category-tab';
                    btn.dataset.category = cat;
                    btn.textContent = cat;
                    btn.onclick = () => filterByCategory(cat);
                    tabsContainer.appendChild(btn);
                });
                
                renderBlocks(allBlocks);
            } catch (err) {
                document.getElementById('blockGrid').innerHTML = '<div class="empty-state">Failed to load blocks</div>';
            }
        }
        
        function renderBlocks(blocks) {
            const grid = document.getElementById('blockGrid');
            if (blocks.length === 0) {
                grid.innerHTML = '<div class="empty-state">No blocks found</div>';
                return;
            }
            grid.innerHTML = blocks.map(block => `
                <div class="block-card" onclick="showBlockDetail('${block.name}')">
                    <div class="block-name">${block.name}</div>
                    <div class="block-category">${block.category || 'general'}</div>
                    <div class="block-desc">${block.description || 'Verified immutable function block'}</div>
                </div>
            `).join('');
        }
        
        function filterByCategory(category) {
            currentCategory = category;
            document.querySelectorAll('.category-tab').forEach(tab => {
                tab.classList.toggle('active', tab.dataset.category === category);
            });
            const filtered = category === 'all' ? allBlocks : allBlocks.filter(b => b.category === category);
            renderBlocks(filtered);
        }
        
        document.getElementById('searchInput').addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            let filtered = allBlocks;
            if (currentCategory !== 'all') {
                filtered = filtered.filter(b => b.category === currentCategory);
            }
            if (query) {
                filtered = filtered.filter(b => 
                    b.name.toLowerCase().includes(query) || 
                    (b.description && b.description.toLowerCase().includes(query))
                );
            }
            renderBlocks(filtered);
        });
        
        async function showBlockDetail(blockName) {
            document.getElementById('modalTitle').textContent = blockName;
            document.getElementById('modalBody').innerHTML = '<div class="loading">Loading block details...</div>';
            document.getElementById('blockModal').classList.add('active');
            
            try {
                const response = await fetch('/api/library/block/' + encodeURIComponent(blockName));
                const data = await response.json();
                const block = data.block;
                
                let inputsHtml = '';
                if (block.inputs && block.inputs.length > 0) {
                    inputsHtml = block.inputs.map(inp => `<span class="param-tag">${inp.name}: ${inp.type}</span>`).join('');
                } else {
                    inputsHtml = '<span class="param-tag">none</span>';
                }
                
                let outputsHtml = '';
                if (block.outputs && block.outputs.length > 0) {
                    outputsHtml = block.outputs.map(out => `<span class="param-tag">${out.name}: ${out.type}</span>`).join('');
                } else {
                    outputsHtml = '<span class="param-tag">result</span>';
                }
                
                document.getElementById('modalBody').innerHTML = `
                    <div class="detail-section">
                        <div class="detail-label">Description</div>
                        <div class="detail-value">${block.description || 'Verified immutable function block'}</div>
                    </div>
                    
                    <div class="detail-section">
                        <div class="detail-label">Category</div>
                        <div class="detail-value">${block.category || 'general'}</div>
                    </div>
                    
                    <div class="detail-section">
                        <div class="detail-label">Inputs</div>
                        <div class="input-list">${inputsHtml}</div>
                    </div>
                    
                    <div class="detail-section">
                        <div class="detail-label">Outputs</div>
                        <div class="output-list">${outputsHtml}</div>
                    </div>
                    
                    <div class="detail-section">
                        <div class="detail-label">Cryptographic Identity (SHA-256)</div>
                        <div class="hash-display">${block.hash || 'Hash not available'}</div>
                    </div>
                    
                    <div class="detail-section">
                        <div class="detail-label">Implementation (Read Only)</div>
                        <pre class="code-block">${escapeHtml(block.code || 'Implementation details protected')}</pre>
                    </div>
                    
                    <div class="detail-section">
                        <div class="detail-label">Constraints</div>
                        <div class="detail-value">
                            Purity: ${block.purity || 'pure'} | 
                            Deterministic: ${block.deterministic !== false ? 'yes' : 'no'} | 
                            Thread Safe: ${block.thread_safe !== false ? 'yes' : 'no'}
                        </div>
                    </div>
                `;
            } catch (err) {
                document.getElementById('modalBody').innerHTML = '<div class="empty-state">Failed to load block details</div>';
            }
        }
        
        function closeModal() {
            document.getElementById('blockModal').classList.remove('active');
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        document.getElementById('blockModal').addEventListener('click', (e) => {
            if (e.target.id === 'blockModal') closeModal();
        });
        
        loadBlocks();
    </script>
</body>
</html>'''
