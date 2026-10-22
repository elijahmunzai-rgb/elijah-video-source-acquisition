import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from render_timeline import VALID_DURATIONS,MIN_SHOTS,validate,within_asset

def fake_project(duration=30):
    n=MIN_SHOTS[duration]
    base=duration//n;extra=duration-base*n
    return {
        'schema':'elijah-film-project-v1','duration':duration,'aspect':'landscape',
        'title':'Real Film', 'release_approved':False,
        'voice':{'mode':'licensed-recording','rights':'Artist-release','reference':'voice.wav'},
        'music':{'mode':'licensed-track','rights':'Composer-release','reference':'music.wav'},
        'scenes':[{'id':f'scene-{i+1}','duration':base+(i<extra),
                   'source_in':0,'media_ref':f'clip{i+1}.mp4',
                   'media_rights':'Approved source evidence',
                   'reviewed':True,'direction':'Original authored action',
                   'narration':'Hello'} for i in range(n)]
    }

class RealTimelineTests(unittest.TestCase):
 def setUp(self):
    self.temp=tempfile.TemporaryDirectory()
    self.root=Path(self.temp.name)
    for i in range(1,35):(self.root/f'clip{i}.mp4').write_bytes(b'fake but inspected via mock ffprobe')
    for x in ('voice.wav','music.wav'):(self.root/x).write_bytes(b'fake')
 def tearDown(self):self.temp.cleanup()
 def probe(self,path):
    p=Path(path)
    if p.suffix=='.mp4':
        return {'duration':65,'video':{'codec_name':'h264'},'streams':[]}
    return {'duration':650,'video':None,'streams':[]}
 def check(self,obj):
    with patch('render_timeline.media',side_effect=self.probe):
        return validate(obj,self.root)
 def test_all_six_duration_render_contracts(self):
    for duration in sorted(VALID_DURATIONS):
        project=fake_project(duration)
        jobs=self.check(project)
        self.assertEqual(len(jobs),MIN_SHOTS[duration])
        self.assertEqual(sum(j['duration'] for j in jobs),duration)
 def test_exactly_timed_real_assets_required(self):
    p=fake_project();p['scenes'][0]['duration']+=1
    with self.assertRaisesRegex(ValueError,'exactly equal'):self.check(p)
    p=fake_project();p['scenes'][0]['media_ref']='../private.mp4'
    with self.assertRaisesRegex(ValueError,'traversal'):self.check(p)
 def test_no_extra_spending_or_gpu_needed_for_renderer_contract(self):
    p=fake_project(300)
    self.assertEqual(self.check(p)[0]['start'],0)
    p['voice']={'mode':'none'}
    with self.assertRaisesRegex(ValueError,'Voice track required'):self.check(p)
 def test_no_duplicate_range_loops_for_long_films(self):
    p=fake_project(600)
    for i in range(1,len(p['scenes'])):p['scenes'][i]['media_ref']='clip1.mp4'
    with self.assertRaisesRegex(ValueError,'Repeated/overlapping'):self.check(p)
 def test_no_fake_rights_or_unsigned_scenes(self):
    p=fake_project(15);p['scenes'][0]['reviewed']=False
    with self.assertRaisesRegex(ValueError,'human scene review'):self.check(p)
 def test_real_source_duration_is_checked(self):
    p=fake_project(15);p['scenes'][0]['source_in']=62
    with self.assertRaisesRegex(ValueError,'more footage'):self.check(p)
 def test_strict_duration_types(self):
    p=fake_project();p['duration']=True
    with self.assertRaisesRegex(ValueError,'Choose exact'):self.check(p)
 def test_only_relative_safe_media_paths(self):
    with self.assertRaises(ValueError):within_asset('/etc/passwd',self.root)
    with self.assertRaises(ValueError):within_asset('../secrets.txt',self.root)

if __name__=='__main__':unittest.main()
