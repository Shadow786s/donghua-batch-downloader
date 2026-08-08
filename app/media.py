import os
import subprocess
import tempfile


def merge_videos(video_files, output_file):
    if not video_files:
        raise ValueError("No video files supplied.")

    concat_file = os.path.join(
        os.path.dirname(output_file),
        "concat.txt"
    )

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as file:

        for video in video_files:
            absolute_path = os.path.abspath(video)

            safe_path = absolute_path.replace(
                "'",
                "'\\''"
            )

            file.write(
                f"file '{safe_path}'\n"
            )

    command = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output_file
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr[-3000:]
        )

    return output_file
