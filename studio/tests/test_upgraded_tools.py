from pathlib import Path
import importlib.util
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent

def load(name):
  spec=importlib.util.spec_from_file_location(name,ROOT/'engine'/f'{name}.py')
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

class QualityUpgradeTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.audit=load('production_audit');cls.mixer=load('audio_mix')
  def test_01_v4_under_bitrate_lufs_flags(self):
    old=Path('/mnt/data/IO_Agency_Cinematic_Code_Directed_V4_30s.mp4')
    if not old.exists():self.skipTest('V4 unavailable outside current workspace')
    d=self.audit.audit(old,True)
    self.assertTrue(any('bitrate' in x for x in d['review_flags']))
    self.assertTrue(any('quiet' in x for x in d['review_flags']))
    self.assertTrue(any('low audio dynamics' in x for x in d['review_flags']))
    self.assertEqual(d['duration_sec'],30.0)
  def test_02_empty_media_errors(self):
    with self.assertRaises(FileNotFoundError):self.audit.audit('/fake/path/bad.mp4')
  def test_03_audio_mix_3sec_stereo(self):
    class A:pass
    with tempfile.TemporaryDirectory() as tmp:
      d=Path(tmp)
      for name, freq in [('v',220),('m',110)]:
        subprocess.run(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i',f'sine=frequency={freq}:duration=3:sample_rate=48000',str(d/f'{name}.wav')],check=True)
      a=A();a.voice=d/'v.wav';a.music=d/'m.wav';a.effects=None;a.duration=3.0;a.target_lufs=-16;a.music_gain=.22;a.effects_gain=.48;a.output=d/'mix.wav'
      subprocess.run(self.mixer.build_command(a),check=True,capture_output=True)
      self.assertTrue(a.output.exists())
      probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=channels','-show_entries','format=duration','-of','csv=p=0',str(a.output)]).decode()
      self.assertIn('2',probe)
      self.assertIn('3.000000',probe)
  def test_04_all_specialists_have_frontmatter(self):
    dirs=[x for x in (ROOT/'skills').glob('*/SKILL.md')]
    self.assertEqual(len(dirs),10)
    for f in dirs:self.assertTrue(f.read_text().startswith('---\nname: '))

if __name__=='__main__':unittest.main()
