"""Check actual PPTX editability. SVG source files alone are not proof.

Exit 1 blocks structural acceptance. --plan verifies labels/object mappings.
--inventory is report-only and never certifies editability.
"""
import argparse
import json
import posixpath
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
R = '{' + NS['r'] + '}'
VECTOR_DETAIL_KINDS = ('dense_scatter', 'heatmap_cells', 'repeated_ticks', 'texture')


def norm(text):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', str(text)))


def local(tag):
    return tag.rsplit('}', 1)[-1]


def shape_name(node):
    prop = node.find('.//p:cNvPr', NS)
    return prop.get('name', '') if prop is not None else ''


def native_text(node):
    return ''.join(t.text or '' for t in node.findall('.//a:t', NS))


def visible(node):
    prop = node.find('.//p:cNvPr', NS)
    if prop is not None and prop.get('hidden') in ('1', 'true'):
        return False
    runs = node.findall('.//a:r', NS)
    return not runs or not all(r.find('.//a:alpha[@val="0"]', NS) is not None for r in runs)


def resolve_part(part, target):
    return target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(part), target))


def audit(path, plan_path=None, require_object_map=False):
    path = Path(path).resolve()
    errors, pages, fonts = [], [], Counter()
    plan, base = {}, path.parent
    if plan_path:
        base = Path(plan_path).resolve().parent
        plan = json.loads(Path(plan_path).read_text(encoding='utf-8-sig'))
    specs = {s['slide']: s for s in plan.get('slides', [])}
    if require_object_map and not plan_path:
        errors.append('Object-level validation requires --plan.')

    def fail(n, text):
        errors.append(f'Slide {n}: {text}')

    with ZipFile(path) as archive:
        names = set(archive.namelist())
        pres = ET.fromstring(archive.read('ppt/presentation.xml'))
        size = pres.find('p:sldSz', NS)
        sw, sh = int(size.get('cx')), int(size.get('cy'))
        slide_files = sorted((n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)), key=lambda n: int(re.search(r'(\d+)\.xml$', n)[1]))
        # Read presentation order rather than assuming slide filenames are ordered.
        if 'ppt/_rels/presentation.xml.rels' in names:
            rels = ET.fromstring(archive.read('ppt/_rels/presentation.xml.rels'))
            targets = {r.get('Id'): resolve_part('ppt/presentation.xml', r.get('Target', '')) for r in rels}
            ids = pres.findall('p:sldIdLst/p:sldId', NS)
            if ids:
                slide_files = [targets[s.get(R + 'id')] for s in ids]
        for n, name in enumerate(slide_files, 1):
            root = ET.fromstring(archive.read(name))
            spec = specs.get(n, {})
            rel_path = posixpath.join(posixpath.dirname(name), '_rels', posixpath.basename(name) + '.rels')
            rels = {r.get('Id'): r for r in ET.fromstring(archive.read(rel_path))} if rel_path in names else {}
            for tag in ('a:latin', 'a:ea', 'a:cs'):
                fonts.update(x.get('typeface', '') for x in root.findall('.//' + tag, NS))
            row = {'slide': n, 'part': name}
            for key, tag in [('shapes', 'p:sp'), ('groups', 'p:grpSp'), ('connectors', 'p:cxnSp'), ('pictures', 'p:pic'), ('charts', 'c:chart'), ('tables', 'a:tbl')]:
                row[key] = len(root.findall('.//' + tag, NS))
            row['group_locks'] = sum(x.get('noGrp') in ('1', 'true') for x in root.findall('.//a:spLocks', NS))
            shapes = root.findall('.//p:sp', NS)
            texts = [native_text(s) for s in shapes if visible(s) and native_text(s).strip()]
            texts += [native_text(c) for c in root.findall('.//a:tc', NS) if native_text(c).strip()]
            row.update(native_text_objects=len(texts), native_text_characters=sum(map(len, texts)), svg_pictures=0, svg_text_nodes=0, picture_details=[])
            allowed = {a.get('name'): a for a in spec.get('allowed_pictures', []) if isinstance(a, dict)}
            for pic in root.findall('.//p:pic', NS):
                pname = shape_name(pic)
                ext = pic.find('p:spPr/a:xfrm/a:ext', NS)
                fraction = int(ext.get('cx')) * int(ext.get('cy')) / (sw * sh) if ext is not None else None
                media = []
                for e in pic.iter():
                    rel = rels.get(e.get(R + 'embed') or e.get(R + 'link'))
                    if rel is not None and rel.get('TargetMode') != 'External':
                        media.append(resolve_part(name, rel.get('Target', '')))
                media = list(dict.fromkeys(media))
                svgs = [m for m in media if m.lower().endswith('.svg')]
                svg_texts, raster = 0, False
                for svg in svgs:
                    graphic = ET.fromstring(archive.read(svg))
                    svg_texts += sum(local(e.tag) == 'text' and bool(''.join(e.itertext()).strip()) for e in graphic.iter())
                    raster |= any(local(e.tag).lower() in ('image', 'feimage', 'foreignobject') for e in graphic.iter())
                row['svg_pictures'] += bool(svgs)
                row['svg_text_nodes'] += svg_texts
                row['picture_details'].append({'name': pname, 'media': media, 'slide_area_fraction': round(fraction, 4) if fraction is not None else None, 'svg_text_nodes': svg_texts, 'svg_contains_raster': raster})
                permit = allowed.get(pname, {})
                permitted = bool(permit.get('reason')) and permit.get('role') in ('user_cover', 'photo', 'source_image', 'vector_detail')
                vector_detail = (permitted and permit.get('role') == 'vector_detail'
                                 and permit.get('detail_kind') in VECTOR_DETAIL_KINDS)
                if permit and not permitted:
                    fail(n, f'Invalid allowed_pictures entry for {pname}; supply role and reason.')
                if permit.get('role') == 'vector_detail' and permit.get('detail_kind') not in VECTOR_DETAIL_KINDS:
                    fail(n, f'vector_detail {pname} requires detail_kind from {VECTOR_DETAIL_KINDS}; '
                         'small area or no text is insufficient. Main diagram components, cards, panels, '
                         'and arrows require native PowerPoint objects.')
                if svgs:
                    if svg_texts:
                        fail(n, f'SVG picture {pname} contains {svg_texts} text labels; these are not PowerPoint text boxes.')
                    if raster:
                        fail(n, f'SVG picture {pname} embeds raster/foreign content.')
                    if fraction is not None and fraction >= .50:
                        fail(n, f'SVG picture {pname} occupies {fraction:.0%} of the slide; split into semantic objects.')
                    if not (vector_detail and not svg_texts and not raster):
                        fail(n, f'SVG picture {pname} is one image object; rebuild native shapes or register a small text-free dense vector_detail.')
                elif not permitted or permit.get('role') == 'vector_detail':
                    fail(n, f'Picture {pname} lacks a source-image role; generated scientific graphics require vector reconstruction.')
            if row['pictures'] and not texts and not (spec.get('role') == 'cover' and allowed):
                fail(n, 'Picture-based page has no native editable text.')
            if spec.get('labels'):
                try:
                    data = json.loads((base / spec['labels']).read_text(encoding='utf-8-sig'))
                    labels = data if isinstance(data, list) else data['labels']
                    expected = [str(l['text']) for l in labels if str(l.get('text', '')).strip()]
                    if not expected and spec.get('generated_reference'):
                        fail(n, 'Generated page has an empty label layer.')
                    missing = [t for t in expected if not any(norm(t) in norm(a) for a in texts)]
                    row.update(expected_labels=len(expected), missing_native_labels=missing)
                    if missing:
                        fail(n, f'{len(missing)}/{len(expected)} labels missing from native text: {missing[:6]}')
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    fail(n, f'Cannot verify label layer: {exc}')
            elif require_object_map and spec.get('generated_reference'):
                fail(n, 'Generated page requires a labels file.')
            if spec.get('objects'):
                try:
                    data = json.loads((base / spec['objects']).read_text(encoding='utf-8-sig'))
                    objects = data if isinstance(data, list) else data['objects']
                    named = {}
                    for e in root.iter():
                        if local(e.tag) in ('sp', 'cxnSp', 'grpSp', 'pic', 'graphicFrame'):
                            named.setdefault(shape_name(e), []).append(e)
                    for obj in objects:
                        kind, targets = obj.get('kind'), obj.get('pptx_names', [])
                        if kind not in ('text', 'shape', 'connector', 'group', 'dense_detail', 'chart') or not targets:
                            fail(n, f'Object {obj.get("id")} needs valid kind and pptx_names.')
                            continue
                        for target in targets:
                            matches = named.get(target, [])
                            if len(matches) != 1:
                                fail(n, f'Object {obj.get("id")}: PPTX name {target!r} resolves to {len(matches)} objects.')
                                continue
                            e, tag = matches[0], local(matches[0].tag)
                            detail = allowed.get(target, {})
                            if tag == 'pic' and not (kind == 'dense_detail' and detail.get('role') == 'vector_detail'
                                                     and detail.get('detail_kind') in VECTOR_DETAIL_KINDS):
                                fail(n, f'Object {obj.get("id")} is a picture, not a native semantic object.')
                            if kind == 'text' and (tag != 'sp' or not native_text(e).strip() or not visible(e)):
                                fail(n, f'Text object {obj.get("id")} is not visible native text.')
                            if kind == 'shape' and (tag != 'sp' or not any(e.find('p:spPr/a:' + g, NS) is not None for g in ('custGeom', 'prstGeom'))):
                                fail(n, f'Shape {obj.get("id")} has no native geometry.')
                            if kind == 'group' and tag != 'grpSp':
                                fail(n, f'Group {obj.get("id")} is not a native group.')
                            if kind == 'connector' and tag not in ('sp', 'cxnSp'):
                                fail(n, f'Connector {obj.get("id")} is not a native line/path.')
                            if kind == 'chart' and e.find('.//c:chart', NS) is None:
                                fail(n, f'Chart {obj.get("id")} is not a native chart.')
                    if not objects:
                        fail(n, 'Object map is empty.')
                    row['mapped_objects'] = len(objects)
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    fail(n, f'Cannot verify semantic object map: {exc}')
            elif require_object_map and spec.get('generated_reference'):
                fail(n, 'Generated page requires an objects file mapping semantic IDs to actual PPTX shape names.')
            pages.append(row)
    if plan_path and plan.get('total_slides') != len(pages):
        errors.append('Plan and PPTX slide counts differ.')
    if plan_path and set(specs) != set(range(1, len(pages) + 1)):
        errors.append('Plan must list each slide exactly once.')
    keys = ('shapes', 'groups', 'connectors', 'pictures', 'charts', 'tables', 'group_locks', 'native_text_objects', 'native_text_characters', 'svg_pictures', 'svg_text_nodes')
    return {'ok': not errors, 'file': str(path), 'slide_count': len(pages), 'totals': {k: sum(p[k] for p in pages) for k in keys}, 'fonts': dict(fonts), 'pages': pages, 'errors': errors,
            'scope': 'Actual PPTX structure and declared labels/objects. Visual fidelity and real edit/save/reopen require PowerPoint checks.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('pptx'); p.add_argument('--plan'); p.add_argument('--require-object-map', action='store_true')
    p.add_argument('--output'); p.add_argument('--inventory', action='store_true')
    a = p.parse_args()
    try:
        result = audit(a.pptx, a.plan, a.require_object_map)
    except Exception as exc:
        result = {'ok': False, 'errors': [f'Cannot audit PPTX: {exc}']}
    if a.inventory:
        result.update(ok=None, validation_mode='inventory_only')
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if a.output:
        Path(a.output).write_text(output, encoding='utf-8')
        print(json.dumps({k: result[k] for k in ('ok', 'slide_count', 'totals') if k in result}, ensure_ascii=False))
    else:
        print(output)
    return 0 if a.inventory or result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
