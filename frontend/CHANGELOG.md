# CHANGELOG

## v1.0.0 (2025-02-12)

### Breaking

* feat!: [Breaking Changes] separate internal &amp; public endpoints
- pause / resume monitors ([`b0302ed`](https://github.com/sahasourav123/watchtower/commit/b0302ed9e7c760e8c1c5fe4f79e5d6bb6dd639d7))

### Build

* build(deps): add and upgrade dependencies ([`f5a60bd`](https://github.com/sahasourav123/watchtower/commit/f5a60bd668e670680a4da6aa59d7acf519c9d2f7))

### Chore

* chore: update release tag pattern ([`50567d8`](https://github.com/sahasourav123/watchtower/commit/50567d81df770565ec215d6935cb6c575da0f7ff))

* chore: improved monitor creation and run history
- group uptime history by monitor group
- add metadata fields for monitor ([`9d83dc2`](https://github.com/sahasourav123/watchtower/commit/9d83dc2892281dca33464e93cf70d3d664287147))

* chore: add observability on the applications ([`ef640e3`](https://github.com/sahasourav123/watchtower/commit/ef640e3b814fd0fe9fc3045194b2bfc1bcd4582b))

* chore: store alert recipient as json in db ([`553384a`](https://github.com/sahasourav123/watchtower/commit/553384a471ebd97b2bc25e2eb1ce5aefb1485b0b))

* chore: improve page layout &amp; side navigation menu ([`d012ef9`](https://github.com/sahasourav123/watchtower/commit/d012ef919b99e8c325e07dcc3c280f984619f682))

* chore: Show list of monitors intuitively ([`835ec7e`](https://github.com/sahasourav123/watchtower/commit/835ec7e5ad90aaf6edd61c2364291da0632b35c5))

* chore: add Google Analytics tracking ([`310430e`](https://github.com/sahasourav123/watchtower/commit/310430ecce527cb051121fd32f4526853258bd31))

* chore: monitor checking workflow ([`d39a5d8`](https://github.com/sahasourav123/watchtower/commit/d39a5d8cfc3ba03738a412f67d1b0e2c1ad5c81b))

* chore: exception handling on api status check ([`f6cace7`](https://github.com/sahasourav123/watchtower/commit/f6cace76130b68959fa1cce85d82d8e8cbd49cf4))

* chore: auth is optional for self-hosted use ([`2b1aac1`](https://github.com/sahasourav123/watchtower/commit/2b1aac1885649c8829423876b91479a1a79db625))

* chore: add suitable image for the project ([`8b86479`](https://github.com/sahasourav123/watchtower/commit/8b86479e54dc2057dc902c7bf84e0e6e5b6be7e1))

* chore: show org code in uder profile ([`00c8df7`](https://github.com/sahasourav123/watchtower/commit/00c8df76afaa05b88f06cf8686543e43b10c15d7))

* chore: Clean look for monitor list ([`fd55074`](https://github.com/sahasourav123/watchtower/commit/fd5507482d6f45e9763aac100327be0a39d8ac76))

* chore:
- Show Monitor List
- Trigger initial after scheduling
- store user_code with monitor ([`e6d3750`](https://github.com/sahasourav123/watchtower/commit/e6d375000cb63bd3aa90c5e706d583aad07cbb3e))

* chore: capture response time in milliseconds ([`8209e92`](https://github.com/sahasourav123/watchtower/commit/8209e92246ac7f973df6213114448c39dd942555))

* chore: skip ssl verification &amp; update monitor data model ([`4b16421`](https://github.com/sahasourav123/watchtower/commit/4b1642189cadc660507321705b56646e6782c4b9))

### Ci

* ci: add watchtower deploy monitoring ([`aa30ae6`](https://github.com/sahasourav123/watchtower/commit/aa30ae64a0dec1638ef084fc03a9a02e674b1b64))

* ci: automated cross architecture image build ([`b8b5c66`](https://github.com/sahasourav123/watchtower/commit/b8b5c6619522bedf85aa55202e262ef46e343ee0))

* ci(deps): upgrade dependencies ([`a53cfab`](https://github.com/sahasourav123/watchtower/commit/a53cfab01a199d45f370691f6f4c54652e85e151))

* ci: fix issue in build pipeline ([`c910643`](https://github.com/sahasourav123/watchtower/commit/c9106437fec1b10eee9c20284fad5a1794e6925c))

* ci: fix issue in build pipeline ([`93c812f`](https://github.com/sahasourav123/watchtower/commit/93c812f8acc6da49e4ea8f5e99f69fab8fa8d0c6))

* ci: manual deploy with workflow dispatch ([`1adb221`](https://github.com/sahasourav123/watchtower/commit/1adb221296bac4f3f8cffd32a25ac784ec8d48bd))

* ci: update port number &amp; fix build pipeline ([`62d256a`](https://github.com/sahasourav123/watchtower/commit/62d256a925ef60e7f94fddb1e5bddac39bc3eedb))

* ci: update port number &amp; fix build pipeline ([`a3379e4`](https://github.com/sahasourav123/watchtower/commit/a3379e49a9c63cae474dfbd18bc4a88c703ecd76))

* ci: update port number &amp; fix build pipeline ([`3518fb9`](https://github.com/sahasourav123/watchtower/commit/3518fb9bd89960d1ad3e5ff340af174dd773072e))

* ci: CI pipeline for frontend app ([`8fb2c95`](https://github.com/sahasourav123/watchtower/commit/8fb2c95283095cd3fe05f989324d655ee430a7db))

* ci: implement ci pipeline ([`e414b18`](https://github.com/sahasourav123/watchtower/commit/e414b18a8019088cda7d636ff3e1e2b838e97394))

### Documentation

* docs: update README.md ([`954c5e9`](https://github.com/sahasourav123/watchtower/commit/954c5e9d2060131f70d968694b38e312db08819f))

### Feature

* feat: event monitoring (push based) ([`0612514`](https://github.com/sahasourav123/watchtower/commit/06125149bbab24867c4d051c0677aef9febf1a53))

* feat: display global check stats ([`3a0a8e1`](https://github.com/sahasourav123/watchtower/commit/3a0a8e1ba3bc0257289ad7eb212b4b134c935c3d))

* feat: alert on status monitor uptime status change ([`85ef754`](https://github.com/sahasourav123/watchtower/commit/85ef75456977faf37cee9037687c8d6005d63b20))

* feat: run existing monitor from UI ([`290957a`](https://github.com/sahasourav123/watchtower/commit/290957a8092042026580c25311a4d8af7629966d))

* feat: new monitor type support ([`40419c6`](https://github.com/sahasourav123/watchtower/commit/40419c6fc4e9600f36e17677acfa0843fffde9c4))

* feat: added new checks (dns, tcp).
Readme Updated ([`b7c7cd5`](https://github.com/sahasourav123/watchtower/commit/b7c7cd5c814360252318c428694ca40dbb88b503))

* feat: Uptime Stats
 - Display mean uptime over period
 - plot response time distribution for avg &amp; p90 ([`eef2c65`](https://github.com/sahasourav123/watchtower/commit/eef2c655edaf06c5d45a4fc09b1e4ea24182e5ee))

* feat: browsing enabled for guest users
- pause/resume monitor from UI
- display global stats to guest
- map internal &amp; public endpoints ([`bda10be`](https://github.com/sahasourav123/watchtower/commit/bda10beff38d16249bd1b3467b155fcd56d0092b))

* feat: Show Sample Monitor &amp; Uptime History for Guest Users ([`f84976a`](https://github.com/sahasourav123/watchtower/commit/f84976af7ab3b8e0f770dd0065549528be25e0bc))

* feat: restrict ssl &amp; domain expiry interval to day and above ([`873befc`](https://github.com/sahasourav123/watchtower/commit/873befc122ddf18372ec97b5e8f8d67791d3d150))

* feat: schedule monitor with different interval i.e. seconds to weeks ([`1b97504`](https://github.com/sahasourav123/watchtower/commit/1b975042f95bb5f80ad25a81c36647f392825c62))

* feat: update Readme ([`6e30b90`](https://github.com/sahasourav123/watchtower/commit/6e30b90ab30877ea443a7aa6658275452b08f3f6))

* feat: create monitor of new types ([`febd2e7`](https://github.com/sahasourav123/watchtower/commit/febd2e73640db937cd4bb4456c6dbd3a2d1aa36c))

* feat: status check for domain expiry, ssl expiry, database connection ([`36842bb`](https://github.com/sahasourav123/watchtower/commit/36842bb4a5f090bb1ef4779d1ed1733b1a8694f3))

* feat: visualize uptime history ([`815e1da`](https://github.com/sahasourav123/watchtower/commit/815e1da0f369189f70051b88cdb45b6dfb08c902))

* feat: compute &amp; serve uptime stats ([`b94662e`](https://github.com/sahasourav123/watchtower/commit/b94662ec66e1e066affcf3b3e7da71c2e20f3ab4))

* feat: log signin history ([`d25f006`](https://github.com/sahasourav123/watchtower/commit/d25f006335ac995461826aba7659cd83349b4b76))

* feat: Create &amp; List Alert Channels ([`fed1123`](https://github.com/sahasourav123/watchtower/commit/fed1123b4c9ea31e8b5522d3916bfd01ce08163a))

* feat: update monitor interval &amp; timeout workflow ([`ce2ce2e`](https://github.com/sahasourav123/watchtower/commit/ce2ce2e824be0e2b8b61d7ca0d60a2e37d08ef73))

* feat: integrate login system ([`d826128`](https://github.com/sahasourav123/watchtower/commit/d826128348d2ea6a82950363b89badeddb9a2e48))

### Fix

* fix: release pipeline ([`4c07c84`](https://github.com/sahasourav123/watchtower/commit/4c07c840d032f0b9266c5388ad5ec14fe5365fb6))

* fix: job execution issues
- next run time got null on job refresh
- email recipient parsed correctly ([`9542b7e`](https://github.com/sahasourav123/watchtower/commit/9542b7e9da76ee562178814698d5cf5defcb25c1))

* fix: error when no alert channel exist for a user ([`e00a311`](https://github.com/sahasourav123/watchtower/commit/e00a3111060daab7ced91b88d005d0fc12eaa2ae))

* fix: handle when no alerts channels are associated with monitor ([`40b06c6`](https://github.com/sahasourav123/watchtower/commit/40b06c61ec117cbae629ddb3c8458e861efeab1f))

* fix: handle when no alerts channels are associated with monitor ([`ca35563`](https://github.com/sahasourav123/watchtower/commit/ca3556370e2fac54cbed78bc3198c32478b5e77c))

* fix: redis value retrival ([`c968ca3`](https://github.com/sahasourav123/watchtower/commit/c968ca3cf20a36da3f1f8f928e1eaee6d0437795))

* fix: add missing dependency ([`e1dd561`](https://github.com/sahasourav123/watchtower/commit/e1dd5616489092f2c342449605f9bd4b311f5429))

* fix: host blacklisting for ssrf protection ([`0085907`](https://github.com/sahasourav123/watchtower/commit/0085907fccef6d4209ea1a373baf1beaa3b16423))

* fix: add missing library ([`6cfd13f`](https://github.com/sahasourav123/watchtower/commit/6cfd13fce9309ad7f89cb02185233c3decc5ea9c))

* fix: use requests library for website uptime check ([`a94d225`](https://github.com/sahasourav123/watchtower/commit/a94d225db558d21912c8214d712183a01b1d789a))

* fix: set request timeout and add handle request exceptions ([`0df4f0f`](https://github.com/sahasourav123/watchtower/commit/0df4f0f601f5ac34771adaf5a50812f0905a5c64))

* fix: Monitor creation &amp; org selection ([`0e2b92f`](https://github.com/sahasourav123/watchtower/commit/0e2b92f1977baafc27a77602ac0024b51d413501))

* fix: connection issue ([`cea4b2d`](https://github.com/sahasourav123/watchtower/commit/cea4b2d3f1275ae0dba3dd13f0f7915958e34f17))

### Unknown

* update release actions ([`0a50b1e`](https://github.com/sahasourav123/watchtower/commit/0a50b1e8f525bab3ffd9be65e8759d4da2c69083))

* create views for failure analytics ([`97831be`](https://github.com/sahasourav123/watchtower/commit/97831beca20244d76b78358948cf890ea4892299))

* wip: slack integration ([`692e0d6`](https://github.com/sahasourav123/watchtower/commit/692e0d6a61f207b33d9eb6df7ed492b0104ffb9c))

* deps: update dependencies ([`2096b50`](https://github.com/sahasourav123/watchtower/commit/2096b5095d98c4b9a5e198ba5553f3c4f87432bd))

* wip: day-wise uptime history ([`cfc85b4`](https://github.com/sahasourav123/watchtower/commit/cfc85b4095d7ef641222f7b91d978a3bd80458e3))

* add scheduler for monitors and placeholder for functionalities ([`f2e93ae`](https://github.com/sahasourav123/watchtower/commit/f2e93ae156b4f2f8131e77c357982e292eb323c9))

* add schema, placeholders &amp; utilities ([`e81dda1`](https://github.com/sahasourav123/watchtower/commit/e81dda1689d72aa06c0c9dbfec6433df0c79e311))

* Create dependabot.yml ([`8e07ce6`](https://github.com/sahasourav123/watchtower/commit/8e07ce6c231c5ab27a2cd6098e1499c736158674))

* change container name to avoid clash ([`dd1ede2`](https://github.com/sahasourav123/watchtower/commit/dd1ede23a56d82a8a3c2f5e2eb6489fbd8466846))

* Merge remote-tracking branch &#39;origin/main&#39;

# Conflicts:
#	.github/workflows/build-frontend.yml ([`dde52ef`](https://github.com/sahasourav123/watchtower/commit/dde52eff91b0fea0fc0914327cd8a37d80749d78))

* Update .env.local ([`9c18a32`](https://github.com/sahasourav123/watchtower/commit/9c18a324fa116d77bcf4bf3eeca744507de27c85))

* create project skeleton ([`b9e29b2`](https://github.com/sahasourav123/watchtower/commit/b9e29b295547ab75a8be6898af02a40d0723edf4))

* Initial commit ([`e0c0dde`](https://github.com/sahasourav123/watchtower/commit/e0c0ddebea3d8b2579f6b3c8dc5887c87fe6c5ff))
