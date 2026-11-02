# STEPLOCK trial retirement — 2 November 2026

Status: **SERVICE_DELETE_FAILED / CLEANUP_PERMISSION_APPROVAL_PENDING**.

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
Automatic approval review rejected applying this specific IAM access-policy
change without explicit user approval. No temporary policy was applied and the
retry did not run. This is an approval gate, not a successful repair.

The foundation was not deleted while the service remains. The service and other
chargeable AWS resources may still incur costs. The original expiry schedule is
unchanged, but the same permission failure can also affect that scheduled
cleanup; do not rely on it as proof that deletion will succeed.

No other project's resources were changed. Historical backend evaluations,
recordings, source, the Day 1 tag and unrelated work remain intact.

Sources: [WAF association permissions](https://docs.aws.amazon.com/waf/latest/developerguide/security_iam_service-with-iam.html),
[Express service deletion](https://docs.aws.amazon.com/sdkfornet/v4/apidocs/items/ECS/MECSDeleteExpressGatewayServiceDeleteExpressGatewayServiceRequest.html),
[ECS managed ingress](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/gateway-overview.html).
