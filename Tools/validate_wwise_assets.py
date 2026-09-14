#!/usr/bin/env python3
"""Verify the saved Wwise project, generated banks and optional PCM output capture."""
import argparse
import array
import hashlib
import json
import math
import pathlib
import struct
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'Audio/VesperAudio'

def prop(node, name, default=None):
    value = node.find(f'PropertyList/Property[@Name="{name}"]')
    if value is None:
        return default
    return value.get('Value', value.findtext('ValueList/Value'))

def measure_capture(capture):
    data = capture.read_bytes()
    assert data[:4] == b'RIFF' and data[8:12] == b'WAVE', 'Expected a RIFF/WAVE capture'
    cursor, channels, rate, samples = 12, None, None, None
    while cursor + 8 <= len(data):
        tag, size = data[cursor:cursor+4], struct.unpack_from('<I', data, cursor+4)[0]
        assert cursor + 8 + size <= len(data), 'Truncated WAV chunk'
        chunk = data[cursor+8:cursor+8+size]
        cursor += 8 + size + (size % 2)
        if tag == b'fmt ':
            fmt, channels, rate, _, _, bits = struct.unpack_from('<HHIIHH', chunk)
            assert fmt in (1, 65534) and bits == 16 and channels > 0 and rate > 0
            if fmt == 65534:
                assert chunk[24:40] == bytes.fromhex('0100000000001000800000aa00389b71'), 'Expected PCM subformat'
        if tag == b'data':
            samples = array.array('h', chunk)
            if sys.byteorder != 'little':
                samples.byteswap()
    assert channels and rate and samples, 'Missing WAV format or empty audio data'
    peak = max(map(abs, samples)) / 32768
    rms = math.sqrt(sum(s*s for s in samples) / len(samples)) / 32768
    clipped = sum(abs(s) >= 32767 for s in samples)
    assert peak > .0001 and rms > .00001 and clipped == 0, 'Output must contain non-silent, unclipped audio'
    return {'channels': channels, 'sampleRate': rate, 'seconds': len(samples)/(channels*rate),
            'peakDbFS': 20*math.log10(peak), 'rmsDbFS': 20*math.log10(rms), 'clippedSamples': clipped}


def validate(capture=None, footstep_captures=None):
    tree = ET.parse(PROJECT / 'Containers/Vesper_W11.wwu')
    sounds = tree.findall('.//Sound')
    assert len(sounds) == 76
    for sound in sounds:
        sources = {s.get('ID'): s for s in sound.findall('ChildrenList/AudioFileSource')}
        active = sound.findall('ActiveSourceList/ActiveSource')
        assert len(sources) == len(active) == 1, sound.get('Name')
        relative = sources[active[0].get('ID')].findtext('AudioFile').replace('\\', '/')
        assert relative.startswith('Vesper_W11/')
        original = ROOT / 'sfx' / relative.removeprefix('Vesper_W11/')
        imported = PROJECT / 'Originals/SFX' / relative
        assert hashlib.sha256(original.read_bytes()).digest() == hashlib.sha256(imported.read_bytes()).digest(), relative
    foot = tree.find('.//SwitchContainer[@Name="Footsteps"]')
    pools = foot.findall('ChildrenList/RandomSequenceContainer')
    assert {p.get('Name') for p in pools} == {'Mud', 'Gravel', 'Snow', 'Rock'}
    assert all(prop(p, 'RandomOrSequence', '1') == '1' and prop(p, 'PlayMechanismStepOrContinuous', '1') == '1' for p in pools)
    assert all(prop(s, 'IsLoopingEnabled', 'False') == 'False' for s in foot.findall('.//Sound'))
    world = tree.find('.//SwitchContainer[@Name="World_Ambience"]')
    assert prop(world, 'SwitchBehavior') == '1'
    fades = world.findall('GroupingInfo/GroupingBehaviorList/GroupingBehavior')
    assert len(fades) == 2
    assert all(float(prop(f, 'FadeInTime')) == float(prop(f, 'FadeOutTime')) == 1.5 for f in fades)
    assert len(world.findall('.//RTPC')) >= 4
    lake = tree.find('.//RandomSequenceContainer[@Name="Lake_Ambience"]')
    assert prop(lake, '3DSpatialization') == '1'
    assert lake.find('ReferenceList/Reference[@Name="Attenuation"]/ObjectRef').get('Name') == 'Lake_40m'
    banks = {}
    for platform in ['Mac', 'Windows']:
        folder = ROOT / 'Unity/Vesper/Assets/StreamingAssets/Audio/GeneratedSoundBanks' / platform
        bank = json.loads((folder / 'Vesper_W11.json').read_text())['SoundBanksInfo']['SoundBanks'][0]
        assert {e['Name'] for e in bank['Events']} == {'Play_Footstep', 'Play_World_Ambience', 'Play_Lake_Ambience'}
        media = bank['Media']
        assert len(media) == 67 and all(m['Location'] == 'Memory' for m in media)
        assert all('thunder' not in m['ShortName'] and 'concreate' not in m['ShortName'] for m in media)
        assert (folder / 'Init.bnk').stat().st_size > 0
        banks[platform] = {'mediaCount': len(media), 'bytes': (folder / 'Vesper_W11.bnk').stat().st_size,
                           'sha256': hashlib.sha256((folder / 'Vesper_W11.bnk').read_bytes()).hexdigest()}
    report = {'sourceFilesVerified': len(sounds), 'footstepPools': 4, 'regionCrossfadeSeconds': 1.5, 'lakeMaxDistance': 40, 'banks': banks}
    if capture:
        report['outputSignal'] = measure_capture(capture)
    if footstep_captures:
        captures = {p.stem.rsplit('-', 1)[-1]: p for p in footstep_captures}
        assert len(footstep_captures) == 4 and set(captures) == {'Mud', 'Gravel', 'Snow', 'Rock'}
        report['isolatedFootsteps'] = {surface: measure_capture(path) for surface, path in sorted(captures.items())}
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=pathlib.Path)
    parser.add_argument('--footstep-captures', type=pathlib.Path, nargs='+')
    args = parser.parse_args()
    report = validate(args.capture, args.footstep_captures)
    (ROOT / 'Audio/output-signal-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
