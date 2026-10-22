import copy
import json
import tempfile
import unittest
from pathlib import Path
from activate import load,plan,report,SAFE_STAGES

class StrictRegistryTests(unittest.TestCase):
 def setUp(self):self.obj=load()
 def test_318_unique_complete_and_historically_verified(self):
  r=report(self.obj)
  self.assertEqual(r["component_entries"],318)
  self.assertEqual(r["historical_source_snapshots"],318)
  self.assertEqual(r["status_counts"]["integration_verified"],0)
  self.assertEqual(r["status_counts"]["cinematic_quality_verified"],0)
 def test_all_ten_production_stages_nonempty(self):
  for stage in SAFE_STAGES:
   q=plan(self.obj,stage,20)
   self.assertTrue(q,stage)
 def test_does_not_risk_hostinger_gpu_private_media_or_purchases(self):
  for k in ["allow_paid_services","allow_dan_gpu","allow_hostinger_heavy_render"]:
   self.assertFalse(self.obj[k])
  self.assertTrue(all(not x["private_media_allowed"] and not x["paid_calls_allowed"]
                      for x in self.obj["records"]))
 def test_license_cautions_propagated(self):
  self.assertGreater(report(self.obj)["license_caution_preliminary"],75)
 def check_invalid(self,change):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"matrix.json";o=copy.deepcopy(self.obj);change(o)
   p.write_text(json.dumps(o))
   with self.assertRaises(ValueError):load(p)
 def test_missing_entry_fails(self):self.check_invalid(lambda x:x["records"].pop())
 def test_duplicate_repo_fails(self):
  self.check_invalid(lambda x:x["records"][1].update(repo=x["records"][0]["repo"]))
 def test_unearned_certification_fails(self):
  self.check_invalid(lambda x:x["records"][0].update(integration_verified=True))
 def test_unearned_creative_quality_fails(self):
  self.check_invalid(lambda x:x["records"][0].update(cinematic_quality_verified=True))
 def test_paid_or_private_enablement_fails(self):
  self.check_invalid(lambda x:x.update(allow_paid_services=True))
  self.check_invalid(lambda x:x["records"][0].update(private_media_allowed=True))

if __name__=="__main__":unittest.main()
