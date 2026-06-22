from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <div style="text-align: center; margin-top: 10%; font-family: sans-serif;">
        <h1>🦷 Pergigian Kelantan Web App</h1>
        <p>Sistem dalam proses pembangunan. Pautan sedia untuk diuji!</p>
        <p style="color: gray; font-size: 0.8em;">Powered by Python & Render</p>
    </div>
    """

if __name__ == '__main__':
    app.run(debug=True)
