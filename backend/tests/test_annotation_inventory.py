import pytest
from scripts.acquire_annotations import parse_annotations


def test_headerless_annotation_first_row_is_not_discarded():
    rows=parse_annotations(b'0,10,attach,base,frame,correct,\n10,20,attach,cover,frame,wrong_order,"prior step missing, reviewed"\n')
    assert len(rows)==2
    assert rows[0]["label"]=="correct"
    assert rows[1]["remark"]=="prior step missing, reviewed"


def test_optional_header_and_malformed_schema():
    rows=parse_annotations(b'start,end,verb,this,that,label,remark\n0,10,attach,a,b,correct,\n')
    assert len(rows)==1
    with pytest.raises(ValueError): parse_annotations(b'not,a,valid,row\n')
