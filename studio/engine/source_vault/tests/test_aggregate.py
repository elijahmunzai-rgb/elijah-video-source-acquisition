import unittest,sys, tempfile, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from verify_combined import combine

class CombinedTests(unittest.TestCase):
 def test_reject_missing_and_dupes(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   manifest=root/'manifest.json'
   manifest.write_text(json.dumps({'skills':[{'repo_full_name':f'test/repo-{i}'} for i in range(318)]}))
   result=root/'results.json'
   result.write_text(json.dumps([{'repo':'test/repo-0','status':'verified','commit':'abcdef','tree':'abcdef','files':1}]))
   report=combine(manifest,[result]);self.assertEqual(len(report['missing']),317);self.assertFalse(report['complete_318'])
   report=combine(manifest,[result,result]);self.assertIn('test/repo-0',report['duplicate_entries']);self.assertFalse(report['complete_318'])
 def test_complete(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)
   manifest=root/'manifest.json'
   manifest.write_text(json.dumps({'skills':[{'repo_full_name':f'test/repo-{i}'} for i in range(318)]}))
   result=root/'results.json'
   result.write_text(json.dumps([{'repo':f'test/repo-{i}','status':'verified','commit':'abcdef','tree':'abcdef','files':1} for i in range(318)]))
   report=combine(manifest,[result]);self.assertEqual(report['verified'],318);self.assertTrue(report['complete_318'])
if __name__=='__main__': unittest.main()
