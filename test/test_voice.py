import importlib.util, tempfile, unittest, wave
from pathlib import Path
spec=importlib.util.spec_from_file_location('voice',Path(__file__).resolve().parents[1]/'scripts/voice.py')
voice=importlib.util.module_from_spec(spec);spec.loader.exec_module(voice)
class Timing(unittest.TestCase):
    def test_service_split_and_mismatch(self):
        b=[{'text':'Hai','start':.1,'end':.3},{'text':'Mikro','start':.4,'end':.7},{'text':'organisma','start':.7,'end':1.2}]
        result=voice.align('Hai. Mikroorganisma...',b)
        self.assertEqual(len(result),2);self.assertEqual(result[1]['end'],1.2)
        self.assertEqual(voice.align('Teks lain',b),[])
    def test_pause_shifts_boundary_and_audio(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'a.wav'
            with wave.open(str(path),'wb') as f:
                f.setparams((1,2,24000,0,'NONE','not compressed'));f.writeframes(b'\0\0'*72000)
            words=[{'index':0,'text':'saya...','start':.2,'end':.8},{'index':1,'text':'sebelum,','start':1.,'end':1.5},{'index':2,'text':'hai.','start':2.,'end':2.5}]
            result=voice.pauses(path,words)
            self.assertAlmostEqual(result[1]['start'],1.3);self.assertAlmostEqual(result[2]['start'],2.37)
            with wave.open(str(path),'rb') as f:self.assertEqual(f.getnframes(),round(3.37*24000))
if __name__=='__main__':unittest.main()
