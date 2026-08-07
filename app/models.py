from dataclasses import dataclass, field


@dataclass
class QualityOption:
    label: str
    height: int
    url: str


@dataclass
class EpisodeSource:
    episode_number: int | None
    page_url: str
    qualities: list[QualityOption] = field(
        default_factory=list
    )

    def highest_quality(self):
        if not self.qualities:
            return None

        return max(
            self.qualities,
            key=lambda quality: quality.height
        )

    def quality_summary(source: EpisodeSource):
        selected = source.highest_quality()

        if selected is None:
            return {
                "status": "no_quality_available"
            }

        return {
            "status": "ready",
            "selected_quality": selected.label,
            "height": selected.height
        }

    def demo_quality_selection():
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
