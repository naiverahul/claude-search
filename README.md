# Claude-Powered Web Search Interface
![image](https://github.com/user-attachments/assets/dea89626-2965-4287-9562-06047f196347)

A minimal and scalable AI-powered search engine built using Claude's API and DuckDuckGo, integrated with both a web interface and a CLI tool.

---

## 📦 Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/claude-search.git
   cd claude-search
   ```

2. **Create a Virtual Environment (optional but recommended)**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**:

   ```bash
   set CLAUDE_API_KEY=your_claude_api_key 
   # In powershell
   $env:CLAUDE_API_KEY=your_key
   ```

---

## 🛠 How It Works

This project includes two main interfaces:

### 1. 📟 CLI Interface (`ask_claude.py`)

* Sends queries to Claude.
* Claude detects tool-use (e.g., web search), and calls the `MCP server` to fetch DuckDuckGo results.
* Claude summarizes the results and replies.

**Run:**

```bash
# Start MCP Server
python mcp_server.py
# On another terminal run 
python ask_claude.py "What is the latest on AI governance?"
```

### 2. 🌐 Web Interface (`app.py`)

* Simple HTML UI for user-friendly searches.
* Sends a query to your MCP server (`/tool_call`) which fetches relevant results.
* Displays them in a clean, TailwindCSS-powered interface.

**Run:**

```bash
python app.py
```

Then visit: [http://localhost:5001](http://localhost:5001)

---

## ⚙️ MCP Server (`mcp_server.py`)

The MCP (Modular Command Processing) server:

* Routes tool calls from Claude to actual data providers like DuckDuckGo.
* Responds with results which are then used by Claude or your app.

**Endpoints:**

* `/health`: Check if the MCP server is running.
* `/tool_call`: Accepts tool call requests with a query and returns relevant search results.


---

## 🚫 Why It Might Not Work Now

While the app and CLI are configured correctly and successfully connect to:

* ✅ Claude's API endpoint
* ✅ MCP server running locally

You may still receive error messages like:

```
"Your Claude API quota or credits may be exhausted."
```
![image](https://github.com/user-attachments/assets/7a86ea4e-afa7-47ee-baf4-251332e6552a)


This is because Claude is rejecting requests due to exhausted API usage quota. The backend is still functional and integrated correctly.

---

## 📁 Project Structure

```
.
├── app.py              # Flask server for the website
├── ask_claude.py       # CLI interface
├── claude_mcp_client.py
├── mcp_server.py       # Handles Claude tool calls
├── mcp_integration.py  # Bridge to DuckDuckGo & Claude logic
├── static/
│   └── index.html      # Frontend UI
├── requirements.txt
└── README.md           # You're here!
```

---

## 📌 To Do

* Add Claude response summarization to UI.
* Enable query history per session.
* Add fallback to local GPT models when Claude is down.

---

## 🧠 Credits

Developed with love and frustration by \Rahul Agarwal. Uses Anthropic Claude API + DuckDuckGo search.
