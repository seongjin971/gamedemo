"""Read actual Unity EXRs; report warm connected components without editing images."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / '.dream-loop/hdr-analysis'))
import OpenEXR
import numpy as np


def measure(folder):
    path = folder / 'reflection-linear-full.exr'
    with OpenEXR.File(str(path)) as source:
        channels = source.channels()
        rgb = channels.get('RGBA', channels.get('RGB')).pixels[:, :, :3]
    lum = rgb @ np.array([.2126, .7152, .0722])
    y, x = np.unravel_index(np.argmax(lum), lum.shape)
    native = json.loads((folder / 'reflection-radiance-full.json').read_text())
    orientation = 'bottom-origin' if y == native['peakY'] else 'top-origin' if y == lum.shape[0]-1-native['peakY'] else 'undetermined'
    mask = (lum > .5) & (rgb[:, :, 0] > rgb[:, :, 1]*1.2) & (rgb[:, :, 1] > rgb[:, :, 2]*1.5)
    visited = set()
    groups = []
    for py, px in zip(*np.nonzero(mask)):
        if (py, px) in visited:
            continue
        pending, component = [(py, px)], []
        visited.add((py, px))
        while pending:
            cy, cx = pending.pop()
            component.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy+dy, cx+dx
                    if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and (ny, nx) not in visited:
                        visited.add((ny, nx))
                        pending.append((ny, nx))
        ys, xs = np.array(component).T
        groups.append({'pixels': len(component), 'boundsXY': [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())], 'peakLuminance': float(lum[ys, xs].max()), 'sumLuminance': float(lum[ys, xs].sum())})
    return {'folder': folder.relative_to(ROOT).as_posix(), 'rowOrientation': orientation, 'peakXY': [int(x), int(y)], 'peakLuminance': float(lum[y, x]), 'warmComponents': sorted(groups, key=lambda g: -g['sumLuminance'])[:12], 'note': 'Actual linear reflection RT. Connected warm pixels are not automatically an identified emitter or visible water pixels; no main-camera blending, masking, tone map, or FPS inference.'}


if __name__ == '__main__':
    print(json.dumps([measure(ROOT / p) for p in sys.argv[1:]], indent=2))
