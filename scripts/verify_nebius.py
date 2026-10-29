"""Read-only authenticated model availability check; never logs credentials."""
import bootstrap
import json
import httpx
from steplock.agent.schemas import AgentConfig


def main():
    config=AgentConfig.from_env()
    if not config.configured:raise SystemExit('Set ENABLE_NEBIUS_AGENT=1 and a backend NEBIUS_API_KEY with an allowed endpoint and NVIDIA model.')
    try:
        with httpx.Client(timeout=15,follow_redirects=False) as client:
            response=client.get(config.base_url+'/models',headers={'Authorization':'Bearer '+config.api_key})
        if response.status_code!=200:raise SystemExit(f'Provider catalog HTTP {response.status_code}; no retries or model substitutions.')
        models=[row['id'] for row in response.json()['data']]
        if config.model not in models:raise SystemExit('Configured NVIDIA model not present in authenticated catalog.')
        print(json.dumps({'status':'CATALOG_VERIFIED','model':config.model,'provider':'Nebius Token Factory','inference_performed':False}))
    except httpx.HTTPError:raise SystemExit('Provider network check failed; key not logged.')


if __name__=='__main__':main()
