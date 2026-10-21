import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import os
SPEC=importlib.util.spec_from_file_location('sources',str(Path(__file__).parents[1]/'import_verified_sources.py'))
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
class AuditTests(unittest.TestCase):
    def test_manifest_exact(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'m.json'
            payload={'skills':[{'repo_full_name':f'source/repo-{i}'} for i in range(318)]}
            p.write_text(json.dumps(payload))
            self.assertEqual(len(M.manifest(p)[1]),318)
            payload['skills'][2]['repo_full_name']='source/repo-1'
            p.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError,'Duplicate'):
                M.manifest(p)
    def test_file_inventory_real_git(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            subprocess.run(['git','init','-q',str(p)],check=True)
            (p/'SKILL.md').write_text('# Direct source\n')
            (p/'engine.py').write_text('pass\n')
            subprocess.run(['git','add','SKILL.md','engine.py'],cwd=p,check=True)
            files=M.audit_checkout(p)['files']
            self.assertEqual(len(files),2)
            self.assertTrue(all(x['type']=='file' for x in files))
            (p/'engine.py').write_text('version https://git-lfs.github.com/spec/v1\n')
            with self.assertRaisesRegex(RuntimeError,'LFS'):
                M.audit_checkout(p)
if __name__=='__main__':unittest.main()
