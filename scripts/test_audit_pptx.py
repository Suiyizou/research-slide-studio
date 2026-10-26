"""Regression checks for failures observed in the two October 2026 decks."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from audit_pptx import audit, NS
from audit_design import audit as audit_design


class EditabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write_json(self, name, value):
        path = self.root / name
        path.write_text(json.dumps(value), encoding='utf-8')
        return path

    def deck(self, *, text='Title', hidden=False, picture=None, size=1000):
        shape = (f'<p:sp><p:nvSpPr><p:cNvPr id="2" name="label" hidden="{int(hidden)}"/>'
                 '<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:prstGeom prst="rect"/>'
                 f'</p:spPr><p:txBody><a:bodyPr/><a:p><a:r><a:t>{text}</a:t>'
                 '</a:r></a:p></p:txBody></p:sp>') if text else ''
        rel = ''
        if picture:
            ext, payload = picture
            shape += (f'<p:pic><p:nvPicPr><p:cNvPr id="3" name="detail"/></p:nvPicPr>'
                      '<p:blipFill><a:blip r:embed="rId1"/></p:blipFill>'
                      f'<p:spPr><a:xfrm><a:ext cx="{size}" cy="{size}"/></a:xfrm></p:spPr></p:pic>')
            rel = f'<Relationship Id="rId1" Target="../media/detail.{ext}"/>'
        ppt = self.root / 'test.pptx'
        with ZipFile(ppt, 'w') as z:
            z.writestr('ppt/presentation.xml', f'<p:presentation xmlns:p="{NS["p"]}"><p:sldSz cx="1000" cy="1000"/></p:presentation>')
            namespaces = ' '.join(f'xmlns:{k}="{v}"' for k, v in NS.items())
            z.writestr('ppt/slides/slide1.xml', f'<p:sld {namespaces}><p:cSld><p:spTree>{shape}</p:spTree></p:cSld></p:sld>')
            z.writestr('ppt/slides/_rels/slide1.xml.rels', f'<Relationships>{rel}</Relationships>')
            if picture:
                z.writestr(f'ppt/media/detail.{ext}', payload)
        return ppt

    def plan(self, labels=None, objects=None, allowed=None, role='content', generated=True, detail_kind=None):
        row = {'slide': 1, 'role': role, 'generated_reference': generated}
        if labels is not None:
            self.write_json('labels.json', {'labels': [{'text': t} for t in labels]})
            row['labels'] = 'labels.json'
        if objects is not None:
            self.write_json('objects.json', {'objects': objects})
            row['objects'] = 'objects.json'
        if allowed:
            row['allowed_pictures'] = [{'name': 'detail', 'role': allowed, 'reason': 'Explicitly declared source/detail'}]
            if detail_kind is not None:
                row['allowed_pictures'][0]['detail_kind'] = detail_kind
        return self.write_json('plan.json', {'total_slides': 1, 'slides': [row]})

    def test_native_text_and_object_mapping_pass(self):
        plan = self.plan(['Title'], [{'id': 'title', 'kind': 'text', 'pptx_names': ['label']}])
        self.assertTrue(audit(self.deck(), plan, True)['ok'])

    def test_whole_svg_with_title_overlay_fails(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><text>Body</text></svg>'
        report = audit(self.deck(picture=('svg', svg)))
        self.assertFalse(report['ok'])
        self.assertEqual(report['totals']['native_text_objects'], 1)
        self.assertEqual(report['totals']['svg_text_nodes'], 1)

    def test_outlined_whole_svg_cannot_use_detail_exception(self):
        plan = self.plan(allowed='vector_detail', detail_kind='dense_scatter')
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0L2 2"/></svg>'
        report = audit(self.deck(picture=('svg', svg)), plan)
        self.assertTrue(any('occupies' in e for e in report['errors']))

    def test_small_text_free_svg_detail_passes(self):
        details = {
            'dense_scatter': '<circle cx="1" cy="1" r=".2"/><circle cx="2" cy="2" r=".2"/>',
            'heatmap_cells': '<rect width="1" height="1"/><rect x="1" width="1" height="1"/>',
            'repeated_ticks': '<path d="M0 0V1 M1 0V1 M2 0V1"/>',
            'texture': '<path d="M0 0L2 2 M1 0L3 2"/>',
        }
        for detail_kind, body in details.items():
            with self.subTest(detail_kind=detail_kind):
                plan = self.plan(['Title'], [{'id': 'points', 'kind': 'dense_detail', 'pptx_names': ['detail']}],
                                 allowed='vector_detail', detail_kind=detail_kind)
                svg = f'<svg xmlns="http://www.w3.org/2000/svg">{body}</svg>'
                self.assertTrue(audit(self.deck(picture=('svg', svg), size=100), plan, True)['ok'])

    def test_small_text_free_svg_requires_detail_kind(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10"/></svg>'
        report = audit(self.deck(picture=('svg', svg), size=100), self.plan(allowed='vector_detail'))
        self.assertFalse(report['ok'])
        self.assertTrue(any('requires detail_kind' in e and 'small area or no text is insufficient' in e
                            for e in report['errors']))

    def test_main_components_cannot_be_declared_as_vector_details(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10"/></svg>'
        for detail_kind in ('card', 'panel', 'diagram', 'arrow'):
            with self.subTest(detail_kind=detail_kind):
                plan = self.plan(['Title'], [{'id': 'component', 'kind': 'dense_detail', 'pptx_names': ['detail']}],
                                 allowed='vector_detail', detail_kind=detail_kind)
                report = audit(self.deck(picture=('svg', svg), size=100), plan, True)
                self.assertFalse(report['ok'])
                self.assertTrue(any('requires detail_kind' in e for e in report['errors']))
                self.assertTrue(any('not a native semantic object' in e for e in report['errors']))

    def test_missing_body_label_fails(self):
        report = audit(self.deck(), self.plan(['Title', 'Body']))
        self.assertEqual(report['pages'][0]['missing_native_labels'], ['Body'])
        self.assertFalse(report['ok'])

    def test_hidden_text_does_not_satisfy_label_layer(self):
        self.assertFalse(audit(self.deck(hidden=True), self.plan(['Title']))['ok'])

    def test_unknown_object_name_fails(self):
        plan = self.plan(['Title'], [{'id': 'node', 'kind': 'shape', 'pptx_names': ['absent']}])
        self.assertFalse(audit(self.deck(), plan, True)['ok'])

    def test_raster_is_not_vector_detail(self):
        self.assertFalse(audit(self.deck(picture=('png', b'png')),
                               self.plan(allowed='vector_detail', detail_kind='dense_scatter'))['ok'])

    def test_declared_user_cover_is_allowed(self):
        plan = self.plan(allowed='user_cover', role='cover', generated=False)
        self.assertTrue(audit(self.deck(text='', picture=('png', b'png')), plan)['ok'])

    def test_final_design_audit_inspects_pptx(self):
        report = audit_design(self.plan(), self.deck(picture=('svg', '<svg><text>Body</text></svg>')))
        self.assertTrue(report['final_pptx_checked'])
        self.assertEqual(report['scope'], 'final_pptx_and_design')
        self.assertTrue(any('not PowerPoint text boxes' in e for e in report['errors']))


if __name__ == '__main__':
    unittest.main()
