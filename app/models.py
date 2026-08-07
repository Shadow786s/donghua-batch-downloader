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
