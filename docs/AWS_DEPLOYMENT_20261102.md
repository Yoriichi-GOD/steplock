# AWS trial deployment - 2 November 2026

Status: IN_PROGRESS. Do not use this preparation receipt as hosted acceptance.

The founder authorized public AWS deployment for YC/A16Z review, then selected a
seven-day STEPLOCK trial with a USD 25 operating allowance. This is not an instant
AWS billing cutoff. No account-plan upgrade, domain purchase or paid model is part
of this deployment. Contact remains unconfigured.

The account's organization policy denies Mumbai. Sydney (`ap-southeast-2`) is
available and is the deployment region. Existing REFLEX infrastructure is read
only and is not used by STEPLOCK. Dedicated resource names start with `steplock-`.

## Release and cost

The container source is pinned to
`c8577afaba7ed8b5474e697294829dc85e2eed1e`; its application is the independently
accepted `e773bef` build. Infrastructure changes are separate. Historical
benchmarks, synthetic reports and `day1-final` remain unchanged.

One Linux x86 Fargate task uses 1 vCPU / 2 GiB, one application worker and a
dedicated HTTPS load balancer. There is no NAT gateway, GPU or external AI call.
Three assumed public IPv4 addresses, compute and ALB give a fixed estimate of
USD 0.09940/hour, USD 2.39/day or USD 16.70/seven days. WAF, ALB capacity units,
traffic, image storage, builds, logs and tax are extra. This is an estimate, not
a guaranteed bill. Rates were retrieved from the official regional
[Fargate price list](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECS/current/ap-southeast-2/index.json)
and [ALB price list](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSELB/current/ap-southeast-2/index.json);
[IPv4 pricing](https://aws.amazon.com/vpc/pricing/) and [WAF pricing](https://aws.amazon.com/waf/pricing/)
are separate. Account-specific credit/identity records stay in ignored runtime.

## Deployment structure

- `infra/aws-steplock/foundation.yaml`: separate VPC, two public subnets, cluster,
  private immutable ECR repository, seven-day logs, scoped image-builder role and
  distinct ECS roles. The builder checks out the exact commit, builds the image,
  runs all four actual-engine container examples and publishes only after success.
- `service.yaml`: digest-pinned ECS Express service at one task, trusted hosts,
  disabled agent/owner access and WAF. Initial access is limited to the tester IP;
  the exact service hostname is configured before opening public access.
- `expiry.yaml`: scheduled deletion of the service/WAF stack, followed 30 minutes
  later by the dedicated foundation. Its separate deletion role is scoped to the
  inventoried STEPLOCK resources. The small control stack remains for audit; its
  completed schedules and IAM roles have no continuously running workload.
- `expiry-probe.yaml`: an empty disposable log-group stack used to verify the
  scheduler -> CloudFormation -> scoped deletion-role path before handoff.
- `prepare_requests.py`: read-only AWS discovery and request generation. Account
  IDs, test IP and exact resource inventories are saved under ignored runtime.

Teardown was planned for 2026-11-08 at 19:23:05 UTC (9 November, 00:53:05 IST),
with foundation cleanup at 19:53:05 UTC. Schedule creation and a live expiry probe
must pass before this is reported as scheduled. These times do not promise that
delayed AWS deletion or billing will stop instantly.

## Definition of Done

Deployment is complete only after the immutable image build/container smoke,
healthy HTTPS service, WAF association, exact hostname/proxy trust, all four
hosted examples and evidence isolation, denied private/model APIs, source-loss
behavior, responsive browser views and autonomous expiry probe pass. Record
actual timings and the endpoint; distinguish these generated software checks from
physical factory validation. Recheck REFLEX without changing it.

## Verified so far

AWS sign-in and caller identity passed. Foundation and service templates passed
AWS syntax validation; all templates passed regional `cfn-lint` after correcting
the WAF CloudFormation property casing. The dedicated foundation reached
CREATE_COMPLETE. AWS image build `2b34f050-bafb-40b9-99d6-9bc31e5a724f`
completed successfully, including all four actual-engine container scenarios.
Published image digest:
`sha256:fe77c48ef879350c0cc83c2c26413c5413da97aafd3d11c9e164caab226d8447`.
The service request is pinned to that digest. Hosted acceptance, public opening
and scheduled deletion are pending.
