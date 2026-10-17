#!/usr/bin/env python3
"""Audit generated-reference coverage and vector reconstruction deliverables."""

import argparse
import hashlib
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def audit(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    base = manifest_path.parent
    errors = []
    try:
        plan = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError) as exc:
        return {'ok': False, 'errors': [f'Cannot read manifest: {exc}']}
    if not isinstance(plan, dict):
        return {'ok': False, 'errors': ['Manifest must be a JSON object.']}
    total = plan.get('total_slides')
    if type(total) is not int or total < 1:
        return {'ok': False, 'errors': ['total_slides must be a positive integer.']}

    def file_for(value, context):
        if not isinstance(value, str) or not value.strip():
            errors.append(f'{context}: supply a real file path.')
            return None
        path = (base / value).resolve()
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f'{context}: missing or empty file: {value}')
            return None
        return path

    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def image_for(value, context):
        path = file_for(value, context)
        if path:
            header = path.read_bytes()[:32]
            recognized = (header.startswith(b'\x89PNG\r\n\x1a\n') or
                          header.startswith(b'\xff\xd8\xff') or
                          (header.startswith(b'RIFF') and header[8:12] == b'WEBP') or
                          (header[4:8] == b'ftyp' and b'avif' in header))
            if not recognized:
                errors.append(f'{context}: supply an actual PNG/JPEG/WebP/AVIF image.')
                return None
        return path

    overviews = plan.get('overviews', [])
    if not isinstance(overviews, list):
        errors.append('overviews must be a list.')
        overviews = []
    if plan.get('new_visual_direction', True) is not False and len(overviews) != 4:
        errors.append('A new visual direction requires exactly four overview images.')
    overview_hashes = set()
    for index, item in enumerate(overviews, 1):
        path = image_for(item, f'Overview {index}')
        if path:
            key = digest(path)
            if key in overview_hashes:
                errors.append(f'Overview {index}: duplicate overview image.')
            overview_hashes.add(key)

    slides = plan.get('slides')
    if not isinstance(slides, list):
        return {'ok': False, 'errors': errors + ['slides must be a list.']}
    page_numbers = [s.get('slide') for s in slides if isinstance(s, dict)]
    if (len(page_numbers) != len(slides) or
            any(type(n) is not int for n in page_numbers) or
            len(slides) != total or set(page_numbers) != set(range(1, total + 1))):
        errors.append(f'slides must list each page from 1 to {total} exactly once.')

    reference_hashes = {}
    svg_count = 0
    covered = 0
    for row in slides:
        if not isinstance(row, dict):
            continue
        context = f'Slide {row.get("slide", "?")}'
        for key in ('role', 'message', 'visual_form'):
            if not isinstance(row.get(key), str) or not row[key].strip():
                errors.append(f'{context}: {key} is required.')
        uses_reference = row.get('generated_reference')
        if type(uses_reference) is not bool:
            errors.append(f'{context}: generated_reference must be true or false.')

        svg_file = None
        if uses_reference is True:
            if row.get('role') == 'cover':
                errors.append(f'{context}: cover images do not count as content references.')
            else:
                covered += 1
            reference = image_for(row.get('reference'), f'{context} reference')
            if reference:
                key = digest(reference)
                if key in overview_hashes:
                    errors.append(f'{context}: an overview cannot count as a page reference.')
                if key in reference_hashes:
                    errors.append(f'{context}: reference duplicates slide {reference_hashes[key]}.')
                reference_hashes[key] = row.get('slide')
            for key in ('prompt', 'labels'):
                file_for(row.get(key), f'{context} {key}')
            for key in ('comparison', 'overlay'):
                image_for(row.get(key), f'{context} {key}')
            if row.get('reviewed') is not True:
                errors.append(f'{context}: inspect the comparison and overlay, then set reviewed=true.')
            svg_file = file_for(row.get('svg'), f'{context} svg')
        elif row.get('svg'):
            svg_file = file_for(row['svg'], f'{context} svg')

        if svg_file:
            try:
                source = svg_file.read_text(encoding='utf-8-sig')
                root = ET.fromstring(source)
                names = [node.tag.rsplit('}', 1)[-1] for node in root.iter()
                         if isinstance(node.tag, str)]
                if root.tag.rsplit('}', 1)[-1] != 'svg':
                    errors.append(f'{context}: svg file has no SVG root.')
                prohibited = {'image', 'feimage', 'foreignobject'}
                if any(name.lower() in prohibited for name in names):
                    errors.append(f'{context}: SVG contains image/feImage/foreignObject; rebuild as vectors.')
                if re.search(r'data\s*:\s*image/', source, re.I):
                    errors.append(f'{context}: SVG embeds an image data URI.')
                if re.search(r'url\(\s*[\"\x27]?[^)#\s]+\.(?:png|jpe?g|webp|gif|avif)', source, re.I):
                    errors.append(f'{context}: SVG links a raster texture.')
                geometry = {'path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'use'}
                if not geometry.intersection(names):
                    errors.append(f'{context}: SVG contains no vector geometry.')
                svg_count += 1
            except (OSError, ValueError, ET.ParseError) as exc:
                errors.append(f'{context}: invalid SVG: {exc}')

    target = math.ceil(total * 0.5)
    if covered < target:
        errors.append(f'Coverage {covered}/{total}; provide at least {target} distinct page references.')
    return {
        'ok': not errors,
        'total_slides': total,
        'reference_target': target,
        'reference_pages': covered,
        'distinct_reference_files': len(reference_hashes),
        'svg_files_checked': svg_count,
        'errors': errors,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', help='Path to completed design-plan.json')
    args = parser.parse_args()
    result = audit(args.manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
