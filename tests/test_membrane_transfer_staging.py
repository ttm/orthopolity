"""The transfer CLI must validate qualification and seals before decoding targets."""

import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments'))
SPEC = importlib.util.spec_from_file_location('membrane_transfer_staging',
                                             ROOT / 'experiments/run_membrane_transfer.py')
RUN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUN)


class MembraneTransferStaging(unittest.TestCase):
    def test_failed_qualification_never_decodes_targets(self):
        with tempfile.TemporaryDirectory() as temporary, \
                patch.object(sys, 'argv', ['runner', '--stage', 'evaluate',
                    '--freeze-commit', 'invented', '--output', temporary + '/output']), \
                patch.object(RUN, 'freeze', return_value='implementation'), \
                patch.object(RUN, 'checked_qualification', side_effect=ValueError('failed gate')), \
                patch.object(RUN, 'read_membrane_archive') as decoder:
            with self.assertRaisesRegex(ValueError, 'failed gate'):
                RUN.main()
            decoder.assert_not_called()

    def test_failed_forecast_seal_never_decodes_targets(self):
        with tempfile.TemporaryDirectory() as temporary, \
                patch.object(sys, 'argv', ['runner', '--stage', 'evaluate',
                    '--freeze-commit', 'invented', '--prediction-commit', 'seal',
                    '--predictions', temporary + '/predictions.json', '--output', temporary + '/output']), \
                patch.object(RUN, 'freeze', return_value='implementation'), \
                patch.object(RUN, 'checked_qualification', return_value=({'design_commit': 'design'}, b'{}')), \
                patch.object(RUN, 'ancestor'), \
                patch.object(RUN, 'checked_prediction', side_effect=ValueError('changed seal')), \
                patch.object(RUN, 'read_membrane_archive') as decoder:
            with self.assertRaisesRegex(ValueError, 'changed seal'):
                RUN.main()
            decoder.assert_not_called()

    def test_prediction_stage_uses_qualified_inputs_without_target_decoder(self):
        with tempfile.TemporaryDirectory() as temporary, \
                patch.object(sys, 'argv', ['runner', '--stage', 'predict',
                    '--freeze-commit', 'invented', '--output', temporary + '/output']), \
                patch.object(RUN, 'freeze', return_value='implementation'), \
                patch.object(RUN, 'checked_qualification', return_value=({'design_commit': 'design'}, b'{}')), \
                patch.object(RUN, 'ancestor'), \
                patch.object(RUN, 'prediction_document', return_value={'target_later_responses_decoded': False}), \
                patch.object(RUN, 'read_membrane_archive') as decoder, \
                contextlib.redirect_stdout(io.StringIO()):
            RUN.main()
            decoder.assert_not_called()
            self.assertTrue((Path(temporary) / 'output/predictions.json').is_file())

    def test_existing_output_prevents_evaluation(self):
        with tempfile.TemporaryDirectory() as temporary, \
                patch.object(sys, 'argv', ['runner', '--stage', 'evaluate',
                    '--freeze-commit', 'invented', '--output', temporary]), \
                patch.object(RUN, 'freeze', return_value='implementation'), \
                patch.object(RUN, 'checked_qualification', return_value=({'design_commit': 'design'}, b'{}')), \
                patch.object(RUN, 'ancestor'), \
                patch.object(RUN, 'read_membrane_archive') as decoder:
            with self.assertRaises(FileExistsError):
                RUN.main()
            decoder.assert_not_called()


if __name__ == '__main__':
    unittest.main()
