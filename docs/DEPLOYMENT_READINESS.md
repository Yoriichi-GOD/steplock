# Pre-launch deployment readiness

Date: 2026-11-01. **IMPLEMENTED_AND_CONTAINER_VERIFIED / AWS_NOT_DEPLOYED.**

The Industrial Requiem evolution is on branch `industrial-requiem`. New story,
motion helpers and self-hosted fonts are browser-side; they require no AWS GPU
or paid model. The one-container route/security architecture below is retained.
The earlier Linux receipt covers its named pre-launch commit, not automatically
this newer source. Current acceptance and any new container run are recorded in
`PRELAUNCH_ACCEPTANCE.md`. No AWS resource change is authorized by this design brief.
The latest brief authorizes preparation and testing, and reserves paid deployment,
cloud changes, domain purchase and public contact publication for explicit approval.
No AWS account API or resource mutation was performed for this pre-launch work.

## What is ready

The existing FastAPI process serves the production React build and all three
refreshable routes on one origin. `/demo` processes four checked-in, watermarked
generated videos with the original OpenCV/procedure/evidence engine. `/app` retains
the full workspace, gated by the backend in public mode. Anonymous visitors cannot
upload, capture a camera, edit recipes or invoke paid models. No email is configured.

The Linux image builds and completes actual HTTP inspections in GitHub Actions.
The verified image ID, source commit, test counts and run link are recorded in
[the Linux receipt](verification/prelaunch/linux-ci.json). A Docker image ID is
not a published ECR digest. An image has not been pushed to AWS.

The image runs as UID 10001 with one worker. Runtime files have a writable,
separate directory. Public frames expire after ten minutes; the server bounds
retention, replay duration, concurrent processing and POST bodies. Persistent
SQLite counters survive process restarts on the same disk. A replacement task
can reset them; WAF is required before opening arbitrary public access.

## Selected temporary hosting candidate

**Mumbai (`ap-south-1`), one ECS Express Mode service, 1 x86 vCPU / 2 GiB,
one task, a dedicated ALB and dedicated STEPLOCK networking.** HTTPS terminates
at the ALB; the application and API use the same AWS-provided HTTPS origin.
The public demo does not need a GPU, model credential, database service or camera.

Express Mode fits the existing long-running container and supplied HTTPS URL.
Static hosting alone cannot run the vision engine. A small VM can have lower
compute cost but adds host maintenance and a separate HTTPS solution. A serverless
rewrite would displace verification without improving this short trial. Express
Mode is the selected convenience tradeoff, not a claim of minimum possible cost.
[AWS describes the managed HTTPS service and underlying charges](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/express-service-overview.html).

Express Mode may share load balancers for matching network configurations.
**Do not use REFLEX's cluster, subnets, security groups, roles, logs, secrets or
load balancer.** Provision a separate STEPLOCK VPC/cluster and inventory the actual
managed resources before association or deletion. Keep the application at one task
and one worker: its session ownership and quotas are not distributed. Managed
rollouts can temporarily overlap revisions; stage updates behind restricted access
and expect temporary demo sessions to be lost. Scale-out is outside this release.

## Concrete preparation artifacts

- `infra/aws-steplock/express-service.request.json`: CLI request candidate, pinned
  resource size, one-task bounds, health path, port 8000 and safe environment.
  All `${...}` fields require reviewed values; no account identifiers are invented.
- `infra/aws-steplock/waf-web-acl.request.json`: initially closed staging ACL,
  approved test-IP allowlist, inspection-start and general request rate rules.
- `infra/aws-steplock/cost-estimate.json`: official regional price capture,
  assumptions, exclusions and trial planning allowance.
- `infra/aws-steplock/validation-receipt.json`: offline CLI schema outcomes.
- `infra/aws-steplock/README.md`: release, approval, domain and teardown sequence.

The initial request deliberately trusts loopback hostnames only. After creation,
read the actual AWS endpoint, add that exact hostname to `STEPLOCK_TRUSTED_HOSTS`
through a reviewed service update, then run hosted acceptance. Do not add `*`.
Only read-only `/api/health` accepts target-IP health-check hosts. Restrict inbound
container port 8000 to the dedicated ALB security group; no direct public task port.
Trust forwarded headers only from the dedicated ALB subnet ranges.

No owner key or Nebius secret is present in these requests. Owner access remains
disabled initially. A future owner key must use a new scoped backend secret,
never a frontend variable or image layer. Existing private credential files are
not copied. No IAM policy is generated or attached by this preparation.

## Costs and approval boundary

Official Mumbai rates captured on 2026-11-01 give **$0.09077/hour** for 1 vCPU,
2 GiB, one ALB and an assumed three public IPv4 addresses. This is a **fixed
subtotal**, excluding LCU usage, WAF, storage/builds, logs, data, tax and domain:

| Duration | Fixed subtotal, USD |
|---|---:|
| 24 hours | 2.18 |
| 48 hours | 4.36 |
| 7 days | 15.25 |
| 730 hours | 66.26 |

One sustained ALB capacity unit adds $0.008/hour. The published WAF pricing example
is $5/ACL-month, $1/rule-month and $0.60/million requests; fees are prorated hourly.
The candidate has three rules. Regional/account-specific billing still needs review.
[WAF pricing](https://aws.amazon.com/waf/pricing/), [public IPv4 pricing](https://aws.amazon.com/vpc/pricing/).
Exact Fargate/ALB price-list URLs and captured rates are in the cost JSON.

Use **$5–10 for a modest 24-hour trial**, or **$10–20 for 48 hours**, as planning
headroom only. These are neither AWS quotes nor hard spending caps. Many clients,
large downloads, repeated builds, unexpected infrastructure or delayed teardown can
exceed them. No NAT Gateway, paid model calls or trial credits are assumed.
Credit balance, expiry, covered services, tax and billing alerts are unverified.
Budget alerts notify; they do not enforce an immediate spending limit.

Before deployment the founder must approve the account, region, resource list,
trial duration/UTC expiry, cost allowance and teardown. Domain and email are
independent later choices. No paid service has been started to obtain that approval.

## Remaining hosted gates

1. Verify account identity, current credit coverage, quotas and current REFLEX
   baseline read-only. Record separate STEPLOCK role/network/resource ownership.
2. Build/publish the reviewed commit to a dedicated ECR repository; pin its actual
   registry digest. Re-run the container smoke against that image.
3. Replace request placeholders, review execution/infrastructure role permissions
   and validate against the target account. Offline shape checks do not prove IAM,
   region availability, subnet reachability, billing or service limits.
4. Create restricted staging only after approval. Attach the WAF ACL to the new
   STEPLOCK ALB, verify test-IP restriction, host allowlist, TLS and proxy behavior.
5. Run direct route, four-scenario/evidence, foreign-token, abuse, expiry, refresh,
   connection-loss, no-backend and viewport acceptance on the actual HTTPS origin.
   Verify public routes cannot reach owner APIs or model billing. Inspect logs for
   secrets, tokens, uploads and unexpected errors. Check memory/CPU under one run.
6. Confirm teardown ownership and scheduled expiry. Only after these pass should
   a separate reviewed WAF change open arbitrary public access. Preserve rate rules.

No factory deployment, physical-camera accuracy, external-video PASS or independent
security certification is established by these local/container checks.

## Local startup

From the repository root, with Python 3.14 and Node 24 available:

```powershell
$env:STEPLOCK_PUBLIC_MODE='1'
$env:ENABLE_NEBIUS_AGENT='0'
python scripts/dev.py --setup --port 62401
```

Open `http://127.0.0.1:62401/` or `/demo`. For the full private workspace, start
a separate terminal with `STEPLOCK_PUBLIC_MODE='0'`, a separate `STEPLOCK_RUNTIME`
directory, and port 62402; open `http://127.0.0.1:62402/app`. No cloud credential is
required. Subsequent startup can omit `--setup`. An already recognized server is
reused; an unrelated occupied port produces an explicit error.

```powershell
docker build -t steplock-prelaunch:local .
docker run --rm -p 127.0.0.1:8000:8000 steplock-prelaunch:local
python scripts/smoke_public_demo.py --origin http://127.0.0.1:8000
```

The installed local Docker Desktop could not initialize its existing inference
socket. Its state was left intact. Linux image verification ran in GitHub instead.
