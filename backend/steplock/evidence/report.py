import html
import json


def html_report(snapshot):
    safe=html.escape
    decision=snapshot["decision"]
    important={"WRONG_COMPONENT","WRONG_ZONE","ORDER_VIOLATION","HOLD_UNCERTAIN","CORRECTED","MISSING_AT_CHECKPOINT","CHECKPOINT","SOURCE_LOST"}
    selected=[event for event in snapshot["events"] if event["kind"] in important]
    # Printable one-page summary; the JSON export is the complete immutable ledger.
    selected=selected if len(selected)<=6 else selected[:2]+selected[-4:]
    events="".join(f"<tr><td>{e['source_time_ms']/1000:.2f}s</td><td>{safe(e['kind'])}</td><td>{safe(e['reason'])}</td><td><code>{safe((e['frame_sha256'] or '')[:16])}</code></td></tr>" for e in selected)
    steps="".join(f"<span>{safe(s['id'])} {safe(s['part'])}: <b>{safe(s['state'])}</b></span>" for s in snapshot["step_states"])
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>STEPLOCK evidence report</title>
    <style>@page{{size:A4;margin:13mm}}*{{box-sizing:border-box}}body{{font:11px/1.5 system-ui;margin:32px auto;color:#15202d;max-width:740px}}h1{{letter-spacing:-1.5px;font-size:27px;margin:0}}h2{{font-size:21px;margin:14px 0 5px}}p{{margin:8px 0}}table{{border-collapse:collapse;width:100%;font-size:9px;margin-top:16px}}td,th{{border:1px solid #bbc5d0;padding:6px;text-align:left;vertical-align:top}}code{{font-size:9px;overflow-wrap:anywhere}}.steps{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}}.steps span{{border:1px solid #bbc5d0;padding:5px;font-size:9px}}footer{{font-size:9px;border-top:1px solid #bbc5d0;margin-top:15px;padding-top:8px}}@media print{{body{{margin:0;max-width:none}}table,tr{{break-inside:avoid}}}}</style>
    <h1>STEPLOCK / EVIDENCE</h1><p>VISUAL PROCEDURE ASSURANCE · ADVISORY ONLY</p>
    <h2>{safe(decision['status'])}</h2><p>{safe(decision['reason'])}</p>
    <div class="steps">{steps}</div>
    <p>Source: {safe(snapshot['source_kind'])}. Recipe SHA-256: <code>{safe(snapshot['recipe_sha256'])}</code></p>
    <p>Source SHA-256: <code>{safe(snapshot['source_sha256'])}</code>. Hash kind: {safe(snapshot.get('source_hash_kind','FILE_BYTES'))}.</p>
    <p>Tag identity is not intrinsic part identity. No torque, fastening, industrial safety or fatigue validation.</p>
    <table><thead><tr><th>Time</th><th>Event</th><th>Reason</th><th>Frame hash prefix</th></tr></thead><tbody>{events}</tbody></table>
    <footer>Printable summary: {len(selected)} selected boundary/finding events of {len(snapshot['events'])} total ledger events. The complete JSON export preserves every event, full frame hash, support ID, timestamp and runtime statistic. No events were removed from that ledger. A frame-quality annotation describes perception; only the procedure summary above is the advisory decision.</footer></html>"""
