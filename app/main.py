from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Donghua Batch Downloader")


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Donghua Batch Downloader</title>
    </head>
    <body>
        <h1>Donghua Batch Downloader</h1>

        <p>Authorized episode-page links यहाँ डालें:</p>

        <textarea
            rows="10"
            cols="60"
            placeholder="One episode URL per line"
        ></textarea>

        <br><br>

        <label>Batch size:</label>

        <select>
            <option value="5">5 episodes</option>
            <option value="10">10 episodes</option>
            <option value="20">20 episodes</option>
        </select>

        <br><br>

        <button>Start Batch</button>

        <p>Status: Ready</p>
    </body>
    </html>
    """


@app.get("/health")
def health():
    return {"status": "ok"}
