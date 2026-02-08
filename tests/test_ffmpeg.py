import unittest

from video_processor.ffmpeg import build_ffmpeg_command


class FFmpegCommandTests(unittest.TestCase):
    def test_h264_command(self):
        cmd = build_ffmpeg_command(
            "in.mp4",
            "out.mp4",
            video_codec="h264",
            crf=23,
            preset="medium",
            audio_codec="aac",
            audio_bitrate_kbps=128,
            target_fps=None,
            overwrite=True,
        )
        self.assertIn("libx264", cmd)
        self.assertIn("aac", cmd)

    def test_h265_command(self):
        cmd = build_ffmpeg_command(
            "in.mp4",
            "out.mp4",
            video_codec="h265",
            crf=28,
            preset="slow",
            audio_codec="opus",
            audio_bitrate_kbps=96,
            target_fps=30,
            overwrite=False,
        )
        self.assertIn("libx265", cmd)
        self.assertIn("libopus", cmd)
        self.assertIn("-r", cmd)


if __name__ == "__main__":
    unittest.main()
