import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from comfy_local_worker import approved_workflow, safe_output_name, validate_workflow, workflow_bytes

EXAMPLE = {"1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "audited_model.safetensors"}},
           "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "Public example only"}}}

class LocalWorkerSecurityTests(unittest.TestCase):
    def test_accepts_api_node_mapping_only(self):
        self.assertEqual(len(validate_workflow(json.dumps(EXAMPLE).encode())), 2)
        for invalid in [[], {"1": {"inputs": {}}}, {"x": {"class_type": "KSampler", "inputs": {}}}]:
            with self.assertRaises(ValueError):
                validate_workflow(json.dumps(invalid).encode())

    def test_rejects_unapproved_workflow_sha(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/"workflow.json"
            p.write_text(json.dumps(EXAMPLE))
            policy = Path(directory)/"approved-workflows.json"
            policy.write_text('{"approved_sha256":[]}')
            with self.assertRaises(PermissionError):
                approved_workflow(p, policy)
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            policy.write_text(json.dumps({"approved_sha256": [digest]}))
            _, actual = approved_workflow(p, policy)
            self.assertEqual(digest, actual)
            p.write_text(p.read_text() + " ")
            with self.assertRaises(PermissionError):
                approved_workflow(p, policy)

    def test_blocks_oversized_config(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/"workflow.json"
            p.write_bytes(b"x"*2_000_001)
            with self.assertRaises(ValueError):
                workflow_bytes(p)

    def test_prevents_traversal_and_nonmedia_downloads(self):
        for bad in ["../key.txt", "/tmp/video.mp4", "..", ".hidden.mp4", "video.exe", "video.mp4/evil", "bad*.mp4"]:
            with self.assertRaises(ValueError, msg=bad):
                safe_output_name(bad)
        self.assertEqual(safe_output_name("scene_01.mp4"), "scene_01.mp4")
        self.assertEqual(safe_output_name("frame 02.png"), "frame 02.png")

if __name__ == "__main__":
    unittest.main()
