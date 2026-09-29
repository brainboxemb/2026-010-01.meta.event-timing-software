# Handoff

Use this document as the stable entry point when continuing the project in a new chat or agent session.

## Copy/paste start instruction

The block below is intended to be copied **as-is** into a new ChatGPT conversation. It contains the current continuation point, but the new session must verify GitHub before treating that state as current.

```text
Werk vanuit `brainboxemb/2026-010-01.meta.event-timing-software` als de cross-project coordination source voor het event-timing softwareproject.

Reconstrueer de actuele toestand niet uit oude chatgeschiedenis. Controleer eerst de repositories, issues, pull requests, CI/evidence en gegenereerde output op GitHub.

Lees eerst in de meta-repository:
- `AGENTS.md`
- `docs/01-handoff.md`
- `docs/02-agent-plan.md`
- `docs/00-brainstorm.md`
- `docs/03-domain-baseline.md`
- `docs/10-SDP-software-development-plan.md`
- `docs/11-SIP-software-implementation-planning.md`
- `docs/12-SDE-software-development-environment.md`
- `docs/13-SDE-java-build-test-toolchain.md`
- `docs/30-01-SISD-timing-application-specification-document.md`
- `docs/20-SSSD-software-system-specification-document.md`
- `docs/30-01-SISD-timing-application-specification-document.md`
- `docs/31-01-SDD-02-java-component-design.md`
- `docs/21-01-IDD-application-control-status.md`
- `docs/21-02-IDD-application-configuration.md`
- `docs/50-SVP-software-verification-plan.md`

Los daarna de actieve work repository op vanuit het actuele plan en GitHub-state. Belangrijke repositories zijn:
- `brainboxemb/2026-010-01.meta.event-timing-software` — coordination, planning, requirements, architecture en verification direction;
- `brainboxemb/2026-010-02.java.event-timing-framework` — publieke SI-01 Java framework/application implementatie;
- `brainboxemb/tool.java-project` — herbruikbare Java build/test/release tooling;
- `brainboxemb/tool.git-project` — generieke Git/repository tooling;
- `brainboxemb/tool.eng-docs` — engineering-documentation tooling.

Controleer voor het actuele werk:
1. open issues en open/draft PR's in meta;
2. open issues en open/draft PR's in iedere implementation/tool repository die door de actieve stap wordt genoemd;
3. de meest recent gemergede PR wanneer die directe predecessor-context bevat;
4. relevante CI-runs en evidence;
5. gegenereerde review-output onder `dev/pr-N/docs` of `dev/pr-N/bld` en de actuele `prod/docs` / `prod/bld` output wanneer die voor de stap relevant is.

Huidig continuation point dat je eerst tegen GitHub moet verifiëren:
- SIP Step 1 en Step 2 zijn afgerond; SIP Step 3 is actief;
- de geaccepteerde Step-2 releasebaseline is `v0.1.0`;
- de huidige gepubliceerde Step-3 productbaseline is `v0.2.1`;
- normale ontwikkeling loopt op `0.2.2-SNAPSHOT`;
- IF-03 definieert application-control/status;
- IF-11 definieert deployment/application-configuratie, inclusief TimingNode-, I/O-, presentation-, runtime/security-ownership, platform/profile overlays en secret references;
- presentation endpoints verwijzen naar TimingNodes; een TimingNode kent geen HTTP-poort of tablet;
- `BuildIdentity` is build provenance en staat los van deploymentconfiguratie;
- `CommandHandler` is de huidige gedeelde presentation/application boundary voor echte commands/queries;
- Presentation modelleert `Console`, `Remote Shell`, `Web` en `Remote API` als aparte interfaces; Console en Remote Shell delen `presentation.common.terminal` voor gemeenschappelijke terminalafhandeling; `Web` is 1..N endpoints, met per Web-endpoint precies één `TimingNodeId` en een eigen presentation-configured luisterpoort;
- `ApplicationId` is de afzonderlijke identiteit van de draaiende Timing Application; bij een single-TimingNode deployment mag en zal deze voorlopig dezelfde geconfigureerde waarde gebruiken als `TimingNodeId`, maar het blijven verschillende types/namespaces;
- de high-level I/O-architectuur scheidt `Devices` (Antenna, displays, keypad) van `Device Networks` (`CanNetworkController`, `NetworkDeviceService`);
- `CanNetworkController` beheert CAN-bus lifecycle/discovery/device-state; `DisplayRev1Can` is het passieve CAN-display dat SI-01 actief aanstuurt;
- `NetworkDeviceService` is de bidirectionele netwerkdevice-boundary; discovery/session/protocol-afhandeling is detail design. `DisplayRev2Wifi` ontdekt/verbindt zelf en bezit rendering, reconnect en synchronisatie;
- `DisplayModel` is alleen voor de passieve CAN-displayroute; smart-displaydata blijft algemene timing/status/reference-data;
- `upstream` benoemt de relatie met het centrale/externe systeem en niet de richting van één bericht; die relatie is bidirectioneel;
- upstream messaging gebruikt application-level `UpstreamMessageRouter` uitsluitend voor upstream-system target resolution; `ApplicationId` kan naar application-scoped responsibilities zoals `SystemStatus` routeren en `TimingNodeId` naar de betreffende `TimingNode.UpstreamMessagePort`;
- I/O `Messaging` bezit `UpstreamGateway` boven 1..N connectors; `UpstreamGateway` is de upstream/transport boundary en een `RabbitMqConnector` bezit transport/session mechanics, niet application/TimingNode-routing;
- `TimingNode.UpstreamMessagePort` is de bidirectionele semantische upstream-messagegrens van één TimingNode;
- `UpstreamMessageRouter` is nadrukkelijk geen generieke interne message/event bus; normale samenwerking binnen de applicatie blijft directe Java-collaboration waar passend;
- maak geen interne status-POJO-hiërarchie alleen om IF-03 JSON te spiegelen;
- deel herbruikbare application/runtime-functionaliteit via composition wanneer echte reuse dat rechtvaardigt; introduceer geen `BaseApplication` inheritance-hiërarchie zonder concrete noodzaak;
- A07 Remote API WebSocket events is gemerged en handmatig op Windows/NetBeans geaccepteerd;
- de actuele bounded Step-3 implementatieslice is A08 runtime logging: SLF4J blijft de framework-facade, de executable configureert JUL, file logging krijgt level + rotation/retention en de JavaFX engineering client kan optioneel via een eigen live-log socket verbinden;
- A08 mag één tijdelijke process-wide loglevel override aanbieden; die wijzigt `application.yml` niet en reset bij restart;
- de live logstream blijft gescheiden van IF-03 status/events en is geen applicatiestatus.

Voor Java releasewerk geldt bewust:
- Maven project version, CHANGELOG release section en Git tag moeten expliciet overeenkomen;
- een Git tag overschrijft nooit stilzwijgend een `-SNAPSHOT` Maven-version;
- een release is pas geaccepteerd nadat de exacte getagde revision opnieuw build/test/smoke verification heeft doorlopen;
- een productrelease moet een herkenbare gereleasde toolingbaseline gebruiken, met daarnaast exacte immutable commit provenance voor reusable GitHub workflows;
- `template.java-project` is bedoeld als externe conformance/reference consumer; de fixture in `tool.java-project` blijft de snelle interne toolingtest.

Ga verder vanuit de actieve SIP Step 3. Bepaal de eerstvolgende bounded implementation slice uit de actuele SIP, IF-03/IF-11, open issues/PR's en de Java-repository; bouw geen later capabilitymodel vooruit zonder een actuele consumer.

Gebruik de repository die eigenaar is van het werk:
- cross-project afspraken/status/closure-governance in meta;
- productimplementatie en product-test evidence in het Java framework;
- generieke Java tooling in `tool.java-project`;
- generieke Git tooling in `tool.git-project`.

Nieuwe software-ideeën, mogelijke requirements, architectuurkeuzes en onopgeloste vragen gaan eerst naar `docs/00-brainstorm.md` wanneer ze nog niet als besluit zijn gepromoveerd. Houd de projectdocumentatie generiek en noem niet het specifieke real-world event dat de aanleiding voor het project was.

Na ieder afgerond onderdeel:
- controleer de afgesproken tests/evidence en generated output;
- werk issue/PR beschrijving en relevante closure-evidence bij;
- merge pas na groene evidence;
- werk meta-status/documentatie bij wanneer een cross-project conclusie of planstatus werkelijk veranderd is;
- houd implementatiedetails in de repository die eigenaar is van de implementatie.
```

## How to use the handoff

The copy/paste block is deliberately operational. It tells a fresh session which sources to read, how to resolve repository ownership, what GitHub evidence to inspect and where the current implementation sequence is expected to continue.

The **current continuation point is not a substitute for checking GitHub**. It is a recovery hint. If issues, PRs, releases or the SIP have moved on, follow the current repository state and update this handoff when the continuation point materially changes.

## Repository resolution

`brainboxemb/2026-010-01.meta.event-timing-software` is the coordination and research repository. A single SIP step may involve several repositories, so do not assume the active implementation pull request is in meta.

Current repository ownership is approximately:

```text
brainboxemb/2026-010-01.meta.event-timing-software
  coordination, planning, requirements, architecture, verification direction

brainboxemb/2026-010-02.java.event-timing-framework
  public SI-01 Java framework/application implementation

brainboxemb/tool.java-project
  reusable Java project/build/test/release tooling

brainboxemb/tool.git-project
  reusable Git/repository tooling

brainboxemb/tool.eng-docs
  reusable engineering-documentation tooling
```

Resolve active work by reading the SIP/AP context and then inspecting the named repositories on GitHub. The implementation PR owns detailed implementation/test evidence. Meta owns the longer-lived cross-project plan and stable software-system conclusions.

## Pull-request and generated-output check

Before deciding what work is current:

1. inspect open issues and PRs in meta;
2. inspect open issues and PRs in every repository named by the active scope;
3. inspect immediate predecessor PRs when they contain relevant handoff evidence;
4. inspect CI rather than assuming a commit is proven merely because it exists;
5. inspect generated `dev/pr-<N>/...` output when the PR produces review artifacts;
6. inspect `prod/docs` or `prod/bld` when current main-branch output matters to the decision.

If no relevant PR is open, use the most recently completed work together with `docs/02-agent-plan.md` and the SIP to determine the next bounded piece of work.

## Software-item register

```text
SI-01  Headless Timing Application
SI-02  Desktop GUI Application
SI-03  Web Operator Application (React/browser/iPad)
```

The software-item number is stable across that item's SISD/SDD documents. It is not a document sequence number. The SSSD owns software-item/interface allocation; system-owned interfaces are documented through IDDs where applicable.

## Document roles

Use the sources consistently:

- `docs/00-brainstorm.md` — unpromoted software ideas, possible requirements, architecture options and unresolved questions;
- `docs/03-domain-baseline.md` — supplied domain facts and terminology;
- SDP — staged software-development governance and maturity/release direction;
- SIP — implementation sequence, active step and step-exit expectations;
- SDE — common development environment, repository/toolchain and workflow rules;
- SSSD/SISD/SDD — accepted specification/design at the appropriate level;
- SVP — common verification strategy and evidence expectations;
- active implementation/tool PR — detailed change/evidence record for current work.

Do not turn long-lived planning documents into chronological activity logs. Record stable conclusions and current status there; keep detailed execution history in issues, PRs, CI and generated evidence.

## Session-end check

Before handing off substantial work:

- ensure each involved PR contains enough description and evidence for a fresh session;
- inspect generated review output when applicable;
- update AP/SIP status only when the status genuinely changed;
- update domain, SDP/SIP, SDE, architecture or SVP only when their owned information changed;
- add unresolved software topics to the brainstorm rather than silently deciding them;
- update `CHANGELOG.md` for notable repository changes;
- update the copy/paste continuation point above when the next bounded piece of work materially changes.
