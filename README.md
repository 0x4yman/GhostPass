# 👻 GhostPass
 
> A Burp Suite extension that tests for authentication bypass vulnerabilities by automatically detecting and stripping authentication headers from HTTP requests.
 
 
---
 
## 📖 What is GhostPass?
 
During a web penetration test, a common vulnerability is when a protected endpoint remains accessible even without authentication headers. For example, an endpoint like:
 
```
GET /profile?user=5 HTTP/1.1
Host: target.com
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Cookie: session=abc123
```
 
...might still return sensitive data if you simply remove the `Authorization` and `Cookie` headers. This is an **authentication bypass** vulnerability.
 
**GhostPass** automates this test. Instead of manually going into Repeater and deleting headers one by one, you right-click any request → Send to GhostPass → select the headers to strip → click Send. Done.
 
---
 
## ✨ Features
 
- **Auto-detection** — Automatically detects 15+ known authentication headers in any request
- **One-click stripping** — Pre-selects all detected auth headers for removal
- **Custom header input** — Optionally specify any non-standard session header to also strip
- **Editable request** — Tweak the request manually before sending
- **Side-by-side view** — Request and response displayed side by side like Repeater
- **Threaded requests** — UI stays responsive while the request is being sent
- **Context menu integration** — Right-click any request anywhere in Burp Suite
---
 
## 🔍 Detected Authentication Headers
 
GhostPass automatically detects and flags the following headers:
 
| Header | Header |
|---|---|
| `Authorization` | `X-Auth-Token` |
| `Cookie` | `X-Access-Token` |
| `X-API-Key` | `X-Session-Token` |
| `X-CSRF-Token` | `Token` |
| `Bearer` | `X-JWT-Token` |
| `X-User-Token` | `Session` |
| `API-Key` | `X-Forwarded-User` |
| `X-Remote-User` | |
 
---
 
## 🚀 Installation
 
### Prerequisites
 
| Requirement | Details |
|---|---|
| Burp Suite | Community or Professional edition |
| Jython Standalone JAR | Version 2.7.x — [Download here](https://www.jython.org/download) |
 
### Step 1 — Configure Jython in Burp Suite
 
1. Open Burp Suite
2. Go to **Extensions** → **Extensions settings**
3. Under **Python environment**, click **Select file**
4. Point to your `jython-standalone-2.7.x.jar` file
### Step 2 — Download GhostPass
 
```bash
git clone https://github.com/YOURUSERNAME/GhostPass.git
```
 
Or download the ZIP from the releases page and extract it.
 
### Step 3 — Load the Extension
 
1. In Burp Suite, go to **Extensions** → **Add**
2. Set **Extension type** to `Python`
3. Click **Select file** and choose `ghostpass.py`
4. Click **Next**
You should see `GhostPass loaded!` in the output panel and a new **GhostPass** tab in Burp Suite.
 
---
 
## 🛠️ Usage
 
### Basic Workflow
 
```
1. Browse your target through Burp proxy as normal
 
2. Find a request you want to test in:
   → Proxy → HTTP history
   → Repeater
   → Target → Site map
   → Anywhere in Burp Suite
 
3. Right-click the request → "Send to GhostPass"
 
4. Go to the "GhostPass" tab
 
5. Review the auto-detected auth headers (all pre-selected)
 
6. Optionally:
   → Deselect headers you want to KEEP
   → Type a custom header name and click Add
 
7. Click the red "Send" button
 
8. Analyze the response
```
 
 
### Optional — Custom Header
 
If the application uses a non-standard header for session management (e.g. `X-Session-ID`, `X-Tenant-Token`), you can type the header name in the **"Optional: manually specify a header name to also strip"** field and click **Add**. GhostPass will find it in the request and add it to the strip list.
 
---
 
## 📁 Project Structure
 
```
GhostPass/
├── ghostpass.py        # Entry point — load this file into Burp Suite
├── ui_panel.py         # Visual tab UI (Swing-based)
├── http_handler.py     # Request stripping and sending logic
├── README.md           # You are here
└── LICENSE             # MIT License
```
 
---
 
 
## 💡 Planned Features
 
- [ ] Response diff view (original vs bypass side by side)
- [ ] History log table of all bypass attempts
- [ ] Automatic bypass verdict engine
- [ ] Export results to HTML/CSV report
- [ ] Token manipulation (empty, malformed, null tokens)
---

 
*GhostPass — because sometimes the best way in is to look like you were never there.*
