# STEPLOCK trial retirement — 2 November 2026

Status: **SERVICE_DELETED / FOUNDATION_DELETED / TEMPORARY_PERMISSION_REMOVED**.

Final verification at **15:06:37 UTC / 20:36:37 IST**: both stacks report
DELETE_COMPLETE. The service's six stack resources and foundation's seventeen
resources report deletion complete. Independent exact-resource calls confirm
LoadBalancerNotFound, RepositoryNotFoundException and InvalidVpcID.NotFound.
The temporary policy was deleted and ListRolePolicies returns only the original
inventory-restricted policy. The expiry control is retained for audit, as planned.
No other project's resources were targeted. See the
[machine-readable receipt](verification/contact-20261102/aws-retirement.json).

The Cloudflare website and automatic contact flow are independent of this old
trial. Previously incurred AWS charges can still appear later. This is resource
retirement verification, not a claim that the entire AWS account has a zero bill.

## Failure and recovery history

The founder explicitly approved the temporary read permission after the review
block. IAM Access Analyzer returned zero findings. The exact approved statement
was applied; no new write permissions or trust changes were made. The immediate
retry hit the same denial before propagation. A subsequent principal-policy
simulation returned `allowed`, and deletion was retried at 14:55:59 UTC.
That retry succeeded. The service was observed DELETE_COMPLETE at 15:04:45 UTC.
Only then was foundation deletion requested, at 15:05:05 UTC. Both stacks and
the permission removal were verified by the final check above.

The free Cloudflare Pages replacement is serving apex and www. At 14:45 UTC,
normal DNS and validated HTTPS checks passed, including the recorded videos,
captions, hashes and absence of a public inspection API. Production contact
delivery was activated and recipient-confirmed. Production contact/style
bundles match the tested local release byte-for-byte.

The original paid trial was kept until these gates passed. The targeted
`steplock-service` DeleteStack request was accepted at 14:49:46 UTC using the
existing inventory-restricted expiry role. It failed at 14:50:49 UTC because the
CloudFormation WAF association handler checks
`wafv2:GetWebACLForResource` against a regional `webacl/*/*` ARN. The original
role grants that action only on the inventoried concrete web ACL ARN.

The failed events identify WafAssociation as the actionable permission failure;
the stack DELETE_FAILED event is the consequence. The custom AWS listener
certificate binding was already detached by the stack operation. Do not treat
this partial cleanup as cost closure, or use the former AWS custom hostname as
the rollback path without restoring its certificate binding. The Cloudflare
site and its SSL are independent.

## Concrete proposed repair

Add one temporary inline statement to the existing expiry deletion role:

- Action: `wafv2:GetWebACLForResource` only (read).
- Resource: `arn:aws:wafv2:<Sydney-region>:<same-account>:regional/webacl/*/*`.
- No new principal, trust, credential, write permission, paid resource or trial
  extension. Existing deletion mutations remain restricted to the inventory.
- Validate the policy, retry only the existing STEPLOCK service stack deletion,
  verify it completes, then retire the dedicated foundation stack.
- Remove the temporary inline policy after cleanup. Keep the original expiry
  control and immutable source/evidence history for audit.

The exact account-scoped policy is in private ignored runtime storage for review.
Automatic approval review initially rejected applying this specific IAM
access-policy change without explicit user approval. That attempt made no
change. The founder subsequently approved the exact temporary read permission;
the current follow-up state is recorded above. Approval and policy simulation
alone are not proof of successful resource deletion.

The foundation was preserved until the service completed deletion. The original
expiry control and schedule definitions remain unchanged, now targeting the
already-deleted trial stacks. They are not evidence of any remaining workload.
No new paid resource, recurring server or trial extension was created.

No other project's resources were changed. Historical backend evaluations,
recordings, source, the Day 1 tag and unrelated work remain intact.

Sources: [WAF association permissions](https://docs.aws.amazon.com/waf/latest/developerguide/security_iam_service-with-iam.html),
[Express service deletion](https://docs.aws.amazon.com/sdkfornet/v4/apidocs/items/ECS/MECSDeleteExpressGatewayServiceDeleteExpressGatewayServiceRequest.html),
[ECS managed ingress](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/gateway-overview.html).
