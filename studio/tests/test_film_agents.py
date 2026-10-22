import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SRC=Path(__file__).parents[1]/"agents"/"pipeline.py"
spec=importlib.util.spec_from_file_location("studio_film_agents",SRC)
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class FilmAgentTests(unittest.TestCase):
    def setUp(self):
        self.b=a.brief("A New Frame","Promote a source-cleared cinematic demo",30,"landscape",True)
    def test_director_30s(self):
        shots=a.director(self.b)
        self.assertEqual(len(shots),10)
        self.assertAlmostEqual(sum(s["duration"] for s in shots),30)
        self.assertEqual(len({s["id"] for s in shots}),10)
    def test_original_2_and_10_min_storyboards_are_plans_only(self):
        for d,count in [(120,16),(600,20)]:
            b={**self.b,"duration":d}
            s=a.director(b)
            self.assertEqual(len(s),count)
            self.assertAlmostEqual(sum(x["duration"] for x in s),d)
            self.assertTrue(all(not x["asset_verified"] for x in s))
    def test_no_private_briefs_in_public_repo(self):
        with self.assertRaises(ValueError):
            a.brief("Confidential","Sensitive",30,"landscape",False)
    def test_input_validation(self):
        with self.assertRaises(ValueError):
            a.brief("X","Y",6000,"landscape",True)
        with self.assertRaises(ValueError):
            a.brief("X","Y",30,"wrong",True)
    def test_preview_is_only_six_seconds(self):
        s=a.motion(self.b)
        self.assertEqual(sum(x["duration"] for x in s["scenes"]),6)
        self.assertEqual(s["canvas"],{"width":1920,"height":1080,"fps":24})
        self.assertEqual(s["renderer"],"studio/agents/premium_preview.py")
        self.assertIn("NOT photoreal",s["preview_type"])
        self.assertTrue(s["audio"]["copyright_cleared"])
    def test_agent_handoffs_and_sha256(self):
        with tempfile.TemporaryDirectory() as t:
            out=a.build(self.b,t)
            manifest=json.loads((out/"manifest.json").read_text())
            rights=json.loads((out/"rights.json").read_text())
            qa=json.loads((out/"qa.json").read_text())
            self.assertEqual(len(manifest["role_agents"]),8)
            self.assertFalse(manifest["full_film_rendered"])
            self.assertFalse(rights["public_delivery_approved"])
            self.assertFalse(qa["full_film_rendered"])
            self.assertTrue(qa["duration_correct"])
            self.assertEqual(len(manifest["files_sha256"]),10)

if __name__=="__main__":
    unittest.main()
