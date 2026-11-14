from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent

class AppTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file(str(ROOT/'app.py'), default_timeout=30).run()

    def test_demo_group_change_and_filter(self):
        at = self.app()
        self.assertFalse(at.exception)
        self.assertEqual(at.metric[0].value, '400')
        at.slider(key='groups').set_value(3)
        at.button(key='analyze').click().run()
        self.assertFalse(at.exception)
        self.assertEqual(at.metric[3].value, '3')
        at.segmented_control(key='view').set_value('فهرست مشتریان').run()
        at.text_input(key='search').set_value('C0001').run()
        self.assertFalse(at.exception)
        self.assertEqual(len(at.dataframe[0].value), 1)
        at.multiselect(key='segments').set_value([]).run()
        self.assertEqual(len(at.dataframe[0].value), 0)

    def test_upload_and_invalid_file(self):
        at = self.app()
        at.radio(key='source').set_value('بارگذاری CSV').run()
        self.assertFalse(at.exception)
        at.file_uploader(key='upload').upload('orders.csv', (ROOT/'sample_orders.csv').read_bytes()).run()
        self.assertFalse(at.exception)
        self.assertEqual(at.metric[0].value, '400')
        at.file_uploader(key='upload').clear().run()
        at.file_uploader(key='upload').upload('bad.csv', b'wrong,columns\n1,2').run()
        self.assertFalse(at.exception)
        self.assertTrue(at.error)

if __name__ == '__main__':
    unittest.main()
