import csv
import hashlib
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

from orthopolity.speech_capacity import fit_models, predict, read_rows, score, weights


def synthetic(exponent=1):
    rows = []
    for lang, family, density in [('CAT','Indo-European',3),('ENG','Indo-European',5),('DEU','Indo-European',8)]:
        for speaker in ('1','2'):
            for text, count in [('a',80),('b',150)]:
                rows.append(dict(language=lang,family=family,speaker=lang+speaker,
                    text=text,ns=count,id=density,she=density+2,duration=count*density**exponent/35))
    return rows


class SpeechCapacity(unittest.TestCase):
    def test_two_noiseless_worlds_recover_and_discriminate(self):
        for exponent, winner, loser in [(1,'conditional','syllabic'),(0,'syllabic','conditional')]:
            train=synthetic(exponent); fits=fit_models(train)
            new=[dict(r,language='JPN',family='Japanese',id=10,duration=r['ns']*10**exponent/35)
                 for r in train[:4]]
            actual=np.log([r['duration'] for r in new])
            np.testing.assert_allclose(predict(winner,fits[winner],new),actual,atol=1e-12)
            self.assertGreater(np.mean(abs(predict(loser,fits[loser],new)-actual)),.2)

    def test_unconstrained_power_and_order(self):
        for exponent in [-.4,1.6]:
            rows=synthetic(exponent);fits=fit_models(rows)
            self.assertAlmostEqual(fits['power']['exponent'],exponent,places=12)
            np.testing.assert_allclose(predict('power',fits['power'],rows),np.log([r['duration'] for r in rows]),atol=1e-12)
            rev=fit_models(rows[::-1]);self.assertAlmostEqual(rev['power']['exponent'],exponent,places=12)

    def test_hierarchy_balances_missing_texts_and_families(self):
        rows=synthetic()[:3]
        rows += [dict(rows[0],language='JPN',family='Japanese',speaker='j',text='a')]
        w=weights(rows)
        np.testing.assert_allclose(w,[.125,.125,.25,.5])
        self.assertAlmostEqual(w.sum(),1)

    def test_mean_bias_and_individual_error_are_distinct(self):
        rows=synthetic()[:2]
        forecast=np.log([r['duration'] for r in rows])+np.array([.3,-.3])
        result=score(forecast,rows)
        self.assertAlmostEqual(result['family_balanced_language_log_mae'],0)
        self.assertAlmostEqual(result['family_balanced_reading_log_mae'],.3)

    def test_same_text_baseline_and_missing_coverage(self):
        rows=synthetic();fits=fit_models(rows)
        expected=np.mean([math.log(r['duration']) for r in rows if r['text']=='a'])
        self.assertAlmostEqual(fits['same_text']['log_duration_by_text']['a'],expected)
        with self.assertRaises(KeyError): predict('same_text',fits['same_text'],[dict(rows[0],text='missing')])

    def test_poisoned_targets_stay_unread(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'source.tsv'
            p.write_text('Speaker\tLanguage\tText\tNS\tID\tShE\tDuration\n'
                'e1\tENG\ta\t80\t5\t7\t10\n'
                'c1\tCAT\ta\t90\t6\t8\t12\n'
                'j1\tJPN\ta\t100\t4\t6\tWITHHELD\n')
            rows=read_rows(p,'calibration')
            self.assertNotIn('duration',rows[-1])
            fits=fit_models(rows[:2]);self.assertTrue(np.isfinite(predict('conditional',fits['conditional'],rows[-1:])).all())
            with self.assertRaises(ValueError): read_rows(p,'evaluation')
            p.write_text(p.read_text().replace('10\n','HIDDEN\n').replace('12\n','HIDDEN\n'))
            self.assertTrue(all('duration' not in r for r in read_rows(p)))

    def test_invalid_measurements_and_rank_stop(self):
        rows=synthetic();rows[0]['duration']=float('nan')
        with self.assertRaises(ValueError): fit_models(rows)
        rows=synthetic()
        for r in rows:r['id']=5
        with self.assertRaises(ValueError): fit_models(rows)

    def test_independent_verifier_masks_targets_and_rejects_tampering(self):
        root=Path(__file__).resolve().parents[1]
        spec=importlib.util.spec_from_file_location('speech_verifier',root/'experiments/verify_speech_capacity.py')
        verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'source.tsv'
            rows=synthetic(.7)
            target=[dict(r,language='JPN',family='Japanese',speaker='j'+r['speaker'],id=4) for r in rows[:4]]
            with p.open('w',newline='') as f:
                writer=csv.writer(f,delimiter='\t',lineterminator='\n')
                writer.writerow(['Speaker','Language','Text','NS','ID','ShE','Duration'])
                for i,r in enumerate(rows+target):
                    duration=r['duration']*math.exp((i%3)*.02) if i<len(rows) else 'WITHHELD'
                    writer.writerow([r['speaker'],r['language'],r['text'],r['ns'],r['id'],r['she'],duration])
            parsed=read_rows(p,'calibration');training=parsed[:len(rows)];targets=parsed[len(rows):]
            fits=fit_models(training)
            for model,fit in fits.items():
                fit['log_forecasts']=predict(model,fit,targets).tolist()
                fit['calibration_score']=score(predict(model,fit,training),training)
            cfg=dict(source=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                     expected_rows=len(parsed),study='synthetic')
            forecasts=dict(config=cfg,study='synthetic',training=training,targets=targets,fits=fits,
                           target_numerical_durations_decoded=False,calibration_id_range=[3.,8.],
                           target_languages_outside_id_support=[])
            checked=verifier.verify(forecasts)
            self.assertGreater(checked['numeric_checks'],100)
            self.assertFalse(checked['target_numerical_durations_decoded'])
            fits['conditional']['log_forecasts'][0]+=.01
            with self.assertRaises(ValueError): verifier.verify(forecasts)


if __name__=='__main__': unittest.main()
