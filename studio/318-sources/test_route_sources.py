"""No-network acceptance tests: 318 original sources are *routed*, not executed."""
import importlib.util
import tempfile
import json
import unittest
from pathlib import Path

modpath=Path(__file__).with_name("route_sources.py")
spec=importlib.util.spec_from_file_location("film_source_router",modpath)
router=importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)

class Frozen318RouterTests(unittest.TestCase):
    def test_full_frozen_index_and_all_ten_stages(self):
        items=router.read_catalog()
        self.assertEqual(len(items),318)
        count=router.coverage(items)
        self.assertEqual(count["total_upstream"],318)
        self.assertEqual(len(count["production_categories"]),10)
        self.assertEqual(sum(count["production_categories"].values()),318)
        self.assertEqual(count["fully_runtime_certified_upstream"],0)
    def test_no_fabricated_active_runtime(self):
        items=router.read_catalog()
        self.assertTrue(all(x["integration_status"]=="not integrated by audit alone" for x in items))
        self.assertTrue(all("repo" in x and "review_before_use" in x for x in items))
        self.assertEqual(len([x for x in items if x["original_index_license"] in ("MISSING","NOASSERTION")]),80)
    def test_all_stages_have_research_candidates(self):
        items=router.read_catalog()
        for stage in router.STAGES:
            q=router.research_candidates(items,stage,limit=5)
            self.assertTrue(q,stage)
            self.assertLessEqual(len(q),5)
            self.assertTrue(all(a["readme"].startswith("https://github.com/") for a in q))
            self.assertTrue(all(a["next_action"].startswith("Read complete") for a in q))
    def test_incomplete_or_duplicate_catalog_fails_closed(self):
        items=router.read_catalog()
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"index.json"
            p.write_text(json.dumps({"source_count":318,"items":items[:-1]}))
            with self.assertRaises(ValueError):router.read_catalog(p)
            corrupt=[dict(x) for x in items]
            corrupt[1]["repo"]=corrupt[0]["repo"]
            p.write_text(json.dumps({"source_count":318,"items":corrupt}))
            with self.assertRaises(ValueError):router.read_catalog(p)
    def test_invalid_stages_blocked(self):
        with self.assertRaises(ValueError):router.research_candidates(router.read_catalog(),"all-at-once")
        with self.assertRaises(ValueError):router.research_candidates(router.read_catalog(),"editing-compositing",limit=0)

if __name__=="__main__":unittest.main()
