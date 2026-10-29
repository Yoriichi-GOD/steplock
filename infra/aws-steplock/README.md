# Independent STEPLOCK deployment boundary

**NOT_DEPLOYED.** The user authorized building/testing and explicitly stopped
before paid AWS deployment. No STEPLOCK AWS resources, build jobs, roles, secrets,
network rules or public endpoints have been created.

Read-only preflight confirmed both existing REFLEX stacks `UPDATE_COMPLETE` and
its public health HTTP 200, OpenCV 5.0.0, build `reflex-20261024t095525z`. REFLEX
source and resources were not changed. Keep STEPLOCK OpenCV 4 isolated.

The repository Dockerfile is a local, separate OpenCV 4 image candidate. Docker
CLI is installed, but the Linux daemon was unavailable
(`dockerDesktopLinuxEngine` pipe missing), so image build/container smoke are
**NOT_RUN**, not passing. Native local build and browser operation are verified
separately. No new cloud service can be claimed from this file.

When local Docker is available:

```powershell
docker build -t steplock-nebius:local .
docker run --rm -p 127.0.0.1:8000:8000 steplock-nebius:local
```

The default image has agent disabled and generated examples only. Supply the
backend environment securely to enable Nebius; never bake credentials or physical
dataset media into an image. Host validation currently permits loopback only;
any future public deployment needs an explicit reviewed hostname/security change.

A future deployment requires a concrete cost review (Fargate/load balancer/IPv4,
logs, ECR/builds and secrets), user approval, independent `steplock-*` resource
names, scoped secret injection, image digest/health/log proof, hosted browser
acceptance, REFLEX recheck and a teardown confined to newly created resources.
Nebius promo credits do not establish AWS coverage. No deployment command is
executed by the resume helper.
