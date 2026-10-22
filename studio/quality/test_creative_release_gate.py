import importlib.util
import unittest
from pathlib import Path

p=Path(__file__).with_name("creative_release_gate.py")
spec=importlib.util.spec_from_file_location("creative_film_gate",p)
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
def sample(n=6):
    return {"deliverable_type":"commercial_30s",
      "shots":[{"id":f"s{i+1}","media_type":"rights-cleared-recorded-footage","media_reference":f"cleared_{i}.mp4",
        "rights_reference":f"license_{i}.md","rights_approved":True,"visual_review_passed":True,
        "reuses_identical_frames":False} for i in range(n)],
      "audio":{"type":"human-narration","source_reference":"approved_narration.wav","rights_approved":True,
        "human_listen_passed":True,"dialogue_required":True,"intelligible_narration_verified":True},
      "review":{"real_reviewer_id":"responsible-art-director","watched_entire_video":True,
        "scores":{k:4.2 for k in gate.REQUIRED_SCORES}},
      "media_probe":{"duration_seconds":30,"width":1920,"height":1080,"codec":"h264","audio_codec":"aac","manually_played":True},
      "public_publish_approved":True}
class CreativeReleaseTests(unittest.TestCase):
    def test_true_complete_dummy_evidence_schema_can_pass_only_when_all_checks_present(self):
        self.assertEqual(gate.assess_manifest(sample()),[])
    def test_previous_360p_typography_silent_demo_is_rejected(self):
        s=sample(3);s["shots"][0]["media_type"]="typography-card";s["media_probe"]["width"]=640
        s["media_probe"]["height"]=360;s["media_probe"]["audio_codec"]=None
        s["audio"]["human_listen_passed"]=False;s["review"]["scores"]["story"]=2
        errors=gate.assess_manifest(s)
        self.assertGreaterEqual(len(errors),6)
        self.assertTrue(any("typography slide" in x for x in errors))
    def test_lacks_approvals_and_rights(self):
        s=sample();s["shots"][0]["rights_approved"]=False;s["public_publish_approved"]=False
        s["review"]["watched_entire_video"]=False
        self.assertGreaterEqual(len(gate.assess_manifest(s)),3)
    def test_full_film_cannot_be_looped_short_ad(self):
        s=sample();s["deliverable_type"]="film_600s";s["media_probe"]["duration_seconds"]=600
        s["shots"][1]["reuses_identical_frames"]=True
        errors=gate.assess_manifest(s)
        self.assertTrue(any("30 distinct" in x for x in errors))
        self.assertTrue(any("repeated footage" in x for x in errors))
    def test_duration_must_be_actual_media_probe(self):
        s=sample();s["media_probe"]["duration_seconds"]=600
        self.assertTrue(any("encoded duration" in x for x in gate.assess_manifest(s)))
    def test_empty_manifest_fails_closed(self):
        self.assertTrue(gate.assess_manifest({}))
        self.assertTrue(gate.assess_manifest(None))
if __name__=="__main__":unittest.main()
