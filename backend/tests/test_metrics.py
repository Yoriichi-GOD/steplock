import pytest
from scripts.eval_metrics import rates,wilson,match_events


def test_metric_denominators_and_zero_cases():
    assert rates(0,0,0)=={"tp":0,"fp":0,"fn":0,"precision":None,"recall":None,"f1":None}
    assert rates(2,1,2)["precision"]==pytest.approx(2/3)
    assert rates(2,1,2)["recall"]==.5
    assert rates(2,1,2)["f1"]==pytest.approx(4/7)
    assert rates(0,0,3)["precision"] is None
    assert rates(0,0,3)["f1"]==0
    assert wilson(0,0) is None
    assert wilson(4,4)[0]<1
    assert wilson(0,4)[1]>0


def test_one_to_one_matching_and_boundary():
    truth={"kind":"ORDER_VIOLATION","part_id":"COVER","zone_id":"COVER_SLOT","onset_ms":1000,"boundary_ms":1400}
    alert={"kind":"ORDER_VIOLATION","part_id":"COVER","zone_id":"COVER_SLOT","source_time_ms":1200}
    result=match_events([truth],[alert,alert])
    assert (result["tp"],result["fp"],result["fn"])==(1,1,0)
    assert result["matches"][0]["timely"]
    assert result["matches"][0]["delay_ms"]==200
    assert match_events([truth],[{**alert,"part_id":"BASE"}])["fn"]==1
    late=match_events([truth],[{**alert,"source_time_ms":1600}])
    assert not late["matches"][0]["timely"]
    assert match_events([truth],[{**alert,"source_time_ms":4000}])["fn"]==1
