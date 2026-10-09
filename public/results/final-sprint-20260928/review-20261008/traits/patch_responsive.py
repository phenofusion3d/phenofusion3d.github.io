from pathlib import Path
O=Path(__file__).resolve().parent
p=O/'build_audit.py';s=p.read_text()
s=s.replace("return '<table><thead><tr>'", "return '<div class=\"table-scroll\" role=\"region\" aria-label=\"Scrollable results table\" tabindex=\"0\"><table><thead><tr>'")
s=s.replace("+'</tbody></table>'", "+'</tbody></table></div>'")
s=s.replace('body{font:16px system-ui;', '*{box-sizing:border-box}html,body{min-width:0}body{font:16px system-ui;')
s=s.replace('table{border-collapse:collapse;width:100%;font-size:14px}', '.table-scroll{max-width:100%;width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch;margin:16px 0;outline-offset:3px}table{border-collapse:collapse;width:100%;min-width:620px;font-size:14px}')
s=s.replace('text-align:left}th{background:#dceaea}img{max-width:100%}', 'text-align:left;vertical-align:top;overflow-wrap:anywhere}td:last-child{min-width:160px}th{background:#dceaea}img{max-width:100%;height:auto}')
s=s.replace('a{color:#006675}</style>', 'a{color:#006675;overflow-wrap:anywhere}@media(max-width:650px){body{margin:20px auto;padding:0 14px}h1{font-size:1.8rem}.warn{padding:14px}td,th{padding:8px}section{min-width:0}}</style>')
p.write_text(s,encoding='utf-8')
