"""One bounded provider request; retries belong to explicit operator actions."""
import json
import time
import httpx


class ProviderFailure(Exception):
    def __init__(self, code, deferred=False, retry_after=None, metadata=None):
        super().__init__(code)
        self.code, self.deferred, self.retry_after = code, deferred, retry_after
        self.metadata = metadata


class NebiusClient:
    def __init__(self, config, transport=None):
        self.config, self.transport = config, transport

    def complete(self, messages):
        if not self.config.configured:
            raise ProviderFailure("AGENT_NOT_CONFIGURED")
        started = time.perf_counter()
        try:
            with httpx.Client(transport=self.transport, timeout=httpx.Timeout(self.config.timeout_seconds, connect=5), follow_redirects=False) as client:
                response = client.post(self.config.base_url + "/chat/completions", headers={
                    "Authorization": "Bearer " + self.config.api_key, "Content-Type": "application/json"},
                    json={"model": self.config.model, "messages": messages, "temperature": 0,
                          "max_tokens": 1100, "response_format": {"type": "json_object"}})
            if response.status_code != 200:
                retry = response.headers.get("retry-after")
                # Defer rather than silently spend credits or ignore Retry-After.
                raise ProviderFailure(f"PROVIDER_HTTP_{response.status_code}", response.status_code in {429, 503}, retry[:80] if retry else None,
                                      {"http_status":response.status_code,"round_trip_ms":round((time.perf_counter()-started)*1000,3),"provider_request_id":response.headers.get("x-request-id"),"attempts":1,"retry_count":0})
            if len(response.content) > 65536:
                raise ProviderFailure("PROVIDER_RESPONSE_TOO_LARGE")
            data = response.json()
            if data.get("model") != self.config.model:
                raise ProviderFailure("SERVED_MODEL_MISMATCH")
            choice = data["choices"][0]
            if choice.get("finish_reason") != "stop":
                raise ProviderFailure("PROVIDER_OUTPUT_INCOMPLETE", metadata={"http_status":200,"served_model":data["model"],"completion_id":data.get("id"),"provider_request_id":response.headers.get("x-request-id"),"usage":data.get("usage"),"round_trip_ms":round((time.perf_counter()-started)*1000,3),"attempts":1,"retry_count":0})
            content = choice["message"]["content"]
            if not isinstance(content, str) or len(content) > 8000:
                raise ProviderFailure("INVALID_MODEL_CONTENT")
            return {"content": content, "served_model": data["model"], "completion_id": data.get("id"),
                    "provider_request_id": response.headers.get("x-request-id"), "usage": data.get("usage"),
                    "round_trip_ms": round((time.perf_counter() - started) * 1000, 3), "http_status": 200,
                    "attempts": 1, "retry_count": 0}
        except ProviderFailure:
            raise
        except httpx.TimeoutException as error:
            raise ProviderFailure("PROVIDER_TIMEOUT") from error
        except httpx.HTTPError as error:
            raise ProviderFailure("PROVIDER_NETWORK_ERROR") from error
        except (ValueError, KeyError, IndexError, TypeError) as error:
            raise ProviderFailure("PROVIDER_INVALID_RESPONSE") from error
