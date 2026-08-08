import os
import subprocess


def merge_videos(video_files, output_file):
    """
    Merge authorized/local video files into one MP4.

    The files are merged in the exact order supplied
    in video_files.
    """

    if not video_files:
        raise ValueError("No video files supplied.")

    output_dir = os.path.dirname(
        os.path.abspath(output_file)
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    concat_file = os.path.join(
        output_dir,
        "concat.txt"
    )

    try:

        with open(
            concat_file,
            "w",
            encoding="utf-8"
        ) as file:

            for video in video_files:

                if not os.path.isfile(video):
                    raise FileNotFoundError(
                        f"Video file not found: {video}"
                    )

                absolute_path = os.path.abspath(
                    video
                )

                safe_path = (
                    absolute_path
                    .replace("\\", "/")
                    .replace("'", "'\\''")
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
            "-movflags", "+faststart",
            output_file
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode != 0:
            raise RuntimeError(
                "FFmpeg merge failed:\n"
                + result.stderr[-4000:]
            )

        if not os.path.isfile(output_file):
            raise RuntimeError(
                "FFmpeg finished but output "
                "file was not created."
            )

        if os.path.getsize(output_file) == 0:
            raise RuntimeError(
                "Merged output file is empty."
            )

        return output_file

    finally:

        if os.path.exists(concat_file):
            try:
                os.remove(concat_file)
            except OSError:
                pass
