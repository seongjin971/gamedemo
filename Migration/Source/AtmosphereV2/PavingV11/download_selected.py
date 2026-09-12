"""Download only the approved research selection; never modifies Unity or V10."""
import datetime, hashlib, json, pathlib, urllib.request, zipfile

ROOT = pathlib.Path(__file__).resolve().parent
AGENT = 'VESPER-PavingV11-AssetResearch/1.0'
API = 'https://ambientcg.com/api/v2/full_json?id=Tiles130&include=downloadData,displayData,dimensionsData,imageData,tagData'

def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read(), response.url

def main():
    raw, _ = fetch(API)
    data = json.loads(raw)
    asset = next(a for a in data['foundAssets'] if a['assetId'] == 'Tiles130')
    downloads = asset['downloadFolders']['default']['downloadFiletypeCategories']['zip']['downloads']
    selected = next(d for d in downloads if d['attribute'] == '4K-PNG')
    source = ROOT / 'source'; source.mkdir(exist_ok=True)
    (source / 'Tiles130-api.json').write_bytes(raw)
    archive = source / selected['fileName']
    if not archive.exists():
        payload, final_url = fetch(selected['downloadLink'])
        archive.write_bytes(payload)
    else:
        final_url = 'existing local archive; see original source URL'
    assert archive.stat().st_size == selected['size'], 'API size mismatch'
    maps = ROOT / 'maps'; maps.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for item in z.infolist():
            destination = (maps / item.filename).resolve()
            assert destination.is_relative_to(maps.resolve()), 'unsafe archive path'
        z.extractall(maps)
    entries = []
    for p in sorted([archive] + list(maps.rglob('*'))):
        if p.is_file():
            b = p.read_bytes()
            entry = {'path': p.relative_to(ROOT).as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}
            if p.suffix == '.png':
                import struct
                w,h,depth,color = struct.unpack('>IIBB',b[16:26])
                entry.update(width=w,height=h,png_bit_depth=depth,png_color_type=color)
            entries.append(entry)
    manifest = {'asset_id':'Tiles130','provider':'ambientCG','asset_url':asset['shortLink'],
        'license':'CC0-1.0','license_url':'https://docs.ambientcg.com/license/',
        'creation_method':asset['creationMethod'],'method_description':asset['creationMethodDescription'],
        'api_url':API,'download_url':selected['downloadLink'],'resolved_download_url':final_url,
        'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source_dimensions_m':[2.3,1.15],'dimension_source':'https://ambientcg.com/view?id=Tiles130',
        'vertical_physical_scale_m':None,'vertical_scale_note':'API dimensionZ=0; no calibrated height amplitude supplied.',
        'archive_size_matches_api':True,'zip_crc_verified':True,
        'provider_hash_available':False,'bytes_modified':False,'files':entries}
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    print(json.dumps(manifest,indent=2))

if __name__ == '__main__': main()
