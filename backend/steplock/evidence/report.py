import html
import json


def html_report(snapshot):
    safe=html.escape
    decision=snapshot["decision"]
    events="".join(f"<tr><td>{e['source_time_ms']/1000:.2f}s</td><td>{safe(e['kind'])}</td><td>{safe(e['reason'])}</td><td><code>{safe(e['frame_sha256'] or '')}</code></td></tr>" for e in snapshot["events"])
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>STEPLOCK evidence report</title>
    <style>body{{font:14px system-ui;margin:40px;color:#15202d}}h1{{letter-spacing:-2px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #bbc5d0;padding:8px;text-align:left}}code{{font-size:9px;overflow-wrap:anywhere}}@media print{{body{{margin:12px}}}}</style>
    <h1>STEPLOCK / EVIDENCE</h1><p>VISUAL PROCEDURE ASSURANCE · ADVISORY ONLY</p>
    <h2>{safe(decision['status'])}</h2><p>{safe(decision['reason'])}</p>
    <p>Source: {safe(snapshot['source_kind'])}. Recipe SHA-256: <code>{safe(snapshot['recipe_sha256'])}</code></p>
    <p>Source SHA-256: <code>{safe(snapshot['source_sha256'])}</code>. Hash kind: {safe(snapshot.get('source_hash_kind','FILE_BYTES'))}.</p>
    <p>Tag identity is not intrinsic part identity. No torque, fastening, industrial safety or fatigue validation.</p>
    <table><thead><tr><th>Source time</th><th>Event</th><th>Reason</th><th>Original PNG SHA-256</th></tr></thead><tbody>{events}</tbody></table>
    <p>JSON export contains exact support IDs, immutable event records, timestamps and runtime statistics. This report is an advisory demonstration record.</p></html>"""
