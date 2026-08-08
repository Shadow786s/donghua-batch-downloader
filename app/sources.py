from models import EpisodeSource, QualityOption


class SourceAdapter:

    def get_episode_source(
        self,
        page_url: str,
        episode_number: int | None = None
    ) -> EpisodeSource:

        raise NotImplementedError


class DemoSourceAdapter(SourceAdapter):

    def get_episode_source(
        self,
        page_url: str,
        episode_number: int | None = None
    ) -> EpisodeSource:

        qualities = [
            QualityOption(
                label="480p",
                height=480,
                url="https://example.com/demo-480"
            ),
            QualityOption(
                label="720p",
                height=720,
                url="https://example.com/demo-720"
            ),
            QualityOption(
                label="1080p",
                height=1080,
                url="https://example.com/demo-1080"
            )
        ]

        return EpisodeSource(
            episode_number=episode_number,
            page_url=page_url,
            qualities=qualities
        )
