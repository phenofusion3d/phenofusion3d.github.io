from pathlib import Path
O=Path(__file__).resolve().parent
p=O/'build_audit.py';s=p.read_text(encoding='utf-8')
try:s=s.encode('cp1252').decode('utf-8')
except (UnicodeEncodeError,UnicodeDecodeError):pass
p.write_text(s,encoding='utf-8')
p=O/'verify_audit.py';s=p.read_text(encoding='utf-8');s=s.replace("h=(O/'index.html').read_text()", "h=(O/'index.html').read_text(encoding='utf-8')");s=s.replace("(O/'index.html').write_text(h)","(O/'index.html').write_text(h,encoding='utf-8')");p.write_text(s,encoding='utf-8')
