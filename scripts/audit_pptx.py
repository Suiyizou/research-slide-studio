"""Read-only PPTX object audit. Counts include children inside groups."""
import argparse,json,re
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

def audit(path):
 ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
     'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
     'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
 pages=[]; fonts=Counter()
 with ZipFile(path) as z:
  names=sorted((n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)),key=lambda n:int(re.search(r'(\d+)\.xml$',n).group(1)))
  for name in names:
   root=ET.fromstring(z.read(name))
   for tag in ['a:latin','a:ea','a:cs']:
    fonts.update(x.attrib.get('typeface','') for x in root.findall('.//'+tag,ns))
   row={'slide':int(re.search(r'(\d+)\.xml$',name).group(1))}
   for label,tag in [('shapes','p:sp'),('groups','p:grpSp'),('connectors','p:cxnSp'),('pictures','p:pic'),('charts','c:chart'),('tables','a:tbl')]:
    row[label]=len(root.findall('.//'+tag,ns))
   row['group_locks']=sum(x.attrib.get('noGrp') in ('1','true') for x in root.findall('.//a:spLocks',ns))
   pages.append(row)
 return {'file':str(Path(path).resolve()),'slide_count':len(pages),'totals':dict(sum((Counter({k:v for k,v in q.items() if k!='slide'}) for q in pages),Counter())),'fonts':dict(fonts),'pages':pages,'scope':'Package structure only; visual inspection remains required.'}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('pptx');p.add_argument('--output');a=p.parse_args()
 result=json.dumps(audit(a.pptx),ensure_ascii=False,indent=2)
 if a.output:Path(a.output).write_text(result,encoding='utf-8')
 else:print(result)
