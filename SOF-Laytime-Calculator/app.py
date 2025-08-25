from flask import Flask, render_template, request, send_file, jsonify
from io import StringIO, BytesIO
import csv, json, os
from extractor import extract_events, extract_text_from_pdf, extract_text_from_docx

app = Flask(__name__)   # ✅ use __name_

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/extract", methods=["POST"])
def extract():
    text = ""
    uploaded = request.files.get("sof_file")   # ✅ matches HTML

    if uploaded and uploaded.filename:
        filename = uploaded.filename.lower()

        # Save file temporarily
        temp_path = os.path.join("uploads", uploaded.filename)
        os.makedirs("uploads", exist_ok=True)
        uploaded.save(temp_path)

        # Check file type
        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(temp_path)
        elif filename.endswith(".docx"):
            text = extract_text_from_docx(temp_path)
        else:
            return "❌ Only PDF or DOCX files are allowed", 400

    # ✅ Debug: show extracted text in terminal
    print("DEBUG Extracted text:\n", text[:1000])

    rows = extract_events(text or "")
    return render_template(
        "result.html",
        rows=rows,
        raw_json=json.dumps(rows, indent=2),
        raw_text=text or ""
    )

@app.route("/download/csv", methods=["POST"])
def download_csv():
    data = request.form.get("data", "[]")
    rows = json.loads(data)

    si = StringIO()
    writer = csv.DictWriter(si, fieldnames=["event", "start", "end"])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    mem = BytesIO(si.getvalue().encode("utf-8"))
    mem.seek(0)
    return send_file(mem,
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name="sof_events.csv")

@app.route("/download/json", methods=["POST"])
def download_json():
    data = request.form.get("data", "[]")
    mem = BytesIO(data.encode("utf-8"))
    mem.seek(0)
    return send_file(mem,
                     mimetype="application/json",
                     as_attachment=True,
                     download_name="sof_events.json")

@app.route("/api/extract", methods=["POST"])
def api_extract():
    payload = request.get_json(force=True, silent=True) or {}
    text = payload.get("text", "")
    return jsonify(extract_events(text))

if __name__ == "__main__":
    app.run(debug=True)
    