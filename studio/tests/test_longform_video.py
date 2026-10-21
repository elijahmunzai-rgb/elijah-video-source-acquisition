from pathlib import Path
import importlib.util
import unittest

ROOT=Path(__file__).resolve().parent.parent
SPEC=importlib.util.spec_from_file_location('film_render',ROOT/'engine'/'render.py')
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

class TenMinuteFilmTests(unittest.TestCase):
    def test_10minute_timeline_is_valid(self):
        scenes=[{'duration':30,'layers':[{'type':'text','text':f'Chapter {i+1}','x':.5,'y':.5,'size':40}]} for i in range(20)]
        conf={'canvas':{'width':640,'height':360,'fps':24},'scenes':scenes}
        w,h,fps,d=M.validate(conf,ROOT)
        self.assertEqual((w,h,fps,d),(640,360,24,600.0))
    def test_over_ten_minutes_rejected(self):
        scenes=[{'duration':30,'layers':[]} for _ in range(21)]
        conf={'canvas':{'width':640,'height':360,'fps':24},'scenes':scenes}
        with self.assertRaisesRegex(ValueError,'600'):M.validate(conf,ROOT)
    def test_nonexistent_media_rejected(self):
        conf={'canvas':{'width':640,'height':360,'fps':24},'scenes':[{'duration':1,'layers':[{'type':'image','path':'never-create-this-image.png'}]}]}
        with self.assertRaises(FileNotFoundError):M.validate(conf,ROOT)

if __name__=='__main__':unittest.main()
