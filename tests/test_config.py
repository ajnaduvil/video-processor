import unittest

from video_processor.config import AppConfig


class ConfigTests(unittest.TestCase):
    def test_round_trip(self):
        config = AppConfig(
            input_dir="input",
            output_dir="output",
            video_codec="h265",
            crf=28,
            preset="slow",
            audio_codec="opus",
            audio_bitrate_kbps=96,
            target_fps=30,
            extensions=[".mp4", ".mkv"],
            parallel=False,
            workers=1,
            dry_run=True,
            collision_policy="suffix",
            enable_csv_log=False,
            enable_json_log=True,
            json_log_path="log.jsonl",
            theme="light",
        )
        data = config.to_dict()
        loaded = AppConfig.from_dict(data)
        self.assertEqual(loaded.video_codec, "h265")
        self.assertEqual(loaded.audio_codec, "opus")
        self.assertEqual(loaded.extensions, [".mp4", ".mkv"])
        self.assertEqual(loaded.theme, "light")


if __name__ == "__main__":
    unittest.main()
