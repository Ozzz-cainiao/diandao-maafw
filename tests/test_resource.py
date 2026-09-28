import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Registry, Resource as JsonResource
from scripts.offline_controller import OfflineController
from maa.custom_recognition import CustomRecognition
from maa.resource import Resource
from maa.tasker import Tasker
from maa.toolkit import Toolkit

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = json.loads((ROOT / 'assets/resource/pipeline/taobao_daily.json').read_text())

class ScriptedRecognition(CustomRecognition):
    """Synthetic recognition outcomes; exercises real engine transitions, NOT OCR accuracy."""
    def __init__(self, claim, confirm, stuck=False, coin_page=True):
        super().__init__()
        self.claim, self.confirm, self.stuck, self.coin_page = claim, confirm, stuck, coin_page

    def analyze(self, context, argv):
        name = argv.node_name
        hit = {'EnterCoins': True, 'CoinPage': self.coin_page,
               'ClaimOnce': self.claim, 'CheckClaimAbsent': self.stuck,
               'ConfirmClaimed': self.confirm, 'ReturnHome': self.stuck}.get(name, False)
        return (100, 100, 20, 20) if hit else None

class ResourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Toolkit.init_option(str(ROOT / '.cache/tests'))

    def test_official_schemas(self):
        directory = ROOT / '.cache/schema'
        registry = Registry()
        for path in directory.glob('*.json'):
            registry = registry.with_resource(path.as_uri(), JsonResource.from_contents(json.loads(path.read_text())))
        for name, data in [('interface', json.loads((ROOT / 'assets/interface.json').read_text())), ('pipeline', PIPELINE)]:
            path = directory / f'{name}.schema.json'
            schema = json.loads(path.read_text())
            schema['$id'] = path.as_uri()
            Draft202012Validator(schema, registry=registry).validate(data)

    def run_scenario(self, claim, confirm, stuck=False, coin_page=True):
        resource = Resource()
        self.assertTrue(resource.post_bundle(ROOT / 'assets/resource').wait().succeeded)
        recog = ScriptedRecognition(claim, confirm, stuck, coin_page)
        self.assertTrue(resource.register_custom_recognition('Scenario', recog))
        controller = OfflineController()
        self.assertTrue(controller.post_connection().wait().succeeded)
        tasker = Tasker()
        tasker.bind(resource, controller)
        override = {}
        for name in PIPELINE:
            override[name] = {'pre_delay': 0, 'post_delay': 0, 'timeout': 150, 'rate_limit': 20}
            if name != 'TaobaoDaily':
                override[name].update(recognition='Custom', custom_recognition='Scenario')
        job = tasker.post_task('TaobaoDaily', override).wait()
        names = [n.name for n in job.get().nodes if n.completed]
        return job.succeeded, names

    def test_new_claim_then_home(self):
        success, names = self.run_scenario(True, True)
        self.assertTrue(success)
        self.assertEqual(names.count('ClaimOnce'), 1)
        self.assertEqual(names[-1], 'ReturnHome')

    def test_already_claimed_no_click(self):
        success, names = self.run_scenario(False, True)
        self.assertTrue(success)
        self.assertNotIn('ClaimOnce', names)
        self.assertEqual(names[-1], 'ReturnHome')

    def test_unknown_result_no_home_or_retry(self):
        success, names = self.run_scenario(True, False)
        self.assertFalse(success)
        self.assertEqual(names.count('ClaimOnce'), 1)
        self.assertNotIn('ReturnHome', names)

    def test_button_still_present_no_home(self):
        success, names = self.run_scenario(True, True, stuck=True)
        self.assertFalse(success)
        self.assertEqual(names.count('ClaimOnce'), 1)
        self.assertNotIn('ReturnHome', names)

    def test_unknown_page_no_claim(self):
        success, names = self.run_scenario(True, True, coin_page=False)
        self.assertFalse(success)
        self.assertNotIn('ClaimOnce', names)
        self.assertNotIn('ReturnHome', names)

if __name__ == '__main__':
    unittest.main()
