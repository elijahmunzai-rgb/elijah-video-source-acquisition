"""Quality checks must prove real motion and actual audio, not just an MP4 file."""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np

SCRIPT=Path(__file__).parents[1]/"agents"/"premium_preview.py"
spec=importlib.util.spec_from_file_location("studio_premium_preview",SCRIPT)
q=importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)

class QualityTests(unittest.TestCase):
    def test_private_content_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                q.render({"title":"PRIVATE","aspect":"landscape","privacy":"confidential"},Path(d)/"a.mp4",width=320,fps=12)
    def test_original_audio_is_written(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"original.wav"
            q.sound(path)
            self.assertGreater(path.stat().st_size,100000)
    def test_real_video_has_motion_original_audio_and_scene_changes(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/"preview.mp4"
            brief={"title":"AN ORIGINAL FRAME","goal":"Demonstrate storyboarding","aspect":"landscape","privacy":"public-demo"}
            result=q.render(brief,output,width=640,fps=12,preview_frames=[12,18,24,30])
            self.assertEqual((result["width"],result["height"],result["duration"]),(640,360,6))
            data=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(output)]))
            self.assertAlmostEqual(float(data["format"]["duration"]),6,delta=.1)
            self.assertIn("h264",[s["codec_name"] for s in data["streams"]])
            self.assertIn("aac",[s["codec_name"] for s in data["streams"]])
            frames=[np.asarray(x.resize((160,90)).convert("RGB")).astype(np.float32) for _,x in result["preview"]]
            self.assertGreater(np.abs(frames[0]-frames[1]).mean(),0.2,"Need motion even within a scene")
            self.assertGreater(np.abs(frames[1]-frames[2]).mean(),4,"Need visual changes between scenes")
            self.assertGreater(output.stat().st_size,150000,"Prevent tiny slideshow-like exports")

if __name__=="__main__":unittest.main()
