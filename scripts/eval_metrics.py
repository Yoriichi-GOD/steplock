"""Evaluation-only calculations, imported nowhere in production inference."""
import math

CLASSES=("WRONG_COMPONENT","WRONG_ZONE","ORDER_VIOLATION","MISSING_AT_CHECKPOINT")


def rates(tp,fp,fn):
    precision=tp/(tp+fp) if tp+fp else None
    recall=tp/(tp+fn) if tp+fn else None
    f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None
    return {"tp":tp,"fp":fp,"fn":fn,"precision":precision,"recall":recall,"f1":f1}


def wilson(successes,total,z=1.96):
    if not total: return None
    p=successes/total
    center=(p+z*z/(2*total))/(1+z*z/total)
    radius=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/(1+z*z/total)
    return [max(0,center-radius),min(1,center+radius)]


def match_events(expected,predicted):
    predicted=[event for event in predicted if event["kind"] in CLASSES]
    used=set();matches=[];missed=[]
    for truth in sorted(expected,key=lambda e:e["onset_ms"]):
        options=[]
        for i,event in enumerate(predicted):
            if i in used or (event["kind"],event["part_id"],event["zone_id"])!=(truth["kind"],truth["part_id"],truth["zone_id"]): continue
            delta=event["source_time_ms"]-truth["onset_ms"]
            limit=200 if truth["kind"]=="MISSING_AT_CHECKPOINT" else 2000
            if -200<=delta<=limit: options.append((abs(delta),i,event))
        if options:
            _,i,event=min(options,key=lambda x:(x[0],x[1]))
            used.add(i)
            matches.append({"truth":truth,"event":event,"delay_ms":event["source_time_ms"]-truth["onset_ms"],
                            "timely":None if truth["boundary_ms"] is None else event["source_time_ms"]<=truth["boundary_ms"]})
        else: missed.append(truth)
    unmatched=[event for i,event in enumerate(predicted) if i not in used]
    return {"matches":matches,"missed":missed,"unmatched":unmatched,"tp":len(matches),"fp":len(unmatched),"fn":len(missed)}
