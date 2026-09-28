#!/usr/bin/env python3
"""Run an actual resource recognizer on a local screenshot; no device is controlled."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from offline_controller import OfflineController
from maa.resource import Resource
from maa.tasker import Tasker
from maa.toolkit import Toolkit

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('image', type=Path)
    parser.add_argument('node')
    args = parser.parse_args()
    pipeline = json.loads((ROOT / 'assets/resource/pipeline/taobao_daily.json').read_text())
    if args.node not in pipeline:
        parser.error('Unknown node')
    Toolkit.init_option(str(ROOT / '.cache/image-check'))
    resource = Resource()
    assert resource.post_bundle(ROOT / 'assets/resource').wait().succeeded
    controller = OfflineController(np.array(Image.open(args.image).convert("RGB"))[:, :, ::-1].copy())
    controller.set_screenshot_target_short_side(720)
    assert controller.post_connection().wait().succeeded
    tasker = Tasker()
    tasker.bind(resource, controller)
    # Override EVERY action and transition so this command only recognizes one image.
    override = {name: {'action': 'DoNothing', 'next': [], 'on_error': [],
                       'pre_delay': 0, 'post_delay': 0} for name in pipeline}
    job = tasker.post_task(args.node, override).wait()
    detail = job.get()
    print(json.dumps({'node': args.node, 'matched': job.succeeded,
                      'executed': [node.name for node in detail.nodes]}, ensure_ascii=False))
    return 0 if job.succeeded else 1

if __name__ == '__main__':
    raise SystemExit(main())
