# AWS trial deployment - 2 November 2026

Status: **DEPLOYED_VERIFIED**. This is a short public prototype trial, not a
production or physical-validation certification.

- [Live landing page](https://st-a69b6c98718945778059ba5124767253.ecs.ap-southeast-2.on.aws)
- [Working inspection demo](https://st-a69b6c98718945778059ba5124767253.ecs.ap-southeast-2.on.aws/demo)
- [Hashed screenshots and redacted evidence](../screenshots/aws-trial-20261102/manifest.json)

The founder authorized seven days with a **USD 25 STEPLOCK operating allowance**.
Service teardown is scheduled for **9 November 2026, 00:53:05 IST**
(8 November, 19:23:05 UTC), with foundation cleanup 30 minutes later.
The allowance and schedule are not an instant billing hard cap. No plan upgrade,
domain purchase, contact address, owner credential or paid model call was added.

## Release provenance

The exact container source is
`c8577afaba7ed8b5474e697294829dc85e2eed1e`; its application is the independently
accepted `e773bef` implementation. This deployment changes infrastructure and
handoff evidence only. Historical evaluation reports, private media, unrelated
work and `day1-final` remain unchanged.

The immutable ECR image is pinned by digest:
`sha256:fe77c48ef879350c0cc83c2c26413c5413da97aafd3d11c9e164caab226d8447`
(260,008,570 bytes). The running task digest was checked against it.
AWS CodeBuild `2b34f050-bafb-40b9-99d6-9bc31e5a724f` succeeded after building
that exact commit and running all four actual-engine container examples.
[Infrastructure commit CI](https://github.com/Yoriichi-GOD/steplock/actions/runs/41342123976)
passed frontend checks/build, backend regression tests and Linux container smoke
for `eca2ceb31bc63881de1f7054c5cbfa150e5740e1`.

## Isolation and public boundary

The account organization policy denies Mumbai; the service is in Sydney
(`ap-southeast-2`). A separate STEPLOCK VPC, two public subnets, ECS cluster,
private immutable ECR repository, HTTPS load balancer, WAF, logs and roles were
created. Existing REFLEX configuration was read only; its service remained
`UPDATE_COMPLETE` at the same endpoint. No REFLEX resource was reused or changed.

One Linux x86 Fargate task uses 1 vCPU / 2 GiB and one application worker. There is
no NAT gateway, GPU, application AWS task role or model credential. Task port 8000
accepts traffic only from its dedicated load-balancer security group; no direct
public IPv4/IPv6 task ingress was found. Trusted hosts contain the exact endpoint
and loopback only, and forwarded proxy trust contains only the two ALB subnets.

HTTPS, HSTS (`max-age=86400`), frame denial and content-type protection passed.
The service was first restricted to the tester IP, then opened after hosted
acceptance. WAF now permits public access with rate blocks before the staging
allow rule: 20 inspection starts and 2,000 total requests per 300 seconds per IP.
These AWS rate controls are approximate. Sampled request capture is disabled.

Public mode permits the bundled generated examples only. Anonymous camera,
uploads, recipe editing, owner workbench APIs and cloud-model APIs are denied.
`/app` shows a restricted-workbench page. Contact is unconfigured. Temporary
sessions are process-local and may disappear on task replacement; only one
inspection can run at a time. This is a small review demo, not a multi-user SLA.

## Actual hosted verification

| Check | Observed result |
|---|---|
| Normal generated assembly | PASS / CHECKPOINT |
| Wrong component | HOLD_FOR_REVIEW / WRONG_COMPONENT |
| Wrong order | HOLD_FOR_REVIEW / ORDER_VIOLATION |
| Corrected assembly | PASS / CORRECTED |
| Evidence boundary | Own source frame available; foreign-session token returns 404 |
| Reset and refresh | DELETE 200; neutral PENDING, no retained green verdict |
| Private/model routes and hostile origin | 403 |
| Responsive landing and demo | No horizontal overflow at 1280x720, 390x844 and 320x740 |
| Actual source image style | `filter: none`, opacity 1; native screenshots retained |
| Stalled heartbeat after PASS | SOURCE LOST after 3,314 ms; no confirmed steps/green PASS |
| Reconnect | Actual session PASS restored before explicit reset |
| Clean startup with API blocked | PENDING and disabled Run button at 1280x720 |
| Browser console/request scope | No page errors or external origins in the primary test context |
| Public access from separate network | Landing/health 200; public mode true; private route 403 |

The final check ran from a separate CodeBuild egress IP outside the staging
allowlist (`a59ae223-7096-40f9-acdf-6232da2aff8b`, SUCCEEDED), without app
credentials. It proves public reachability rather than access by the tester alone.
An initial exact-host rollout briefly returned 400 while the old task was still
serving; after rollout completion the exact-host checks passed without changing
the application or permitting wildcard hosts.

One actual hosted browser run processed **30 frames / 10 events**, completing in
**7,847 ms**; its reported vision p95 was **44.1 ms**. These and the 3,314 ms
source-loss observation are single generated-example measurements, not a repeated
latency benchmark or physical-camera accuracy evidence. The four HTTP checks
reported zero provider calls. The browser checks use emulated phone viewports,
not a physical-phone performance test.

Final ECS state: one running / one desired / zero pending tasks. Container-level
health status was `UNKNOWN` (no container health check); HTTPS/ALB health and the
actual inspections passed. The last 30-minute CloudWatch window had 29 one-minute
samples, including rollout, idle and acceptance traffic: CPU mean 0.522%, peak
23.539%; memory mean 3.720%, peak 4.980%. This is not a sustained-load benchmark.
The application log search for `ERROR` or `Traceback` returned zero matching
events in the checked window; it is not proof of absence of all possible errors.

## Scheduled expiry and cost

`steplock-expiry` is deployed. Its Scheduler role can request deletion only of the
three exact trial/probe stack ARNs and pass the dedicated deletion role. That
deletion role is scoped to 21 inventoried STEPLOCK resource ARNs; IAM Access
Analyzer reported no policy validation errors. The universal Scheduler target
passes the deletion role explicitly, so future teardown does not depend on the
founder's interactive CLI session remaining signed in.

The live disposable log-group stack was automatically deleted through this path
at **2026-11-01 19:43:53 UTC** (`DELETE_COMPLETE`). This proves scheduled
invocation and scoped log-group deletion. It does **not** prove that future full
service/network deletion has already happened or cannot fail. The service
schedule is ENABLED for 8 November 19:23:05 UTC; foundation follows at 19:53:05.
Deletion and billing can be delayed. The small audit control stack, completed
schedules and IAM roles remain; no continuous compute is retained by that stack.

At retrieved Sydney rates, compute, the ALB hourly base and three assumed public
IPv4 addresses total USD 0.09940/hour, **USD 2.39/day or USD 16.70/seven days**.
WAF, ALB capacity units, traffic, builds, registry storage, logs and tax are extra.
This is an estimate, not a guaranteed bill or a new budget alarm. Trial credits
are shared with other account resources; no full-account credit balance is
published. Sources: official
[Fargate price list](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECS/current/ap-southeast-2/index.json),
[ALB price list](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSELB/current/ap-southeast-2/index.json),
[IPv4 pricing](https://aws.amazon.com/vpc/pricing/) and
[WAF pricing](https://aws.amazon.com/waf/pricing/).

## Remaining security and product limitations

The completed ECR basic OS-package scan found **0 critical, 15 high, 17 medium
and 5 low** findings. High findings affect libxml2, glibc, sqlite3 and zlib.
A fresh apt update/upgrade simulation in a disposable AWS build found only a
timezone-data update, with no available affected-package upgrades or held-back
packages. High findings remain unresolved; this image is not claimed clean or
security certified. This was not a complete application or exploitability audit.
Upstream examples: [libxml2 tracker](https://security-tracker.debian.org/tracker/CVE-2026-86140)
and [SQLite tracker](https://security-tracker.debian.org/tracker/CVE-2026-119586).

The public boundary limits exposure to controlled included video fixtures, no
anonymous uploads/camera, no app cloud keys and bounded sessions/request rates.
Those controls do not erase vulnerability findings. Before a longer-lived or
customer deployment, revisit the base image and scan, cost monitoring, persistent
session storage and operational monitoring. No custom domain or public contact
address is configured. This trial does not invoke Nebius/Tavily or establish a
verified real physical-assembly PASS. All hosted inspection results here are
explicitly **SYNTHETIC_FIXTURE**; existing physical-dataset limitations still apply.

## Definition of Done receipt

- [x] Exact-commit image build and four container inspections passed.
- [x] Isolated service, digest match, trusted host/proxy and security-group checks.
- [x] HTTPS public access verified outside the staging allowlist.
- [x] Hosted HTTP scenarios, evidence isolation and private/model boundary passed.
- [x] Responsive browser, unavailable-backend and stale-PASS checks passed.
- [x] Actual screenshots, measurements and hashes retained without account/IP data.
- [x] Enabled teardown schedule and live disposable deletion probe verified.
- [x] Existing CI/regression result recorded; no application changes in deployment.
- [x] REFLEX and frozen Day 1 history preserved.

Account-specific requests, resource ARNs, logs and inventories stay under ignored
`runtime/aws-deploy-20261102/`. The public evidence is an explicit redacted
allowlist, not a dump of that folder. Screenshot hashes/dimensions are in the
manifest. Reproduce hosted acceptance with
`python scripts/smoke_public_demo.py --origin <HTTPS endpoint>` and
`node infra/aws-steplock/hosted_browser_check.cjs <HTTPS endpoint>` after installing
Playwright and Chromium into the documented local `runtime/browser_qa` location.
