# STEPLOCK custom domain — 2 November 2026

Status: **WWW_VERIFIED — ROOT_HTTPS_PENDING**.

- [Verified landing page](https://www.step-lock.xyz)
- [Verified inspection demo](https://www.step-lock.xyz/demo)
- [Redacted checks](verification/domain-20261102/checks.json)
- [Screenshots and hashes](../screenshots/domain-20261102/manifest.json)

The `www` hostname passed normal DNS/TLS checks and all four actual inspection
examples from a separate AWS network. Browser acceptance also passed, using
explicit diagnostic routing around this computer's stale ISP resolver. HTTPS
certificate checks stayed enabled. The root HTTP homepage redirects correctly;
root HTTPS and root deep links remain incomplete, as detailed below. The
[original AWS URL](AWS_DEPLOYMENT_20261102.md) remains available.

## Verified so far

- The public registry identifies GoDaddy as registrar and lists
  `ns29.domaincontrol.com` and `ns30.domaincontrol.com`; registration is dated
  2 November 2026. Public DNS initially returned NXDOMAIN; the GoDaddy delegation
  and certificate CNAME subsequently resolved. Registration and public DNS
  readiness are separate checks.
- Four actual hosted generated examples passed through the new hostname:
  normal PASS, wrong component HOLD, wrong order HOLD, and corrected PASS.
  The independent CodeBuild run `777dfdf0-63ae-4582-94fa-bf43fb8ca487`
  succeeded at 12:10:54 UTC (17:40:54 IST), with normal DNS and TLS verification.
  It also checked the original AWS health URL returned 200. The initial probe
  failed because the runner had no source checkout; embedding the same unchanged
  smoke script fixed that runner setup. Both run logs are preserved privately.
- Earlier browser-callback and manual-code CLI sign-ins failed with
  `TOKEN_EXPIRED`, including one after a profile-scoped logout. Local UTC and
  the AWS HTTP Date agreed within request time. A later external-browser approval
  succeeded, followed by a successful STS identity check in the intended account.
- Browser automation recovered. The registrar inventory contains the parked
  apex, `www` CNAME, two NS records, SOA, `_domainconnect`, and `_dmarc`. There
  were no MX records. The validation CNAME was added, `www` was changed to the
  ALB hostname, and GoDaddy replaced the parked apex A record with its forwarding
  addresses. NS, SOA, `_domainconnect` and `_dmarc` remain in place.
- cfn-lint 1.59.0 found zero issues in both changed templates. AWS template and
  change-set validation succeeded. The cleanup IAM policy passed Access
  Analyzer with zero findings. cfn-guard is unavailable and was not run; these
  checks do not constitute a full security/compliance audit.

## Applied routing

GoDaddy remains authoritative. The app is served at `https://www.step-lock.xyz`.
GoDaddy has saved an unmasked permanent 301 redirect from the apex to that
address. This is forwarding, not an apex CNAME or a fixed ALB IP address.

The `www` CNAME points to the live STEPLOCK ALB DNS name:
`ecs-express-gateway-alb-9b87b79f-506039654.ap-southeast-2.elb.amazonaws.com`.
Do not copy load-balancer IP addresses into fixed A records or put a CNAME at
`@`. The saved ownership-validation record is:

| Type | GoDaddy name | Value |
|---|---|---|
| CNAME | `_0fe6dcd4799275087793afca5c569085.www` | `_c671731f7fdb33854bbc9b7ad593368c.wzccmgtwzk.acm-validations.aws` |

A non-exportable, DNS-validated ACM certificate for `www.step-lock.xyz` is ISSUED
and attached as an additional SNI certificate. The AWS-generated certificate
remains default. The managed host-header rule contains both exact hostnames;
its target groups and deployment weights were preserved. Recheck this direct
rule customization after future Express updates.

The service's exact trusted-host list includes `www.step-lock.xyz` and the
original AWS hostname. Both service and expiry stacks are UPDATE_COMPLETE.
ECS has one running/desired task and zero pending; the running image digest is
unchanged: `sha256:fe77c48ef879350c0cc83c2c26413c5413da97aafd3d11c9e164caab226d8447`.
WAF remains attached with both original rate rules. No application code or
historical benchmark was changed.

This route adds no Route 53 hosted zone, new load balancer, task, model endpoint
or domain purchase. ACM non-exportable public certificates for integrated AWS
services have no certificate charge; GoDaddy documents HTTPS forwarding at no
additional charge. Existing hosting and usage charges remain. The original
seven-day / USD 25 allowance and scheduled expiry are unchanged. Any added AWS
resource must be inventoried and covered by cleanup before routing is enabled.

The certificate and listener binding are owned by the existing service stack.
Their dependency detaches SNI before certificate/service deletion. The existing
cleanup role now includes only the additional exact certificate/listener ARNs
and required cleanup actions. Service teardown remains **8 November 2026,
19:23:05 UTC / 9 November, 00:53:05 IST**; foundation cleanup follows 30 minutes
later. This is scheduled cleanup, not proof that future deletion already ran.

## Actual acceptance and remaining gaps

| Check | Result |
|---|---|
| Google and Cloudflare public DNS | `www` resolves to the intended ALB |
| External AWS run, normal DNS/TLS | Four engine scenarios PASS; original AWS health 200 |
| Local public-boundary regression | 8 passed in 34.38 seconds; one existing deprecation warning |
| Browser viewports | No horizontal overflow at 1280x720, 390x844 and 320x740 |
| Normal inspection | 30 frames, 10 events, PASS; completion 8,060 ms; vision p95 45.7 ms |
| Source loss after PASS | SOURCE LOST after 3,375 ms; zero confirmed steps and green PASS elements |
| Reconnect, reset and refresh | Passed; reset/refresh returns PENDING |
| API unavailable at startup | PENDING, disabled Run button |
| Public boundary | Private/model routes and hostile origin rejected; owner access and contact remain disabled |
| Source image | `filter: none`, opacity 1 |
| Browser errors / external origins | Zero in the primary context |
| Original AWS browser regression | Entire acceptance run passed again without diagnostic DNS routing |
| Root HTTP homepage | 301 to `https://www.step-lock.xyz` |
| Root HTTPS | Not working yet; timeout/reset observed, most recently at 12:19 UTC / 17:49 IST |
| Root `/demo` over HTTP | 404 during the checked window; use the explicit `www` demo link |

GoDaddy states that forwarding SSL may take a few hours to activate. This is
separate from the already issued AWS `www` certificate. Root TLS and root path
forwarding need a later successful check; saving the settings alone is not proof.
The local ISP resolver still reached the prior destination during acceptance.
Do not disable TLS checks to work around propagation.

The browser run used a localhost-only CONNECT tunnel that routes only the exact
public hostname to the independently verified ALB hostname. It does not terminate
TLS, read credentials, or change system DNS. The override is explicit in the
receipt. The separate AWS smoke run used no DNS override. Failed local browser
attempts and original deployment screenshots remain unchanged under ignored
runtime storage. Single-run timings above are not a latency distribution or a
factory-performance claim.

## Definition of Done

- [x] AWS caller identity and live STEPLOCK inventory confirmed.
- [x] Existing registrar records inspected and preserved.
- [x] ACM DNS record published; certificate status ISSUED.
- [x] Correct SNI certificate and host routing read back from AWS.
- [x] Exact trusted-host update deployed; original AWS URL still works.
- [x] `www` DNS resolves to the intended load balancer on public resolvers.
- [ ] Root HTTP/HTTPS forwarding and deep links verified without TLS bypass.
- [x] Landing, demo, static assets and public API work through the new origin.
- [x] Four generated-engine scenarios and evidence isolation pass.
- [x] Responsive browser, source-loss clearing and unavailable-backend checks pass.
- [x] New resources included in the original expiry cleanup scope.
- [x] Redacted result receipt and screenshot hashes saved; Git checkpoint recorded separately.

Run browser acceptance with a separate output folder to retain the original
deployment evidence:

```powershell
node infra/aws-steplock/hosted_browser_check.cjs https://www.step-lock.xyz runtime/domain-step-lock/browser
```

For diagnostic routing during ISP propagation, append the verified ALB hostname
as the fourth argument. This enables the local test-only tunnel and records the
override; TLS validation remains enabled. Public reachability still needs an
independent normal-DNS check.

All inspection examples remain **SYNTHETIC_FIXTURE**. Domain verification is not
physical-camera or industrial-accuracy validation.

## Official references

- [AWS ECS Express custom-domain procedure](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/express-service-advanced-customization.html)
- [ACM certificate pricing](https://aws.amazon.com/certificate-manager/pricing/)
- [GoDaddy HTTPS forwarding](https://www.godaddy.com/en-ph/help/what-forwarding-types-are-available-2376)
- [GoDaddy CNAME requirements](https://www.godaddy.com/en-in/help/add-a-cname-record-19236)
- [AWS CLI login, including manual-code mode](https://docs.aws.amazon.com/cli/latest/reference/login/)
- [AWS CLI token-exchange issue and clock diagnostics](https://github.com/aws/aws-cli/issues/10330)
