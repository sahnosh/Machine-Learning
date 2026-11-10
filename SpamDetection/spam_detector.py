"""Offline English SMS classifier: download, train, evaluate and predict."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'SMSSpamCollection'
MODEL = ROOT / 'models' / 'spam_model.joblib'
URL = 'https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip'

def normalize(text):
    return re.sub(r'\s+', ' ', text).strip().casefold()

def download():
    if DATA.exists():
        return
    archive = ROOT / 'data' / 'sms_spam_collection.zip'
    if not archive.exists():
        with urllib.request.urlopen(URL, timeout=90) as response:
            payload = response.read()
        import io
        with zipfile.ZipFile(io.BytesIO(payload)) as check:
            check.getinfo('SMSSpamCollection')
        archive.write_bytes(payload)
    with zipfile.ZipFile(archive) as z:
        DATA.write_bytes(z.read('SMSSpamCollection'))
        (ROOT / 'data' / 'UCI_README.txt').write_bytes(z.read('readme'))
    print('Dataset downloaded:', DATA)

def load_data(path=DATA):
    groups = {}
    total = 0
    with Path(path).open(encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            label, text = line.rstrip('\r\n').split('\t', 1)
            if label not in ('ham', 'spam') or not text.strip():
                raise ValueError('Every data row must be: ham or spam, TAB, nonempty message')
            total += 1
            key = normalize(text)
            item = groups.setdefault(key, {'text': text, 'labels': set()})
            item['labels'].add(label)
    rows = [(v['text'], next(iter(v['labels']))) for v in groups.values() if len(v['labels']) == 1]
    if not rows:
        raise ValueError('No usable data')
    texts, labels = map(list, zip(*rows))
    return texts, labels, {'raw_rows': total, 'usable_unique_rows': len(rows),
        'removed_duplicate_or_conflicting_rows': total-len(rows)}

def train(path=DATA):
    import joblib
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
    texts, labels, stats = load_data(path)
    train_x, test_x, train_y, test_y = train_test_split(texts, labels, test_size=0.2,
        random_state=42, stratify=labels)
    pipeline = Pipeline([('tfidf', TfidfVectorizer(lowercase=True, ngram_range=(1,2), sublinear_tf=True)),
                         ('classifier', MultinomialNB(alpha=0.1))])
    pipeline.fit(train_x, train_y)
    predictions = pipeline.predict(test_x)
    report = {**stats, 'train_rows': len(train_x), 'test_rows': len(test_x),
        'class_counts': dict(Counter(labels)), 'random_seed': 42,
        'accuracy': accuracy_score(test_y, predictions),
        'classification_report': classification_report(test_y, predictions, output_dict=True, zero_division=0),
        'confusion_matrix_labels': ['ham','spam'],
        'confusion_matrix': confusion_matrix(test_y, predictions, labels=['ham','spam']).tolist(),
        'dataset_sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        'sklearn_version': sklearn.__version__, 'trained_utc': datetime.now(timezone.utc).isoformat(),
        'evaluation': 'Fixed stratified 80/20 holdout; normalized duplicates and conflicting groups removed before splitting. Vocabulary learned only on training data. Saved model is the evaluated training-split model.'}
    MODEL.parent.mkdir(exist_ok=True)
    (ROOT/'reports').mkdir(exist_ok=True)
    joblib.dump(pipeline, MODEL)
    (ROOT/'reports'/'metrics.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    with (ROOT/'reports'/'test_predictions.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer=csv.writer(f)
        writer.writerow(['message','actual','predicted'])
        writer.writerows(zip(test_x,test_y,predictions))
    summary=classification_report(test_y,predictions,zero_division=0)
    (ROOT/'reports'/'evaluation.txt').write_text(summary+'\n'+report['evaluation'],encoding='utf-8')
    print(summary)
    print('Saved model:', MODEL)
    return report

def load_model():
    import joblib
    if not MODEL.exists():
        raise FileNotFoundError('Model missing. Run train.cmd first.')
    return joblib.load(MODEL)  # Load only the local model created by this project.

def predict(text, model=None):
    if not text.strip():
        raise ValueError('Please enter a nonempty English message.')
    if not re.search('[A-Za-z]', text):
        raise ValueError('This model requires an English message.')
    model = load_model() if model is None else model
    if model.named_steps['tfidf'].transform([text]).nnz == 0:
        raise ValueError('No known vocabulary found. Enter a longer English message.')
    probability = model.predict_proba([text])[0]
    spam_index = list(model.classes_).index('spam')
    return {'label': str(model.predict([text])[0]), 'spam_score': float(probability[spam_index]),
            'note': 'Model score is not a calibrated probability; trained on English SMS.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('download')
    t=sub.add_parser('train')
    t.add_argument('--data',type=Path,default=DATA)
    p=sub.add_parser('predict')
    p.add_argument('text')
    args=parser.parse_args()
    try:
        if args.command=='download': download()
        elif args.command=='train':
            if args.data==DATA: download()
            train(args.data)
        else: print(json.dumps(predict(args.text),indent=2,ensure_ascii=False))
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        parser.exit(1,f'Error: {exc}\n')

if __name__=='__main__': main()
