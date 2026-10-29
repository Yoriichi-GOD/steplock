import json
import httpx
import pytest
from steplock.agent.schemas import AgentConfig
from steplock.agent.nebius_client import NebiusClient,ProviderFailure


def config(**kw):
    return AgentConfig(enabled=True,api_key="unit-test-not-a-real-secret",**kw)


@pytest.mark.parametrize("status",[401,403,429,500,503,307])
def test_errors_never_retry_or_leak_key(status):
    calls=[]
    def response(request):
        calls.append(request)
        return httpx.Response(status,headers={"Retry-After":"120"},text="untrusted secret-like response body")
    client=NebiusClient(config(),httpx.MockTransport(response))
    with pytest.raises(ProviderFailure) as exc:client.complete([])
    assert len(calls)==1 and "secret" not in str(exc.value)
    assert exc.value.deferred==(status in [429,503])
    assert exc.value.retry_after=="120"


def test_real_contract_checks_served_model_and_records_actual_usage():
    cfg=config()
    def response(request):
        body=json.loads(request.content)
        assert body["model"]==cfg.model and body["max_tokens"]==1100
        assert body["chat_template_kwargs"]=={"enable_thinking":False}
        assert request.headers["authorization"]=="Bearer "+cfg.api_key
        return httpx.Response(200,headers={"x-request-id":"mock-id"},json={"model":cfg.model,"id":"mock-completion","choices":[{"finish_reason":"stop","message":{"content":"{}"}}],"usage":{"total_tokens":20}})
    result=NebiusClient(cfg,httpx.MockTransport(response)).complete([])
    assert result["served_model"]==cfg.model and result["usage"]["total_tokens"]==20
    assert cfg.api_key not in json.dumps(result)


@pytest.mark.parametrize("model,finish",[("meta-llama/other","stop"),(None,"stop"),("nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B","length")])
def test_mismatch_and_truncation_refuse_output(model,finish):
    client=NebiusClient(config(),httpx.MockTransport(lambda _:httpx.Response(200,json={"model":model,"choices":[{"finish_reason":finish,"message":{"content":"{}"}}]})))
    with pytest.raises(ProviderFailure):client.complete([])


def test_timeout_is_explicit_and_no_network_when_unconfigured():
    def timeout(_):raise httpx.ReadTimeout("private network detail")
    with pytest.raises(ProviderFailure,match="PROVIDER_TIMEOUT"):NebiusClient(config(),httpx.MockTransport(timeout)).complete([])
    with pytest.raises(ProviderFailure,match="NOT_CONFIGURED"):NebiusClient(AgentConfig(),httpx.MockTransport(timeout)).complete([])
    assert not config(base_url="https://attacker.example/v1").configured
    assert not config(model="meta-llama/other").configured
