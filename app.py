from flask import Flask, render_template, request, send_file
import joblib
import numpy as np
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from pymongo import MongoClient

app = Flask(**name**)

# ------------------- MongoDB -------------------

MONGO_URI = "mongodb+srv://indu77:gill7777@cluster0.lvfhnbs.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["hydroponics_db"]
collection = db["predictions"]

# ------------------- Model -------------------

MODEL_PATH = os.path.join(os.path.dirname(**file**), 'model.pkl')
model = joblib.load(MODEL_PATH)

last_result = {}

@app.route('/')
def home():
return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
global last_result

```
plant = request.form.get('plant', 'Unknown')

try:
    temp = float(request.form.get('temperature', 25))
    ph = float(request.form.get('ph', 6.2))
    ec = float(request.form.get('ec', 1.8))
    humidity = float(request.form.get('humidity', 65))
except ValueError:
    return "Invalid input"

X = np.array([[temp, ph, ec, humidity]])
pred = model.predict(X)[0]

pred_temp = float(pred[0])
pred_ph = float(pred[1])
pred_ec = float(pred[2])

suggestions = []

if pred_temp - temp > 0.5:
    suggestions.append(f"Increase temperature by {pred_temp - temp:.1f} °C")
elif temp - pred_temp > 0.5:
    suggestions.append(f"Decrease temperature by {temp - pred_temp:.1f} °C")

if pred_ph - ph > 0.2:
    suggestions.append(f"Increase pH by {pred_ph - ph:.2f}")
elif ph - pred_ph > 0.2:
    suggestions.append(f"Decrease pH by {ph - pred_ph:.2f}")

if pred_ec - ec > 0.2:
    suggestions.append(f"Increase EC by {pred_ec - ec:.2f}")
elif ec - pred_ec > 0.2:
    suggestions.append(f"Decrease EC by {ec - pred_ec:.2f}")

last_result = {
    "plant": plant,
    "temperature": temp,
    "ph": ph,
    "ec": ec,
    "humidity": humidity,
    "predicted_temperature": round(pred_temp, 2),
    "predicted_ph": round(pred_ph, 2),
    "predicted_ec": round(pred_ec, 2),
    "suggestions": suggestions
}

collection.insert_one(last_result)

return render_template('result.html', **last_result)
```

@app.route('/download_report')
def download_report():
global last_result

```
if not last_result:
    return "No data"

filename = f"{last_result['plant']}_report.pdf"
filepath = os.path.join(os.getcwd(), filename)

doc = SimpleDocTemplate(filepath, pagesize=A4)
styles = getSampleStyleSheet()
content = []

logo_path = os.path.join(app.static_folder, "images/logo.png")
if os.path.exists(logo_path):
    content.append(Image(logo_path, width=1.2*inch, height=1.2*inch))
    content.append(Spacer(1, 12))

content.append(Paragraph(f"<b>Hydroponics Report - {last_result['plant']}</b>", styles['Title']))
content.append(Spacer(1, 20))

details = f"""
Temperature: {last_result['temperature']} °C<br/>
pH: {last_result['ph']}<br/>
EC: {last_result['ec']}<br/>
Humidity: {last_result['humidity']} %<br/><br/>

Predicted Temperature: {last_result['predicted_temperature']} °C<br/>
Predicted pH: {last_result['predicted_ph']}<br/>
Predicted EC: {last_result['predicted_ec']}<br/>
"""

content.append(Paragraph(details, styles['Normal']))

for s in last_result["suggestions"]:
    content.append(Paragraph(f"- {s}", styles['Normal']))

doc.build(content)

return send_file(filepath, as_attachment=True)
```

if app = Flask(__name__):
app.run(host='0.0.0.0', port=5000)
