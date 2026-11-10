import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from spam_detector import load_data, load_model, predict

class ClassifierTests(unittest.TestCase):
    def test_deduplication_and_conflicts(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'sample.tsv'
            p.write_text('ham\tHello Friend\nham\t hello   friend \nspam\tWin now\nham\tWIN NOW\nspam\tFree prize\n',encoding='utf-8')
            x,y,stats=load_data(p)
            self.assertEqual(len(x),2)
            self.assertEqual(set(y),{'ham','spam'})
            self.assertEqual(stats['raw_rows'],5)
    def test_saved_model_predictions(self):
        model=load_model()
        self.assertEqual(predict('Can we meet tomorrow for lunch?',model)['label'],'ham')
        self.assertEqual(predict('Congratulations! You have won a free prize. Call now to claim!',model)['label'],'spam')
    def test_empty_and_unsupported_text(self):
        for text in ['', '  ', 'سلام دوست من', '123456']:
            with self.assertRaises(ValueError): predict(text)
    @unittest.skipUnless((Path(__file__).resolve().parents[1]/"runtime/python.exe").exists(), "E-drive isolation check applies to the original local installation")
    def test_runtime_and_packages_on_e(self):
        import sklearn, numpy, scipy, joblib
        for path in [sys.executable,sys.base_prefix,sklearn.__file__,numpy.__file__,scipy.__file__,joblib.__file__]:
            self.assertEqual(Path(path).drive.upper(),'E:')

if __name__=='__main__': unittest.main()
