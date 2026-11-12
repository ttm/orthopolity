# TNG metadata access: executed D1 gate

12 November 2026. The readiness work was committed and pushed to `origin/main`
as `ad9bd13d11d86a1611dff5502df4dbf5dad3f7dd`, then the author requested the next
step. This record executes the first access gate of the
[D1 metadata task](cosmic-test-readiness-2026-11-11.md#next-task-queue).
**The archive is reachable with verified TLS, but anonymous access returns
HTTP 403. D1 awaits authorized TNG access; the metadata manifest is incomplete.**
The author reports no existing TNG access.

The intended scientific reading remains log-orthopolic collisionless total-matter
allocation among disjoint hosts in a dark-matter-only simulation. This access
probe supplies no evidence about that allocation.

## Requests and retained evidence

Both requests addressed only
`https://www.tng-project.org/api/TNG50-4-Dark/`. No credential, cookie, numerical
catalogue, particle array, merger tree or binary data endpoint was used. The
probe performs one request with no redirects or automatic retries. An explicit
second invocation corrected the local TLS trust configuration after the first
received no HTTP response.

| Attempt, UTC | Transport | Result | Response-body bytes |
|---|---|---|---:|
| 03:56:45 | Python default certificate paths | Local `SSLCertVerificationError`; no HTTP status or body | 0 |
| 13:48:51 | Explicit system CA bundle `/etc/ssl/cert.pem` | HTTP **403**, complete JSON response; certificate and hostname verification enabled | 55 |

The error response states:

> Failed session auth (and no API-Key sent).

This is an actual archive authentication response, unlike the earlier DNS,
browser and local-certificate failures. It does not establish that authenticated
access succeeds, or that any required scientific field is available.
The [raw response](../data/cosmic-source-qualification/2026-11-12/tng50-4-dark-system-trust/response-body.bin)
has SHA-256
`cdd472ccde7ca2d86c904a6a2d3ad2aa8d25fb4e89dc4f3d86c46d08cd58542a`.

The [acquisition manifest](../data/cosmic-source-qualification/2026-11-12/acquisition.json)
records both attempts, per-file hashes, the readiness commit and the shared
budget. Total response content is **55 / 1,048,576 bytes**, leaving **1,048,521
bytes** in this bounded metadata operation. Source snapshots reproduce the code
used for each attempt; receipts retain exact times, status, byte counts and
completeness. The system-trust receipt also identifies and hashes its CA bundle.

Task-local checks found no `TNG_API_KEY`, `ILLUSTRIS_API_KEY` or
`ILLUSTRISTNG_API_KEY` environment value, and no repository-root `.env`,
`.env.local` or `.env.tng` file. Only presence was checked; no credential value
was printed. The author's subsequent report resolves the current access question.

## Stop and resume conditions

The authentication stop rule applies. No further anonymous request, account
registration or provider contact follows from this attempt. A new request needs
an available authorized TNG account/session or API key configured locally; never
place a key in repository files, receipts or chat. The current anonymous probe
does not read credentials and cannot become authenticated just by setting an
environment variable.

When access becomes available, implement the authenticated metadata request
against the same approved HTTPS host with the remaining shared budget. Retain
run metadata, follow its metadata-only snapshot-list link, and inspect selected
development snapshot descriptions. If exact header fields, offsets or chunk
sizes are absent from JSON, record the missing information rather than silently
downloading data. No target has yet been assigned or sealed.

The exact acquisition manifest (D2), material-reader qualification (D3) and
separate abundance prediction remain dependent on successful metadata
qualification. The existing bounded archive search stays closed; the failure
to authenticate does not justify an unplanned source switch or an empirical
conclusion about orthopolity.

## Offline verification

The [anonymous probe](../experiments/probe_cosmic_metadata.py) retains partial
bodies on read failure, never reads an extra byte past its cap, marks truncation
and inconsistent lengths incomplete, preserves HTTP error responses and refuses
to overwrite a previous receipt. TLS verification remains enabled.

Ten [offline tests](../tests/test_cosmic_metadata_probe.py) pass, covering those
behaviors, redirect refusal, the distinction between HTTP and transport errors,
retained source/body hashes and the shared 55-byte budget. Run:

```sh
build/main-venv-2026-10-09/bin/python -m unittest discover -s tests -p 'test_cosmic_metadata_probe.py' -v
```

The tests use mocked responses and retained files; they make no network request.
Terminology, whitespace and all 196 local links / 2 anchors in this follow-up's
changed/new documents also pass.
No manuscript, frozen prior study, result or empirical registry entry changes.
