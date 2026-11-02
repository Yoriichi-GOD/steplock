# Independent STEPLOCK AWS trial

**Deployed and checked on 2 November:** see [the live deployment receipt](../../docs/AWS_DEPLOYMENT_20261102.md)
for the endpoint, immutable image, hosted acceptance, security findings and scheduled
expiry. `foundation.yaml`, `service.yaml` and `expiry.yaml` describe that trial;
`hosted_browser_check.cjs` records its reproducible browser checks.

The [custom-domain receipt](../../docs/DOMAIN_SETUP_20261102.md) covers the
verified `www.step-lock.xyz` hostname and GoDaddy root-forwarding limitations.
`CustomDomain` adds a DNS-validated, non-exportable ACM certificate and SNI
binding to this same trial stack. Add the exact hostname to `TrustedHosts` too.
GoDaddy retains DNS ownership. After any Express service update, verify the
managed listener rule still includes the AWS hostname and custom hostname;
the documented direct host-rule customization is outside the Express template.

The section below preserves the **historical 1 November preparation snapshot**;
its NOT_DEPLOYED wording does not describe the current trial.

**NOT_DEPLOYED.** Prepared 2026-11-01 for a short, separately approved AWS trial.
No AWS account API, resource creation, existing-resource update, image publication,
domain change or paid inference was performed in this pre-launch implementation.
Earlier REFLEX preflight results are historical snapshots, not checks repeated today.
REFLEX source and infrastructure were left alone.

See [readiness and costs](../../docs/DEPLOYMENT_READINESS.md),
[test receipt](../../docs/PRELAUNCH_TEST_RECEIPT.md) and
[public contract](../../docs/PUBLIC_DEMO.md).

## Candidate and verified scope

One same-origin Linux container: landing `/`, restricted generated-example
`/demo`, owner-only `/app`, API `/api`. Agent disabled, no owner key, no email.
Use one task/one application worker. Session state is process-local; replacing a
task may discard sessions and reset disk counters. WAF is required before public access.

Candidate: ECS Express Mode in Mumbai, x86 Linux, 1 vCPU / 2 GiB, with a dedicated
STEPLOCK VPC/cluster/ALB. It provides an AWS HTTPS URL without buying a domain.
Express Mode can share ALBs for matching network configurations, so do not reuse
REFLEX networking. This is a convenience tradeoff, not minimum possible cost.

The Linux production image and four actual container inspections passed in
[run 41296194824](https://github.com/Yoriichi-GOD/steplock/actions/runs/41296194824).
The image ID/source commit are in `docs/verification/prelaunch/linux-ci.json`.
That ID is not a published ECR digest. Local Docker Desktop failed to initialize
its existing inference socket; its data was left intact.

## Prepared requests

`express-service.request.json` fixes port 8000, CPU 1024 units, memory 2048 MiB,
x86, health path and min/max task count 1. Its initial trusted hosts are loopback
only; later add the actual AWS endpoint explicitly. Never use wildcard hosts.
All `${...}` values are unresolved inputs:

| Input | Required source |
|---|---|
| Cluster and two subnets | New dedicated STEPLOCK VPC/cluster, separate from REFLEX |
| Execution/infrastructure roles | New reviewed STEPLOCK roles; no unrelated role reuse |
| Container image | Reviewed ECR image at its actual registry SHA-256 digest |
| Proxy ranges | Dedicated ALB subnet CIDRs, not all callers |
| Teardown time | User-approved UTC end of trial |

No application task role or model credential is needed for baseline inspection.
No IAM policy or role is generated/attached here. Review permissions in the target
account using the [official role/service instructions](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/express-service-getting-started.html).

`waf-web-acl.request.json` starts default BLOCK, allows only a new STEPLOCK test
IPv4 IP set, and applies rate blocks before that allow rule: 20 inspection starts
and 2,000 total requests per five minutes per IP. WAF rate limits are approximate,
not hard cost caps. Sampled request capture is disabled.

ECS offline AWS CLI 2.38.5 schema generation passed without contacting AWS.
WAF output-skeleton generation failed on its locally generated `Summary.ARN`
stub (length 3, minimum 20). This is blocked, not a passing WAF validation.
See `validation-receipt.json`. No CloudFormation stack, IAM policy, service
permissions or network reachability is claimed as validated.

## Local production check

```powershell
docker build -t steplock-prelaunch:local .
docker run --rm -p 127.0.0.1:8000:8000 steplock-prelaunch:local
python scripts/smoke_public_demo.py --origin http://127.0.0.1:8000
```

The non-root image excludes credentials, licensed private research media, runtime
evidence and unrelated projects. Its public demo contains generated fixtures only.

## Deployment sequence — not executed

1. Approve account, region, duration/UTC expiry, resource inventory and cost
   allowance. Verify actual trial credits, expiry and covered services. Nebius
   credits do not establish AWS coverage.
2. Record REFLEX health/inventory read-only. Create only new STEPLOCK resources:
   dedicated ECR repository, reviewed roles, VPC/public subnets/cluster and short
   retention log group. Avoid a NAT Gateway for this explicitly priced candidate.
   Restrict task port 8000 to the dedicated ALB security group.
3. Publish the reviewed image and record its ECR digest. Replace every request
   placeholder; review role permissions and validate in the target account.
   The approved creation operation is `aws ecs create-express-gateway-service
   --region ap-south-1 --cli-input-json file://runtime/steplock-approved-service.json`.
   Never pass the unresolved checked-in candidate to deployment.
4. Inventory every managed resource. Create and capacity-check the new test-IP
   WAF ACL; associate it only with the new STEPLOCK ALB. Verify test-IP restriction
   before configuring the normal public hostname.
5. Read the actual HTTPS endpoint, then update only this service's trusted hosts.
   Verify narrow proxy ranges, HTTPS-aware Secure cookies/HSTS and target health.
   Only read-only health checks may bypass host matching for target-IP probes.
6. Run all hosted gates in DEPLOYMENT_READINESS: routes, four real engine replays,
   evidence isolation, denied private/model APIs, limits/expiry, source loss,
   direct refresh and viewports. Inspect CPU/memory, measured latency and logs.
7. Recheck REFLEX read-only, confirm teardown inventory/expiry, then review a
   separate WAF change to open public access while retaining both rate rules.
   Claim a live service only after independently verifying its actual endpoint.

## Cost and domain

Official Mumbai rates captured in `cost-estimate.json` give a fixed subtotal
of $2.18/24 hours or $4.36/48 hours for one task, ALB and assumed three public IPv4
addresses. LCU usage, WAF, logs, registry/builds, data, tax and domain are extra.
One sustained ALB LCU adds $0.008/hour. Plan $5–10/24h or $10–20/48h for modest
traffic, not as a quote, credit guarantee or spend cap. Verify account-specific
pricing/credits before approval; budget alarms do not stop charges.

Initially use the actual AWS HTTPS URL. A domain can remain at any registrar.
After choosing one, validate ownership with DNS and request an ACM certificate in
the ALB's region. Add it to the STEPLOCK HTTPS listener; add the custom host as an
OR condition while preserving the AWS service host, and add it to application
trusted hosts. Route 53 uses an A/AAAA alias to the STEPLOCK ALB. Other DNS providers
can use a `www` or `app` CNAME to the ALB DNS name. An apex needs supported
ALIAS/ANAME/flattening or Route 53, rather than a standard apex CNAME. Verify the
certificate and routes before switching primary URLs.
[AWS custom-domain procedure](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/express-service-advanced-customization.html).
A future CloudFront design would need its ACM certificate in us-east-1; that is
a different architecture and is not required for this ALB trial.

## Teardown — exact owned resources only

At deployment record actual service/cluster ARN, VPC/subnets/routes, ALB/listeners/
targets/security groups, WAF/IP set, ECR repository/image, log group, new roles/
secrets/certificates and UTC expiry. An `ExpiresAt` tag does not schedule deletion.

At expiry block new STEPLOCK traffic, remove its WAF association and delete its
Express service using the inventoried ARN. Monitor real deletion; stopped tasks
alone do not remove ALB/IPv4 charges. Confirm no other consumer before deleting
any resource. Remove only inventoried STEPLOCK leftovers, including WAF/IP set,
registry images, logs, roles, secrets and dedicated network. Verify ALB/ENIs/public
addresses are gone, then review delayed billing. Preserve Git evidence and the
frozen tag, and recheck REFLEX read-only. Never use account-wide or partial-name cleanup.
[Service deletion reference](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_DeleteExpressGatewayService.html).
