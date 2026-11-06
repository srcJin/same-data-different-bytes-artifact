"""Recompute paper tables and paired uncertainty from frozen selected outcomes.

This checks aggregation, not the original transcript-level grading.
No model, network or database calls are made.
"""
import csv, hashlib, json, random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ('faithful', 'altered', 'insufficient_evidence')
ARMS = ('A', 'B', 'C')


def reproduce():
    for entry in json.loads((ROOT/'provenance.json').read_text())['files']:
        assert hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest() == entry['sha256'], entry['path']
    with (ROOT/'data/trials.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    materials = sorted({r['material'] for r in rows})
    models = sorted({r['model'] for r in rows})
    assert len(rows) == 5832 and len(materials) == 36 and len(models) == 6
    assert len({r['trial_id'] for r in rows}) == len(rows)
    slots = {(r['material'], r['model'], r['repeat'], r['scenario'], r['arm']) for r in rows}
    assert len(slots) == len(rows)
    for m in materials:
        for model in models:
            for repeat in ('1', '2', '3'):
                for scenario in SCENARIOS:
                    for arm in ARMS:
                        assert (m, model, repeat, scenario, arm) in slots
    counts, totals = Counter(), Counter()
    by_material = Counter()
    model_counts, model_totals = Counter(), Counter()
    for row in rows:
        assert row['success'] in ('True', 'False')
        value = int(row['success'] == 'True')
        key = (row['scenario'], row['arm'])
        counts[key] += value
        totals[key] += 1
        by_material[row['material'], *key] += value
        model_counts[row['model'], *key] += value
        model_totals[row['model'], *key] += 1
    expected = json.loads((ROOT/'data/paper-results.json').read_text())['results']
    aggregate = []
    for scenario in SCENARIOS:
        for arm in ARMS:
            k = scenario, arm
            assert totals[k] == expected[scenario][arm]['n'] == 648
            assert counts[k] == expected[scenario][arm]['count']
            aggregate.append({'scenario':scenario, 'arm':arm, 'count':counts[k], 'n':totals[k], 'percent':counts[k]*100/totals[k]})
    # Match the recorded 100,000-resample material-cluster bootstrap exactly.
    frozen = json.loads((ROOT/'data/bootstrap-intervals.json').read_text())
    labels = [(s,a,b) for s in SCENARIOS for a,b in [('B','A'),('C','A'),('C','B')]]
    vectors = [[by_material[m,s,a]-by_material[m,s,b] for s,a,b in labels] for m in materials]
    samples = [[] for _ in labels]
    rng = random.Random(frozen['seed'])
    for _ in range(frozen['resamples']):
        summed = [0] * len(labels)
        for index in rng.choices(range(len(materials)), k=len(materials)):
            for j,value in enumerate(vectors[index]):
                summed[j] += value
        for j,value in enumerate(summed):
            samples[j].append(value*100/648)
    def quantile(values, p):
        loc = (len(values)-1)*p
        lo = int(loc)
        hi = min(lo+1,len(values)-1)
        return values[lo] + (loc-lo)*(values[hi]-values[lo])
    intervals=[]
    for j,(s,a,b) in enumerate(labels):
        values=sorted(samples[j])
        interval=[quantile(values, .025), quantile(values, .975)]
        point=(counts[s,a]-counts[s,b])*100/648
        published=next(r for r in frozen['results'] if r['scenario']==s and r['contrast']==a+'-'+b)
        assert abs(point-published['difference_pp']) < 1e-10
        assert all(abs(x-y)<1e-10 for x,y in zip(interval,published['ci95_percentile_pp']))
        intervals.append({'scenario':s,'contrast':a+'-'+b,'difference_pp':point,'ci95_pp':interval})
    out=ROOT/'build'
    out.mkdir(exist_ok=True)
    for name,records in [('table-ii.csv',aggregate),('bootstrap.csv',intervals),
                         ('table-iii.csv',[{'model':model,'scenario':s,'arm':a,'count':model_counts[model,s,a], 'n':model_totals[model,s,a], 'percent':model_counts[model,s,a]*100/model_totals[model,s,a]} for model in models for s in SCENARIOS for a in ARMS])]:
        with (out/name).open('w', newline='') as f:
            writer=csv.DictWriter(f, fieldnames=records[0].keys());writer.writeheader();writer.writerows(records)
    print('Verified 5,832 paired selected outcomes, 36 materials, 6 models, 3 repeats.')
    print('All Table II counts and all 9 recorded bootstrap contrasts match.')
    for s in SCENARIOS:
        print(s, ' / '.join(f'{a}: {counts[s,a]}/{totals[s,a]} ({100*counts[s,a]/totals[s,a]:.1f}%)' for a in ARMS))
    print('Wrote build/table-ii.csv, build/table-iii.csv and build/bootstrap.csv.')

if __name__ == '__main__':
    reproduce()
