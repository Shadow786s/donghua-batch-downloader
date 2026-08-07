from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl

app = FastAPI(title="Donghua Batch Downloader")


class BatchRequest(BaseModel):
    urls: list[HttpUrl]
    batch_size: int = 5


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

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

            select,
            button {
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

            #result {
                white-space: pre-wrap;
            }
        </style>
    </head>

    <body>

        <h1>Donghua Batch Downloader</h1>

        <p>
            Authorized episode-page links को एक-एक line में डालें।
        </p>

        <textarea
            id="urls"
            placeholder="One episode URL per line"></textarea>

        <br>

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

        <div class="box">
            <strong>Result:</strong>
            <p id="result">Ready</p>
        </div>

        <script>
            async function prepareBatch() {

                const text =
                    document.getElementById("urls").value;

                const urls = text
                    .split("\\n")
                    .map(url => url.trim())
                    .filter(url => url.length > 0);

                const batchSize =
                    Number(
                        document.getElementById("batch").value
                    );

                if (urls.length === 0) {
                    document.getElementById("result").innerText =
                        "Please enter at least one URL.";

                    return;
                }

                try {

                    const response = await fetch("/prepare-batch", {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            urls: urls,
                            batch_size: batchSize
                        })
                    });

                    const data = await response.json();

                    document.getElementById("result").innerText =
                        JSON.stringify(data, null, 2);

                } catch (error) {

                    document.getElementById("result").innerText =
                        "Error: " + error;
                }
            }
        </script>

    </body>
    </html>
    """


@app.post("/prepare-batch")
def prepare_batch(request: BatchRequest):

    if request.batch_size not in [5, 10, 20]:
        return {
            "error": "Batch size must be 5, 10, or 20."
        }

    batches = []

    for index in range(
        0,
        len(request.urls),
        request.batch_size
    ):
        batch = request.urls[
            index:index + request.batch_size
        ]

        batches.append({
            "batch_number": len(batches) + 1,
            "episode_count": len(batch),
            "urls": [str(url) for url in batch]
        })

    return {
        "status": "ready",
        "total_episodes": len(request.urls),
        "batch_size": request.batch_size,
        "batches": batches
    }

@app.get("/check-page")
async def check_page(url: str):

    import httpx

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=15
        ) as client:

            response = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

        return {
            "status": "ok",
            "http_status": response.status_code,
            "final_url": str(response.url),
            "content_type": response.headers.get(
                "content-type"
            )
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }

@app.get("/health")
def health():
    return {"status": "ok"}
