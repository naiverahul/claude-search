from flask import Flask, send_from_directory, jsonify, request
import os
from mcp_integration import handle_claude_tool_call

app = Flask(__name__, static_folder="static")

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/tool_call", methods=["POST"])
def tool_call():
    if not request.json:
        return jsonify({"error": "Invalid request"}), 400

    tool_name = request.json.get("name")
    parameters = request.json.get("parameters", {})

    if tool_name != "fetch_web_content":
        return jsonify({"error": "Unknown tool name"}), 400

    try:
        result = handle_claude_tool_call(parameters)
        return jsonify(result)
    except Exception as e:
        error_msg = str(e)
        if "insufficient_quota" in error_msg or "credits" in error_msg.lower():
            return jsonify({"error": "Your Claude API quota or credits may be exhausted."}), 402
        return jsonify({"error": error_msg}), 500

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
