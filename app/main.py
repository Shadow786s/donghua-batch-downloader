from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl
import re

app = FastAPI(title="Donghua Batch Downloader")


class BatchRequest(BaseModel):
    urls: list[HttpUrl]
    batch_size: int = 5
    quality: str = "highest"
    

def clean_urls(urls):
    seen = set()
    cleaned = []

    for url in urls:
        url = str(url).strip()

        if not url:
            continue

        if url not in seen:
            seen.add(url)
            cleaned.append(url)

    return cleaned


def detect_episode_number(url):
    patterns = [
        r"episode[-_ ]?(\d+)",
        r"ep[-_ ]?(\d+)",
        r"/(\d+)(?:/)?$"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            url,
            re.IGNORECASE
        )

        if match:
            return int(match.group(1))

    return None


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
                margin: 30px auto;
                padding: 20px;
                background: #f7f7f7;
            }

            h1 {
                margin-bottom: 8px;
            }

            textarea {
                width: 100%;
                min-height: 220px;
                padding: 14px;
                box-sizing: border-box;
                border: 1px solid #ccc;
                border-radius: 10px;
                font-size: 15px;
            }

            select,
            button {
                padding: 11px 16px;
                margin-top: 12px;
                border-radius: 8px;
                border: 1px solid #bbb;
            }

            button {
                cursor: pointer;
                font-weight: bold;
            }

            .box {
                background: white;
                border: 1px solid #ddd;
                border-radius: 12px;
                padding: 20px;
                margin-top: 20px;
            }

            .batch {
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 14px;
                margin-top: 12px;
                background: #fafafa;
            }

            .batch-title {
                font-weight: bold;
                margin-bottom: 8px;
            }

            .ready {
                font-weight: bold;
            }

            .episode {
                margin-top: 5px;
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
            placeholder="Episode 1 URL
Episode 2 URL
Episode 3 URL
Episode 4 URL
Episode 5 URL"></textarea>

        <div class="box">

            <label for="batch">
                <strong>Batch size:</strong>
            </label>

            <select id="batch">
                <option value="5">5 Episodes</option>
                <option value="10">10 Episodes</option>
                <option value="20">20 Episodes</option>
            </select>

            <br><br>

            <label for="quality">
                <strong>Video quality:</strong>
            </label>

            <select id="quality">
                <option value="highest">Highest Available</option>
                <option value="1080">1080p</option>
                <option value="720">720p</option>
                <option value="480">480p</option>
            </select>

            <br>

            <button onclick="prepareBatch()">
                Create Batch Queue
            </button>

        </div>

        <div class="box">

            <strong>Status</strong>

            <p id="status">
                Ready
            </p>

        </div>

        <div class="box">

            <strong>Batch Queue</strong>

            <div id="batches">
                No batches created yet.
            </div>

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

                const quality =
                    document.getElementById("quality").value;

                const status =
                    document.getElementById("status");

                const batchesBox =
                    document.getElementById("batches");

                if (urls.length === 0) {

                    status.innerText =
                        "Please enter at least one URL.";

                    batchesBox.innerHTML = "";

                    return;
                }

                status.innerText =
                    "Creating batch queue...";

                try {

                    const response = await fetch(
                        "/prepare-batch",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                urls: urls,
                                batch_size: batchSize,
                                quality: quality
                            })
                        }
                    );

                    const data =
                        await response.json();

                    if (!response.ok) {

                        status.innerText =
                            data.detail ||
                            "Something went wrong.";

                        return;
                    }

                    status.innerText =
                        "Queue ready: " +
                        data.total_episodes +
                        " unique episode(s).";

                    batchesBox.innerHTML = "";

                    data.batches.forEach(function(batch) {

                        const div =
                            document.createElement("div");

                        div.className = "batch";

                        let episodeText = "";

                        batch.episodes.forEach(
                            function(episode) {

                                let number;

                                if (
                                    episode.episode_number !== null
                                ) {
                                    number =
                                        "Episode " +
                                        episode.episode_number;
                                } else {
                                    number =
                                        "Episode number not detected";
                                }

                                episodeText +=
                                    "<div class='episode'>" +
                                    number +
                                    "</div>";
                            }
                        );

                        div.innerHTML =
                            "<div class='batch-title'>" +
                            "Batch " +
                            batch.batch_number +
                            " — " +
                            batch.episode_count +
                            " episode(s)" +
                            "</div>" +

                            "<div class='ready'>" +
                            "Status: Ready" +
                            "</div>" +

                            episodeText;

                        batchesBox.appendChild(div);

                    });

                } catch (error) {

                    status.innerText =
                        "Connection error: " +
                        error;
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
            "detail":
                "Batch size must be 5, 10, or 20."
        }

    allowed_qualities = [
        "highest",
        "1080",
        "720",
        "480"
    ]

    if request.quality not in allowed_qualities:
        return {
            "detail":
                "Invalid quality selection."
        }

    cleaned_urls = clean_urls(request.urls)

    batches = []

    for index in range(
        0,
        len(cleaned_urls),
        request.batch_size
    ):

        batch_urls = cleaned_urls[
             index:index + request.batch_size
        ]

        episode_items = []

        for url in batch_urls:

            episode_number = detect_episode_number(url)

            episode_items.append({
                "url": url,
                "episode_number": episode_number
            })

        batches.append({
            "batch_number":
                len(batches) + 1,

            "episode_count":
                len(batch_urls),

            "episodes":
                episode_items
        })

    return {
        "status": "ready",
        "total_episodes":
            len(cleaned_urls),
        "batch_size":
            request.batch_size,
        "quality":
            request.quality,
        "batches":
            batches
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
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
            "content_type":
                response.headers.get(
                    "content-type"
                )
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }
