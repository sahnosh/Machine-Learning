import unittest
import numpy as np
import pandas as pd
from segmentation import read_orders, build_rfm, segment, kmeans, csv_bytes
from generate_demo import generate

class SegmentationTests(unittest.TestCase):
    def test_cleaning_and_exact_rfm(self):
        content = b"customer_id,order_id,order_date,amount\n001,A,2026-10-01,10\n001,B,2026-10-05,20\n001,B,2026-10-05,20\n002,C,2026-10-03,5\n002,D,bad,3\n003,E,2026-10-02,-10\n"
        orders, audit = read_orders(content)
        self.assertEqual(audit, dict(input_rows=6, invalid_rows=2, duplicate_rows=1, valid_orders=3))
        rfm, ref = build_rfm(orders)
        row = rfm.set_index('customer_id').loc['001']
        self.assertEqual((row.Recency, row.Frequency, row.Monetary), (1, 2, 30))
        self.assertEqual(str(ref.date()), '2026-10-06')
        with self.assertRaises(ValueError):
            build_rfm(orders, '2026-09-01')

    def test_conflicting_order_and_invalid_schema(self):
        with self.assertRaises(ValueError):
            read_orders(b'customer_id,order_id,order_date,amount\nA,1,2026-01-01,3\nA,1,2026-01-01,4\n')
        for content in (b'', b'hello,world\n1,2', b'customer_id,order_id,order_date,amount\nA,1,invalid,3'):
            with self.assertRaises(ValueError):
                read_orders(content)

    def test_clusters_separate_known_blobs(self):
        rng = np.random.default_rng(7)
        x = np.concatenate([rng.normal(-5, .1, (30, 3)), rng.normal(5, .1, (30, 3))])
        _, labels, _ = kmeans(x, 2)
        self.assertEqual(len(set(labels[:30])), 1)
        self.assertEqual(len(set(labels[30:])), 1)
        self.assertNotEqual(labels[0], labels[-1])
        with self.assertRaises(ValueError):
            kmeans(np.zeros((10, 3)), 3)

    def test_demo_determinism_and_totals(self):
        orders, _ = read_orders(generate().to_csv(index=False).encode())
        rfm, _ = build_rfm(orders)
        a, summary, metrics = segment(rfm, 4)
        b, _, _ = segment(rfm, 4)
        pd.testing.assert_frame_equal(a, b)
        self.assertEqual(summary.Customers.sum(), 400)
        self.assertAlmostEqual(summary.Revenue.sum(), orders.amount.sum())
        self.assertTrue(-1 <= metrics['silhouette'] <= 1)
        self.assertEqual(a.Segment.nunique(), 4)

    def test_csv_formula_escaping(self):
        value = csv_bytes(pd.DataFrame({'customer_id':['=1+1','001']})).decode('utf-8-sig')
        self.assertIn("'=1+1", value)
        self.assertIn('001', value)

if __name__ == '__main__':
    unittest.main()
