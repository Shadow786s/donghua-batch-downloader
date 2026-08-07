from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Donghua Batch Downloader")


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>Donghua Batch Downloader</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
            }

            textarea {
                width: 100%;
                min-height: 220px;
                padding: 12px;
                box-sizing: border-box;
            }

            select, button {
                padding: 10px 14px;
                margin-top: 12px;
            }

            button {
                cursor: pointer;
            }

            .box {
                border: 1px solid #ddd;
                border-radius: 12px;
                padding: 20px;
                margin-top: 20px;
            }
        </style>
    </head>

    <body>

        <h1>Donghua Batch Downloader</h1>

        <p>
            Authorized episode-page links को नीचे एक-एक line में डालें।
        </p>

        <textarea
            id="urls"
            placeholder="https://example.com/episode-1
https://example.com/episode-2
https://example.com/episode-3"
        ></textarea>

        <div class="box">

            <label for="batch">
                <strong>Batch size:</strong>
            </label>

            <select id="batch">
                <option value="5">5 Episodes</option>
                <option value="10">10 Episodes</option>
                <option value="20">20 Episodes</option>
            </select>

            <br>

            <button onclick="prepareBatch()">
                Prepare Batch
            </button>

        </div>

        <div class="box">
            <strong>Status:</strong>
            <p id="status">Ready</p>
        </div>

        <script>
            function prepareBatch() {

                const text = document.getElementById("urls").value;

                const urls = text
                    .split("\\n")
                    .map(url => url.trim())
                    .filter(url => url.length > 0);

                const batchSize =
                    Number(document.getElementById("batch").value);

                if (urls.length === 0) {
                    document.getElementById("status").innerText =
                        "Please enter at least one episode URL.";

                    return;
                }

                document.getElementById("status").innerText =
                    "Found " + urls.length +
                    " episode link(s). Batch size: " +
                    batchSize +
                    ". Processing system is ready.";
            }
        </script>

    </body>
    </html>
    """


@app.get("/health")
def health():
    return {"status": "ok"}
