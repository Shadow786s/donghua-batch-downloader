from fastapi import FastAPI
import io
import zipfile
import subprocess
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl
import re

app = FastAPI(title="Donghua Batch Downloader")


class BatchRequest(BaseModel):
    urls: list[HttpUrl]
    batch_size: int = 5
    quality: str = "highest"
    source_quality: str = "highest"
    

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

            <strong>Source Information</strong>

            <p>
                अगर आपके पास किसी authorized/downloadable source
                की information है, तो यहाँ दर्ज करें।
            </p>

            <label for="source-quality">
                Quality:
            </label>

            <select id="source-quality">
                <option value="highest">Highest Available</option>
                <option value="1080">1080p</option>
                <option value="720">720p</option>
                <option value="480">480p</option>
            </select>

        </div>

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

                const sourceQuality =
                    document.getElementById("source-quality").value;

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
                                quality: quality,
                                source_quality: sourceQuality
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

                        const downloadLink =
                             "/test-batch-merge/" +
                             batch.batch_number +
                             "?batch_size=" +
                             batch.episode_count;

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

                            episodeText +

                            "<br>" +

                            "<a href='" +
                            downloadLink +
                            "' " +
                            "download " +
                            "style='display:inline-block;" +
                            "padding:10px 16px;" +
                            "background:#222;" +
                            "color:white;" +
                            "text-decoration:none;" +
                            "border-radius:8px;'>" +
                            "Merge & Download MP4" +
                            "</a>";

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

    if request.source_quality not in allowed_qualities:
        return {
            "detail":
                "Invalid source quality selection."
        }

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
        "source_quality":
            request.source_quality,
        "batches":
            batches
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }

@app.get("/test-quality")
def test_quality():

    from models import (
        EpisodeSource,
        QualityOption
    )

    source = EpisodeSource(
        episode_number=281,
        page_url="https://example.com/episode-281",
        qualities=[
            QualityOption(
                label="480p",
                height=480,
                url="https://example.com/video-480"
            ),
            QualityOption(
                label="720p",
                height=720,
                url="https://example.com/video-720"
            ),
            QualityOption(
                label="1080p",
                height=1080,
                url="https://example.com/video-1080"
            )
        ]
    )

    selected = source.highest_quality()

    return {
        "episode": source.episode_number,
        "selected_quality": selected.label,
        "height": selected.height
    }

@app.get("/check-page")
async def check_page(url: str):

    import httpx

    try:

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        ) as client:

            response = await client.get(url)

        content_type = (
            response.headers.get("content-type")
            or ""
        )

        content_length = (
            response.headers.get("content-length")
        )

        return {
            "status": "ok",
            "http_status": response.status_code,
            "requested_url": url,
            "final_url": str(response.url),
            "content_type": content_type,
            "content_length": content_length,
            "is_video":
                content_type.lower().startswith(
                    "video/"
                )
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }

@app.get("/test-batch-download")
def test_batch_download():

    episodes = [
        "Episode 281",
        "Episode 282",
        "Episode 283",
        "Episode 284",
        "Episode 285"
    ]

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:

        for episode in episodes:

            content = (
                f"TEST FILE\n"
                f"{episode}\n"
                f"Quality: 1080p\n"
                f"This is only a batch-system test.\n"
            )

            filename = (
                episode.replace(" ", "_")
                + "_1080p.txt"
            )

            zip_file.writestr(
                filename,
                content
            )

    zip_buffer.seek(0)

    from fastapi.responses import StreamingResponse

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition":
                "attachment; "
                "filename=donghua_test_batch.zip"
        }
    )

@app.get("/test-batch/{batch_number}")
def test_batch(batch_number: int):

    import io
    import zipfile
    from fastapi.responses import StreamingResponse

    if batch_number < 1:
        return {
            "detail": "Invalid batch number."
        }

    start_episode = ((batch_number - 1) * 5) + 281

    episodes = [
        start_episode + i
        for i in range(5)
    ]

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:

        for episode in episodes:

            content = (
                "TEST FILE\n"
                f"Episode: {episode}\n"
                "Quality: 1080p\n"
                "Batch download test only.\n"
            )

            filename = (
                f"Episode_{episode}_1080p.txt"
            )

            zip_file.writestr(
                filename,
                content
            )

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition":
                f"attachment; "
                f"filename=batch_{batch_number}.zip"
        }
    )

@app.get("/test-source")
def test_source():

    from sources import DemoSourceAdapter

    adapter = DemoSourceAdapter()

    source = adapter.get_episode_source(
        page_url="https://example.com/perfect-world-episode-281",
        episode_number=281
    )

    selected = source.highest_quality()

    return {
        "episode": source.episode_number,
        "page_url": source.page_url,
        "available_qualities": [
            quality.label
            for quality in source.qualities
        ],
        "selected_quality": (
            selected.label
            if selected
            else None
        ),
        "selected_height": (
            selected.height
            if selected
            else None
        )
    }

@app.get("/test-ffmpeg")
def test_ffmpeg():

    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return {
                "status": "error",
                "message": result.stderr
            }

        first_line = (
            result.stdout
            .splitlines()[0]
            if result.stdout
            else "FFmpeg detected"
        )

        return {
            "status": "ok",
            "ffmpeg": first_line
        }

    except FileNotFoundError:
        return {
            "status": "not_installed",
            "message": "FFmpeg is not installed."
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }

@app.get("/test-merge")
def test_merge():

    import os
    import shutil
    import tempfile
    import subprocess

    from fastapi.responses import StreamingResponse

    temp_dir = tempfile.mkdtemp()

    try:
        video_files = []

        # Create 5 short test videos
        for i in range(1, 6):

            output_file = os.path.join(
                temp_dir,
                f"episode_{i}.mp4"
            )

            command = [
                "ffmpeg",
                "-y",
                "-f", "lavfi",
                "-i",
                "testsrc=size=640x360:rate=24",
                "-t", "2",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-an",
                output_file
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise RuntimeError(
                    result.stderr[-2000:]
                )

            video_files.append(output_file)

        # Create concat list
        concat_file = os.path.join(
            temp_dir,
            "concat.txt"
        )

        with open(
            concat_file,
            "w",
            encoding="utf-8"
        ) as file:

            for video in video_files:
                file.write(
                    f"file '{video}'\n"
                )

        # Merge videos
        merged_file = os.path.join(
            temp_dir,
            "merged_batch.mp4"
        )

        merge_command = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            merged_file
        ]

        result = subprocess.run(
            merge_command,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr[-2000:]
            )

        with open(
            merged_file,
            "rb"
        ) as file:

            video_data = file.read()

        return StreamingResponse(
            iter([video_data]),
            media_type="video/mp4",
            headers={
                "Content-Disposition":
                    "attachment; "
                    "filename=merged_batch_test.mp4"
            }
        )

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }

    finally:
        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

@app.get("/test-media-module")
def test_media_module():

    from media import merge_videos

    return {
        "status": "ok",
        "module": "media.py",
        "function": "merge_videos",
        "ready": callable(merge_videos)
    }

@app.get("/test-batch-merge/{batch_number}")
def test_batch_merge(batch_number: int, batch_size: int = 5):

    import os
    import shutil
    import tempfile
    import subprocess

    from fastapi.responses import FileResponse
    from media import merge_videos

    allowed_batch_sizes = [5, 10, 20]

    if batch_number < 1:
        return {
            "status": "error",
            "message": "Invalid batch number."
        }

    if batch_size not in allowed_batch_sizes:
        return {
            "status": "error",
            "message":
                "Batch size must be 5, 10, or 20."
        }

    temp_dir = tempfile.mkdtemp()

    try:

        video_files = []

        start_episode = (
            ((batch_number - 1) * batch_size)
            + 281
        )

        for i in range(batch_size):

            episode_number = (
                start_episode + i
            )

            output_file = os.path.join(
                temp_dir,
                f"episode_{episode_number}.mp4"
            )

            command = [
                "ffmpeg",
                "-y",
                "-f", "lavfi",
                "-i",
                "testsrc=size=640x360:rate=24",
                "-t", "2",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-an",
                output_file
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise RuntimeError(
                    result.stderr[-2000:]
                )

            video_files.append(
                output_file
            )

        merged_file = os.path.join(
            temp_dir,
            f"batch_{batch_number}_{batch_size}.mp4"
        )

        merge_videos(
            video_files,
            merged_file
        )

        return FileResponse(
            merged_file,
            media_type="video/mp4",
            filename=(
                f"batch_{batch_number}_"
                f"{batch_size}_episodes.mp4"
            ),
            background=None
        )

    except Exception as error:

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

        return {
            "status": "error",
            "message": str(error)
        }

@app.get("/test-authorized-download")
async def test_authorized_download(url: str):

    import re
    from urllib.parse import urljoin
    import httpx

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=60,
            headers=headers
        ) as client:

            response = await client.get(url)

            content_type = (
                response.headers.get("content-type")
                or ""
            ).lower()

            # --------------------------------
            # CASE 1: URL itself is a video
            # --------------------------------

            if content_type.startswith("video/"):

                return {
                    "status": "direct_video",
                    "video_url": str(response.url),
                    "content_type": content_type
                }

            # --------------------------------
            # CASE 2: URL is a webpage
            # --------------------------------

            if "text/html" not in content_type:

                return {
                    "status": "error",
                    "message":
                        "URL is neither a video nor an HTML page.",
                    "content_type": content_type
                }

            html = response.text

            # Find ordinary href links
            links = re.findall(
                r'href\s*=\s*["\']([^"\']+)["\']',
                html,
                re.IGNORECASE
            )

            checked_links = []

            # --------------------------------
            # Check candidate links
            # --------------------------------

            for link in links:

                candidate = urljoin(
                    str(response.url),
                    link
                )

                lower_candidate = candidate.lower()

                if not any(
                    extension in lower_candidate
                    for extension in [
                        ".mp4",
                        ".mkv",
                        ".webm",
                        ".mov"
                    ]
                ):
                    continue

                # Don't trust the filename.
                # Verify the actual response.
                try:

                    check = await client.get(
                        candidate,
                        follow_redirects=True
                    )

                    candidate_type = (
                        check.headers.get(
                            "content-type"
                        )
                        or ""
                    ).lower()

                    checked_links.append({
                        "url": candidate,
                        "content_type": candidate_type,
                        "http_status":
                            check.status_code
                    })

                    if candidate_type.startswith(
                        "video/"
                    ):

                        return {
                            "status":
                                "verified_video",
                            "video_url":
                                str(check.url),
                            "content_type":
                                candidate_type,
                            "http_status":
                                check.status_code
                        }

                except Exception:
                    continue

            # --------------------------------
            # No verified video found
            # --------------------------------

            return {
                "status": "no_verified_video",
                "message":
                    "The page contains no ordinary "
                    "download link that returned video/*.",
                "page_url":
                    str(response.url),
                "checked_links":
                    checked_links[:10]
            }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error)
        }
