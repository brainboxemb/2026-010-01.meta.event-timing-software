# Engineering graph review

Source revision: dca0d6d0b488689778b5b82289f21fe5a0ec6dee
Source graph: sphinx-needs Event timing engineering graph migration-013

Engineering objects and outgoing relations come from the Sphinx-Needs export.
Incoming relations below are derived from those outgoing relations.
Diagram identities are references to existing engineering objects.

## Overview

| Object | Type | Authored outgoing | Generated incoming | Diagram refs |
| --- | --- | ---: | ---: | ---: |
| [Antenna](#antenna) | arch | 0 | 0 | 1 |
| [AntennaManager](#antennamanager) | arch | 0 | 0 | 1 |
| [Api](#api) | arch | 4 | 0 | 1 |
| [Application](#application) | arch | 0 | 0 | 1 |
| [Beeper](#beeper) | arch | 0 | 0 | 1 |
| [CanNetworkController](#cannetworkcontroller) | arch | 0 | 0 | 1 |
| [CommandHandler](#commandhandler) | arch | 5 | 0 | 1 |
| [Composition](#composition) | arch | 0 | 0 | 1 |
| [Conductor](#conductor) | arch | 0 | 0 | 1 |
| [Connector](#connector) | arch | 0 | 0 | 1 |
| [Console](#console) | arch | 0 | 0 | 1 |
| [DebugConnector](#debugconnector) | arch | 0 | 0 | 1 |
| [DeviceNetworks](#devicenetworks) | arch | 0 | 0 | 1 |
| [Devices](#devices) | arch | 0 | 0 | 1 |
| [Display](#display) | arch | 0 | 0 | 1 |
| [IF03-REQ-001](#if03-req-001) | ifreq | 2 | 2 | 0 |
| [IF03-REQ-002](#if03-req-002) | ifreq | 1 | 1 | 0 |
| [IF03-REQ-003](#if03-req-003) | ifreq | 2 | 1 | 0 |
| [IF03-REQ-004](#if03-req-004) | ifreq | 3 | 3 | 0 |
| [IF03-REQ-005](#if03-req-005) | ifreq | 1 | 1 | 0 |
| [IF03-REQ-006](#if03-req-006) | ifreq | 1 | 1 | 0 |
| [IF03-REQ-007](#if03-req-007) | ifreq | 1 | 0 | 0 |
| [IF03-REQ-008](#if03-req-008) | ifreq | 1 | 0 | 0 |
| [IF03-REQ-009](#if03-req-009) | ifreq | 1 | 0 | 0 |
| [IF03-REQ-010](#if03-req-010) | ifreq | 1 | 0 | 0 |
| [IF03-REQ-011](#if03-req-011) | ifreq | 1 | 1 | 0 |
| [IF03-REQ-012](#if03-req-012) | ifreq | 1 | 1 | 0 |
| [IF03-REQ-013](#if03-req-013) | ifreq | 2 | 1 | 0 |
| [IF03-REQ-014](#if03-req-014) | ifreq | 1 | 1 | 0 |
| [IF03-REQ-015](#if03-req-015) | ifreq | 1 | 1 | 0 |
| [IF03-REQ-016](#if03-req-016) | ifreq | 1 | 1 | 0 |
| [IF05-REQ-001](#if05-req-001) | ifreq | 0 | 1 | 0 |
| [IF05-REQ-002](#if05-req-002) | ifreq | 0 | 2 | 0 |
| [IF05-REQ-003](#if05-req-003) | ifreq | 0 | 2 | 0 |
| [IF05-REQ-004](#if05-req-004) | ifreq | 0 | 1 | 0 |
| [IF05-REQ-005](#if05-req-005) | ifreq | 0 | 1 | 0 |
| [IF05-REQ-006](#if05-req-006) | ifreq | 0 | 1 | 0 |
| [IF05-REQ-007](#if05-req-007) | ifreq | 0 | 2 | 0 |
| [Keypad](#keypad) | arch | 0 | 0 | 1 |
| [LogBook](#logbook) | arch | 0 | 0 | 1 |
| [Logging](#logging) | arch | 0 | 0 | 1 |
| [LoggingServer](#loggingserver) | arch | 0 | 0 | 1 |
| [Messaging](#messaging) | arch | 0 | 0 | 1 |
| [NetworkDeviceService](#networkdeviceservice) | arch | 0 | 0 | 1 |
| [NextUpTeams](#nextupteams) | arch | 0 | 0 | 1 |
| [PlatformEnvironment](#platformenvironment) | arch | 0 | 0 | 1 |
| [PlatformEvents](#platformevents) | arch | 0 | 0 | 1 |
| [PlatformExecution](#platformexecution) | arch | 0 | 0 | 1 |
| [RabbitMqConnector](#rabbitmqconnector) | arch | 0 | 0 | 1 |
| [RaceData](#racedata) | arch | 0 | 0 | 1 |
| [RemoteShell](#remoteshell) | arch | 0 | 0 | 1 |
| [Rev1CanDisplay](#rev1candisplay) | arch | 0 | 0 | 1 |
| [Rev1CanKeypad](#rev1cankeypad) | arch | 0 | 0 | 1 |
| [Rev2WifiDisplay](#rev2wifidisplay) | arch | 0 | 0 | 1 |
| [SI01-REQ-001](#si01-req-001) | req | 0 | 1 | 0 |
| [SI01-REQ-002](#si01-req-002) | req | 0 | 1 | 0 |
| [SI01-REQ-003](#si01-req-003) | req | 2 | 2 | 0 |
| [SI01-REQ-010](#si01-req-010) | req | 0 | 2 | 0 |
| [SI01-REQ-011](#si01-req-011) | req | 0 | 1 | 0 |
| [SI01-REQ-020](#si01-req-020) | req | 2 | 3 | 0 |
| [SI01-REQ-021](#si01-req-021) | req | 2 | 3 | 0 |
| [SI01-REQ-022](#si01-req-022) | req | 1 | 3 | 0 |
| [SI01-REQ-023](#si01-req-023) | req | 0 | 2 | 0 |
| [SI01-REQ-030](#si01-req-030) | req | 0 | 2 | 0 |
| [SI01-REQ-031](#si01-req-031) | req | 0 | 6 | 0 |
| [SI01-REQ-032](#si01-req-032) | req | 0 | 1 | 0 |
| [SI01-REQ-033](#si01-req-033) | req | 0 | 1 | 0 |
| [SI01-REQ-040](#si01-req-040) | req | 4 | 2 | 0 |
| [SI01-REQ-041](#si01-req-041) | req | 2 | 2 | 0 |
| [SI01-REQ-042](#si01-req-042) | req | 3 | 3 | 0 |
| [SI01-REQ-043](#si01-req-043) | req | 1 | 3 | 0 |
| [SI01-REQ-044](#si01-req-044) | req | 1 | 2 | 0 |
| [SI01-REQ-045](#si01-req-045) | req | 8 | 0 | 0 |
| [SI01-REQ-046](#si01-req-046) | req | 2 | 0 | 0 |
| [SI01-REQ-047](#si01-req-047) | req | 4 | 1 | 0 |
| [SI01-REQ-048](#si01-req-048) | req | 1 | 0 | 0 |
| [SharedTerminalHandler](#sharedterminalhandler) | arch | 0 | 0 | 1 |
| [SimulatedAntenna](#simulatedantenna) | arch | 0 | 0 | 1 |
| [StageStartTimes](#stagestarttimes) | arch | 0 | 0 | 1 |
| [StageTiming](#stagetiming) | arch | 0 | 0 | 1 |
| [Storage](#storage) | arch | 0 | 0 | 1 |
| [SystemStatus](#systemstatus) | arch | 0 | 0 | 1 |
| [SystemUpstreamMessagePort](#systemupstreammessageport) | arch | 0 | 0 | 1 |
| [TagProcessor](#tagprocessor) | arch | 0 | 0 | 1 |
| [TimeSource](#timesource) | arch | 0 | 0 | 1 |
| [TimingData](#timingdata) | arch | 0 | 0 | 1 |
| [TimingNode](#timingnode) | arch | 3 | 0 | 1 |
| [TimingNodeUpstreamMessagePort](#timingnodeupstreammessageport) | arch | 0 | 0 | 1 |
| [TimingSystem](#timingsystem) | arch | 0 | 0 | 1 |
| [UC-001](#uc-001) | uc | 0 | 4 | 0 |
| [UC-002](#uc-002) | uc | 0 | 1 | 0 |
| [UC-003](#uc-003) | uc | 0 | 3 | 0 |
| [UC-004](#uc-004) | uc | 0 | 0 | 0 |
| [UC-005](#uc-005) | uc | 0 | 0 | 0 |
| [UC-006](#uc-006) | uc | 0 | 0 | 0 |
| [UC-007](#uc-007) | uc | 0 | 0 | 0 |
| [UC-008](#uc-008) | uc | 0 | 4 | 0 |
| [UC-009](#uc-009) | uc | 0 | 5 | 0 |
| [UC-010](#uc-010) | uc | 0 | 0 | 0 |
| [UC-011](#uc-011) | uc | 0 | 2 | 0 |
| [UC-012](#uc-012) | uc | 0 | 1 | 0 |
| [UC-013](#uc-013) | uc | 0 | 2 | 0 |
| [UC-014](#uc-014) | uc | 0 | 1 | 0 |
| [UC-015](#uc-015) | uc | 0 | 0 | 0 |
| [UC-016](#uc-016) | uc | 0 | 0 | 0 |
| [UC-017](#uc-017) | uc | 0 | 0 | 0 |
| [UC-018](#uc-018) | uc | 0 | 0 | 0 |
| [UC-019](#uc-019) | uc | 0 | 0 | 0 |
| [UpstreamGateway](#upstreamgateway) | arch | 0 | 0 | 1 |
| [UpstreamMessageRouter](#upstreammessagerouter) | arch | 0 | 0 | 1 |
| [UpstreamProtocol](#upstreamprotocol) | arch | 0 | 0 | 1 |
| [VC-ST1-001](#vc-st1-001) | vc | 11 | 0 | 0 |
| [VC-ST1-002](#vc-st1-002) | vc | 10 | 0 | 0 |
| [VC-ST1-003](#vc-st1-003) | vc | 2 | 0 | 0 |
| [VendorAntenna](#vendorantenna) | arch | 0 | 0 | 1 |
| [Web](#web) | arch | 0 | 0 | 1 |

## Antenna

Type: arch (Architecture Element)  
Title: Antenna  
Source: docs/41-01-SSD-timing-application-specification-document.md:904

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:291 (diagram=layered-architecture, node=devices-io)

## AntennaManager

Type: arch (Architecture Element)  
Title: AntennaManager  
Source: docs/41-01-SSD-timing-application-specification-document.md:896

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:288 (diagram=layered-architecture, node=devices-io)

## Api

Type: arch (Architecture Element)  
Title: API  
Source: docs/41-01-SSD-timing-application-specification-document.md:529

### Authored outgoing

- satisfies -> **IF03-REQ-001**
- satisfies -> **IF03-REQ-002**
- satisfies -> **IF03-REQ-004**
- satisfies -> **SI01-REQ-031**

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:124 (diagram=layered-architecture, node=remote-api)

## Application

Type: arch (Architecture Element)  
Title: Application  
Source: docs/41-01-SSD-timing-application-specification-document.md:447

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:382 (diagram=layered-architecture, node=timing-application-runtime)

## Beeper

Type: arch (Architecture Element)  
Title: Beeper  
Source: docs/41-01-SSD-timing-application-specification-document.md:965

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:310 (diagram=layered-architecture, node=devices-io)

## CanNetworkController

Type: arch (Architecture Element)  
Title: CanNetworkController  
Source: docs/41-01-SSD-timing-application-specification-document.md:972

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:322 (diagram=layered-architecture, node=device-network-io)

## CommandHandler

Type: arch (Architecture Element)  
Title: CommandHandler  
Source: docs/41-01-SSD-timing-application-specification-document.md:615

### Authored outgoing

- satisfies -> **IF03-REQ-001**
- satisfies -> **IF03-REQ-004**
- satisfies -> **SI01-REQ-022**
- satisfies -> **SI01-REQ-030**
- satisfies -> **SI01-REQ-031**

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:149 (diagram=layered-architecture, node=command-handler)

## Composition

Type: arch (Architecture Element)  
Title: Composition  
Source: docs/41-01-SSD-timing-application-specification-document.md:436

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:390 (diagram=layered-architecture, node=runtime-composition)

## Conductor

Type: arch (Architecture Element)  
Title: Conductor  
Source: docs/41-01-SSD-timing-application-specification-document.md:609

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:141 (diagram=layered-architecture, node=application-conductor)

## Connector

Type: arch (Architecture Element)  
Title: Connector  
Source: docs/41-01-SSD-timing-application-specification-document.md:994

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:337 (diagram=layered-architecture, node=messaging-io)

## Console

Type: arch (Architecture Element)  
Title: Console  
Source: docs/41-01-SSD-timing-application-specification-document.md:559

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:100 (diagram=layered-architecture, node=local-console)

## DebugConnector

Type: arch (Architecture Element)  
Title: DebugConnector  
Source: docs/41-01-SSD-timing-application-specification-document.md:1009

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:342 (diagram=layered-architecture, node=messaging-io)

## DeviceNetworks

Type: arch (Architecture Element)  
Title: DeviceNetworks  
Source: docs/41-01-SSD-timing-application-specification-document.md:861

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:317 (diagram=layered-architecture, node=device-network-io)

## Devices

Type: arch (Architecture Element)  
Title: Devices  
Source: docs/41-01-SSD-timing-application-specification-document.md:850

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:283 (diagram=layered-architecture, node=devices-io)

## Display

Type: arch (Architecture Element)  
Title: Display  
Source: docs/41-01-SSD-timing-application-specification-document.md:929

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:298 (diagram=layered-architecture, node=devices-io)

## IF03-REQ-001

Type: ifreq (Interface Requirement)  
Title: Shared semantics  
Source: docs/32-03-ISD-application-control-status.md:479

### Authored outgoing

- derived_from -> **SI01-REQ-022**
- derived_from -> **SI01-REQ-030**

### Generated incoming

- satisfies <- **Api**
- satisfies <- **CommandHandler**

### Diagram references

_None._

## IF03-REQ-002

Type: ifreq (Interface Requirement)  
Title: Remote-host operation  
Source: docs/32-03-ISD-application-control-status.md:490

### Authored outgoing

- derived_from -> **SI01-REQ-031**

### Generated incoming

- satisfies <- **Api**

### Diagram references

_None._

## IF03-REQ-003

Type: ifreq (Interface Requirement)  
Title: Version query  
Source: docs/32-03-ISD-application-control-status.md:501

### Authored outgoing

- derived_from -> **SI01-REQ-010**
- derived_from -> **SI01-REQ-011**

### Generated incoming

- verifies <- **VC-ST1-001**

### Diagram references

_None._

## IF03-REQ-004

Type: ifreq (Interface Requirement)  
Title: Status query  
Source: docs/32-03-ISD-application-control-status.md:509

### Authored outgoing

- derived_from -> **SI01-REQ-020**
- derived_from -> **SI01-REQ-021**
- derived_from -> **SI01-REQ-022**

### Generated incoming

- satisfies <- **Api**
- satisfies <- **CommandHandler**
- verifies <- **VC-ST1-001**

### Diagram references

_None._

## IF03-REQ-005

Type: ifreq (Interface Requirement)  
Title: Live status/event delivery  
Source: docs/32-03-ISD-application-control-status.md:518

### Authored outgoing

- derived_from -> **SI01-REQ-023**

### Generated incoming

- verifies <- **VC-ST1-001**

### Diagram references

_None._

## IF03-REQ-006

Type: ifreq (Interface Requirement)  
Title: Reconnect to current state  
Source: docs/32-03-ISD-application-control-status.md:526

### Authored outgoing

- derived_from -> **SI01-REQ-023**

### Generated incoming

- verifies <- **VC-ST1-001**

### Diagram references

_None._

## IF03-REQ-007

Type: ifreq (Interface Requirement)  
Title: Machine-readable representation  
Source: docs/32-03-ISD-application-control-status.md:534

### Authored outgoing

- derived_from -> **SI01-REQ-031**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-008

Type: ifreq (Interface Requirement)  
Title: Explicit failure response  
Source: docs/32-03-ISD-application-control-status.md:542

### Authored outgoing

- derived_from -> **SI01-REQ-031**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-009

Type: ifreq (Interface Requirement)  
Title: Safe default listen scope  
Source: docs/32-03-ISD-application-control-status.md:550

### Authored outgoing

- derived_from -> **SI01-REQ-032**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-010

Type: ifreq (Interface Requirement)  
Title: Compatible extension  
Source: docs/32-03-ISD-application-control-status.md:558

### Authored outgoing

- derived_from -> **SI01-REQ-033**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-011

Type: ifreq (Interface Requirement)  
Title: Step-4 location and lifecycle control  
Source: docs/32-03-ISD-application-control-status.md:566

### Authored outgoing

- derived_from -> **SI01-REQ-040**

### Generated incoming

- verifies <- **VC-ST1-002**

### Diagram references

_None._

## IF03-REQ-012

Type: ifreq (Interface Requirement)  
Title: Engineering capability discovery  
Source: docs/32-03-ISD-application-control-status.md:577

### Authored outgoing

- derived_from -> **SI01-REQ-043**

### Generated incoming

- verifies <- **VC-ST1-002**

### Diagram references

_None._

## IF03-REQ-013

Type: ifreq (Interface Requirement)  
Title: Dev auto-reg control  
Source: docs/32-03-ISD-application-control-status.md:587

### Authored outgoing

- derived_from -> **SI01-REQ-041**
- derived_from -> **SI01-REQ-043**

### Generated incoming

- verifies <- **VC-ST1-002**

### Diagram references

_None._

## IF03-REQ-014

Type: ifreq (Interface Requirement)  
Title: Committed LogBook query  
Source: docs/32-03-ISD-application-control-status.md:597

### Authored outgoing

- derived_from -> **SI01-REQ-042**

### Generated incoming

- verifies <- **VC-ST1-002**

### Diagram references

_None._

## IF03-REQ-015

Type: ifreq (Interface Requirement)  
Title: Live committed TimingData delivery  
Source: docs/32-03-ISD-application-control-status.md:606

### Authored outgoing

- derived_from -> **SI01-REQ-042**

### Generated incoming

- verifies <- **VC-ST1-002**

### Diagram references

_None._

## IF03-REQ-016

Type: ifreq (Interface Requirement)  
Title: Rebuild LogBook before live presentation  
Source: docs/32-03-ISD-application-control-status.md:616

### Authored outgoing

- derived_from -> **SI01-REQ-044**

### Generated incoming

- verifies <- **VC-ST1-003**

### Diagram references

_None._

## IF05-REQ-001

Type: ifreq (Interface Requirement)  
Title: Common TimingData envelope  
Source: docs/32-05-ISD-timingdata-interchange.md:195

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-045**

### Diagram references

_None._

## IF05-REQ-002

Type: ifreq (Interface Requirement)  
Title: Record identity within a TimingSystem  
Source: docs/32-05-ISD-timingdata-interchange.md:204

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-045**
- derived_from <- **SI01-REQ-047**

### Diagram references

_None._

## IF05-REQ-003

Type: ifreq (Interface Requirement)  
Title: Sequence progression  
Source: docs/32-05-ISD-timingdata-interchange.md:213

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-045**
- derived_from <- **SI01-REQ-047**

### Diagram references

_None._

## IF05-REQ-004

Type: ifreq (Interface Requirement)  
Title: Automatic and manual registration  
Source: docs/32-05-ISD-timingdata-interchange.md:222

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-045**

### Diagram references

_None._

## IF05-REQ-005

Type: ifreq (Interface Requirement)  
Title: Registration record values  
Source: docs/32-05-ISD-timingdata-interchange.md:230

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-045**

### Diagram references

_None._

## IF05-REQ-006

Type: ifreq (Interface Requirement)  
Title: Registration add and revoke  
Source: docs/32-05-ISD-timingdata-interchange.md:238

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-045**

### Diagram references

_None._

## IF05-REQ-007

Type: ifreq (Interface Requirement)  
Title: Committed record immutability  
Source: docs/32-05-ISD-timingdata-interchange.md:248

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-045**
- derived_from <- **SI01-REQ-047**

### Diagram references

_None._

## Keypad

Type: arch (Architecture Element)  
Title: Keypad  
Source: docs/41-01-SSD-timing-application-specification-document.md:951

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:305 (diagram=layered-architecture, node=devices-io)

## LogBook

Type: arch (Architecture Element)  
Title: LogBook  
Source: docs/41-01-SSD-timing-application-specification-document.md:1139

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:234 (diagram=layered-architecture, node=logbook-domain)

## Logging

Type: arch (Architecture Element)  
Title: Logging  
Source: docs/41-01-SSD-timing-application-specification-document.md:1079

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:406 (diagram=layered-architecture, node=logging-infra)

## LoggingServer

Type: arch (Architecture Element)  
Title: LoggingServer  
Source: docs/41-01-SSD-timing-application-specification-document.md:1089

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:398 (diagram=layered-architecture, node=logging-server)

## Messaging

Type: arch (Architecture Element)  
Title: Messaging  
Source: docs/41-01-SSD-timing-application-specification-document.md:875

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:329 (diagram=layered-architecture, node=messaging-io)

## NetworkDeviceService

Type: arch (Architecture Element)  
Title: NetworkDeviceService  
Source: docs/41-01-SSD-timing-application-specification-document.md:979

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:324 (diagram=layered-architecture, node=device-network-io)

## NextUpTeams

Type: arch (Architecture Element)  
Title: NextUpTeams  
Source: docs/41-01-SSD-timing-application-specification-document.md:740

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:209 (diagram=layered-architecture, node=next-up-teams)

## PlatformEnvironment

Type: arch (Architecture Element)  
Title: PlatformEnvironment  
Source: docs/41-01-SSD-timing-application-specification-document.md:1058

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:368 (diagram=layered-architecture, node=platform-environment)

## PlatformEvents

Type: arch (Architecture Element)  
Title: PlatformEvents  
Source: docs/41-01-SSD-timing-application-specification-document.md:1050

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:358 (diagram=layered-architecture, node=platform-events)

## PlatformExecution

Type: arch (Architecture Element)  
Title: PlatformExecution  
Source: docs/41-01-SSD-timing-application-specification-document.md:1042

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:348 (diagram=layered-architecture, node=platform-execution)

## RabbitMqConnector

Type: arch (Architecture Element)  
Title: RabbitMqConnector  
Source: docs/41-01-SSD-timing-application-specification-document.md:1002

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:340 (diagram=layered-architecture, node=messaging-io)

## RaceData

Type: arch (Architecture Element)  
Title: RaceData  
Source: docs/41-01-SSD-timing-application-specification-document.md:746

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:217 (diagram=layered-architecture, node=race-data)

## RemoteShell

Type: arch (Architecture Element)  
Title: RemoteShell  
Source: docs/41-01-SSD-timing-application-specification-document.md:568

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:108 (diagram=layered-architecture, node=remote-shell)

## Rev1CanDisplay

Type: arch (Architecture Element)  
Title: Rev1CanDisplay  
Source: docs/41-01-SSD-timing-application-specification-document.md:937

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:301 (diagram=layered-architecture, node=devices-io)

## Rev1CanKeypad

Type: arch (Architecture Element)  
Title: Rev1CanKeypad  
Source: docs/41-01-SSD-timing-application-specification-document.md:958

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:308 (diagram=layered-architecture, node=devices-io)

## Rev2WifiDisplay

Type: arch (Architecture Element)  
Title: Rev2WifiDisplay  
Source: docs/41-01-SSD-timing-application-specification-document.md:944

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:303 (diagram=layered-architecture, node=devices-io)

## SI01-REQ-001

Type: req (Requirement)  
Title: Start from external configuration  
Source: docs/41-01-SSD-timing-application-specification-document.md:64

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-002

Type: req (Requirement)  
Title: Clean process shutdown  
Source: docs/41-01-SSD-timing-application-specification-document.md:71

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-003

Type: req (Requirement)  
Title: Minimal TimingSystem / TimingNode composition  
Source: docs/41-01-SSD-timing-application-specification-document.md:78

### Authored outgoing

- derived_from -> **UC-001**
- derived_from -> **UC-014**

### Generated incoming

- satisfies <- **TimingNode**
- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-010

Type: req (Requirement)  
Title: Single application build identity  
Source: docs/41-01-SSD-timing-application-specification-document.md:93

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **IF03-REQ-003**
- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-011

Type: req (Requirement)  
Title: Consistent identity across interfaces  
Source: docs/41-01-SSD-timing-application-specification-document.md:100

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **IF03-REQ-003**

### Diagram references

_None._

## SI01-REQ-020

Type: req (Requirement)  
Title: Authoritative current status snapshot  
Source: docs/41-01-SSD-timing-application-specification-document.md:111

### Authored outgoing

- derived_from -> **UC-001**
- derived_from -> **UC-008**

### Generated incoming

- derived_from <- **IF03-REQ-004**
- satisfies <- **TimingNode**
- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-021

Type: req (Requirement)  
Title: Minimum first-executable status content  
Source: docs/41-01-SSD-timing-application-specification-document.md:120

### Authored outgoing

- derived_from -> **UC-001**
- derived_from -> **UC-008**

### Generated incoming

- derived_from <- **IF03-REQ-004**
- satisfies <- **TimingNode**
- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-022

Type: req (Requirement)  
Title: Equivalent status semantics across first interfaces  
Source: docs/41-01-SSD-timing-application-specification-document.md:140

### Authored outgoing

- derived_from -> **UC-008**

### Generated incoming

- derived_from <- **IF03-REQ-001**
- derived_from <- **IF03-REQ-004**
- satisfies <- **CommandHandler**

### Diagram references

_None._

## SI01-REQ-023

Type: req (Requirement)  
Title: Status-change publication  
Source: docs/41-01-SSD-timing-application-specification-document.md:152

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **IF03-REQ-005**
- derived_from <- **IF03-REQ-006**

### Diagram references

_None._

## SI01-REQ-030

Type: req (Requirement)  
Title: Shared application behaviour  
Source: docs/41-01-SSD-timing-application-specification-document.md:163

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **IF03-REQ-001**
- satisfies <- **CommandHandler**

### Diagram references

_None._

## SI01-REQ-031

Type: req (Requirement)  
Title: Externally testable executable  
Source: docs/41-01-SSD-timing-application-specification-document.md:172

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **IF03-REQ-002**
- derived_from <- **IF03-REQ-007**
- derived_from <- **IF03-REQ-008**
- satisfies <- **Api**
- satisfies <- **CommandHandler**
- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-032

Type: req (Requirement)  
Title: Safe default network exposure  
Source: docs/41-01-SSD-timing-application-specification-document.md:182

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **IF03-REQ-009**

### Diagram references

_None._

## SI01-REQ-033

Type: req (Requirement)  
Title: Compatible first API evolution  
Source: docs/41-01-SSD-timing-application-specification-document.md:189

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **IF03-REQ-010**

### Diagram references

_None._

## SI01-REQ-040

Type: req (Requirement)  
Title: Operational location and lifecycle  
Source: docs/41-01-SSD-timing-application-specification-document.md:198

### Authored outgoing

- derived_from -> **UC-001**
- derived_from -> **UC-002**
- derived_from -> **UC-008**
- derived_from -> **UC-009**

### Generated incoming

- derived_from <- **IF03-REQ-011**
- verifies <- **VC-ST1-002**

### Diagram references

_None._

## SI01-REQ-041

Type: req (Requirement)  
Title: Accepted semantic registration operation  
Source: docs/41-01-SSD-timing-application-specification-document.md:209

### Authored outgoing

- derived_from -> **UC-003**
- derived_from -> **UC-009**

### Generated incoming

- derived_from <- **IF03-REQ-013**
- verifies <- **VC-ST1-002**

### Diagram references

_None._

## SI01-REQ-042

Type: req (Requirement)  
Title: Committed registration observability  
Source: docs/41-01-SSD-timing-application-specification-document.md:220

### Authored outgoing

- derived_from -> **UC-003**
- derived_from -> **UC-009**
- derived_from -> **UC-011**

### Generated incoming

- derived_from <- **IF03-REQ-014**
- derived_from <- **IF03-REQ-015**
- verifies <- **VC-ST1-002**

### Diagram references

_None._

## SI01-REQ-043

Type: req (Requirement)  
Title: Capability-gated dev auto-reg  
Source: docs/41-01-SSD-timing-application-specification-document.md:230

### Authored outgoing

- derived_from -> **UC-009**

### Generated incoming

- derived_from <- **IF03-REQ-012**
- derived_from <- **IF03-REQ-013**
- verifies <- **VC-ST1-002**

### Diagram references

_None._

## SI01-REQ-044

Type: req (Requirement)  
Title: Reconnect rebuild before live presentation  
Source: docs/41-01-SSD-timing-application-specification-document.md:242

### Authored outgoing

- derived_from -> **UC-009**

### Generated incoming

- derived_from <- **IF03-REQ-016**
- verifies <- **VC-ST1-003**

### Diagram references

_None._

## SI01-REQ-045

Type: req (Requirement)  
Title: Reference TimingData representation support  
Source: docs/41-01-SSD-timing-application-specification-document.md:253

### Authored outgoing

- derived_from -> **IF05-REQ-001**
- derived_from -> **IF05-REQ-002**
- derived_from -> **IF05-REQ-003**
- derived_from -> **IF05-REQ-004**
- derived_from -> **IF05-REQ-005**
- derived_from -> **IF05-REQ-006**
- derived_from -> **IF05-REQ-007**
- derived_from -> **UC-011**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-046

Type: req (Requirement)  
Title: Write TimingData before commit completion  
Source: docs/41-01-SSD-timing-application-specification-document.md:264

### Authored outgoing

- derived_from -> **UC-003**
- derived_from -> **UC-012**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-047

Type: req (Requirement)  
Title: Restore committed TimingData after restart  
Source: docs/41-01-SSD-timing-application-specification-document.md:278

### Authored outgoing

- derived_from -> **IF05-REQ-002**
- derived_from -> **IF05-REQ-003**
- derived_from -> **IF05-REQ-007**
- derived_from -> **UC-013**

### Generated incoming

- verifies <- **VC-ST1-002**

### Diagram references

_None._

## SI01-REQ-048

Type: req (Requirement)  
Title: Reject invalid TimingData recovery input  
Source: docs/41-01-SSD-timing-application-specification-document.md:293

### Authored outgoing

- derived_from -> **UC-013**

### Generated incoming

_None._

### Diagram references

_None._

## SharedTerminalHandler

Type: arch (Architecture Element)  
Title: SharedTerminalHandler  
Source: docs/41-01-SSD-timing-application-specification-document.md:576

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:132 (diagram=layered-architecture, node=shared-terminal)

## SimulatedAntenna

Type: arch (Architecture Element)  
Title: SimulatedAntenna  
Source: docs/41-01-SSD-timing-application-specification-document.md:912

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:294 (diagram=layered-architecture, node=devices-io)

## StageStartTimes

Type: arch (Architecture Element)  
Title: StageStartTimes  
Source: docs/41-01-SSD-timing-application-specification-document.md:734

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:201 (diagram=layered-architecture, node=stage-start-times)

## StageTiming

Type: arch (Architecture Element)  
Title: StageTiming  
Source: docs/41-01-SSD-timing-application-specification-document.md:753

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:225 (diagram=layered-architecture, node=stage-timing)

## Storage

Type: arch (Architecture Element)  
Title: Storage  
Source: docs/41-01-SSD-timing-application-specification-document.md:844

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:270 (diagram=layered-architecture, node=storage-io)

## SystemStatus

Type: arch (Architecture Element)  
Title: SystemStatus  
Source: docs/41-01-SSD-timing-application-specification-document.md:1115

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:175 (diagram=layered-architecture, node=system-status-domain)

## SystemUpstreamMessagePort

Type: arch (Architecture Element)  
Title: TimingSystem UpstreamMessagePort  
Source: docs/41-01-SSD-timing-application-specification-document.md:706

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:166 (diagram=layered-architecture, node=system-upstream-message-port)

## TagProcessor

Type: arch (Architecture Element)  
Title: TagProcessor  
Source: docs/41-01-SSD-timing-application-specification-document.md:724

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:193 (diagram=layered-architecture, node=tag-processor)

## TimeSource

Type: arch (Architecture Element)  
Title: TimeSource  
Source: docs/41-01-SSD-timing-application-specification-document.md:1169

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:261 (diagram=layered-architecture, node=time-source-domain)

## TimingData

Type: arch (Architecture Element)  
Title: TimingData  
Source: docs/41-01-SSD-timing-application-specification-document.md:1148

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:243 (diagram=layered-architecture, node=timing-data-domain)

## TimingNode

Type: arch (Architecture Element)  
Title: TimingNode  
Source: docs/41-01-SSD-timing-application-specification-document.md:1126

### Authored outgoing

- satisfies -> **SI01-REQ-003**
- satisfies -> **SI01-REQ-020**
- satisfies -> **SI01-REQ-021**

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:58 (diagram=layered-architecture, node=timing-node-aggregate)

## TimingNodeUpstreamMessagePort

Type: arch (Architecture Element)  
Title: TimingNode UpstreamMessagePort  
Source: docs/41-01-SSD-timing-application-specification-document.md:715

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:184 (diagram=layered-architecture, node=upstream-message-port)

## TimingSystem

Type: arch (Architecture Element)  
Title: TimingSystem  
Source: docs/41-01-SSD-timing-application-specification-document.md:1102

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:49 (diagram=layered-architecture, node=timing-system-aggregate)

## UC-001

Type: uc (Use Case)  
Title: Connect to a registration system  
Source: docs/30-UC-system-use-cases.md:108

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-003**
- derived_from <- **SI01-REQ-020**
- derived_from <- **SI01-REQ-021**
- derived_from <- **SI01-REQ-040**

### Diagram references

_None._

## UC-002

Type: uc (Use Case)  
Title: Configure, open and close a registration point  
Source: docs/30-UC-system-use-cases.md:145

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-040**

### Diagram references

_None._

## UC-003

Type: uc (Use Case)  
Title: Register a participant through RFID  
Source: docs/30-UC-system-use-cases.md:188

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-041**
- derived_from <- **SI01-REQ-042**
- derived_from <- **SI01-REQ-046**

### Diagram references

_None._

## UC-004

Type: uc (Use Case)  
Title: Recover or reinitialise RFID equipment  
Source: docs/30-UC-system-use-cases.md:235

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## UC-005

Type: uc (Use Case)  
Title: Manage ready teams through keypad/operator input  
Source: docs/30-UC-system-use-cases.md:253

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## UC-006

Type: uc (Use Case)  
Title: Drive a passive CAN display from current system state  
Source: docs/30-UC-system-use-cases.md:272

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## UC-007

Type: uc (Use Case)  
Title: Provide data to a smart network display  
Source: docs/30-UC-system-use-cases.md:289

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## UC-008

Type: uc (Use Case)  
Title: Operate SI-01 through a desktop GUI  
Source: docs/30-UC-system-use-cases.md:308

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-020**
- derived_from <- **SI01-REQ-021**
- derived_from <- **SI01-REQ-022**
- derived_from <- **SI01-REQ-040**

### Diagram references

_None._

## UC-009

Type: uc (Use Case)  
Title: Exercise the registration system through the Engineering Client  
Source: docs/30-UC-system-use-cases.md:446

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-040**
- derived_from <- **SI01-REQ-041**
- derived_from <- **SI01-REQ-042**
- derived_from <- **SI01-REQ-043**
- derived_from <- **SI01-REQ-044**

### Diagram references

_None._

## UC-010

Type: uc (Use Case)  
Title: Synchronise reference data from backoffice  
Source: docs/30-UC-system-use-cases.md:336

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## UC-011

Type: uc (Use Case)  
Title: Synchronise TimingNodeId-scoped data to backoffice  
Source: docs/30-UC-system-use-cases.md:358

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-042**
- derived_from <- **SI01-REQ-045**

### Diagram references

_None._

## UC-012

Type: uc (Use Case)  
Title: Continue local operation during backoffice outage  
Source: docs/30-UC-system-use-cases.md:383

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-046**

### Diagram references

_None._

## UC-013

Type: uc (Use Case)  
Title: Restart and restore local state  
Source: docs/30-UC-system-use-cases.md:400

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-047**
- derived_from <- **SI01-REQ-048**

### Diagram references

_None._

## UC-014

Type: uc (Use Case)  
Title: Run multiple TimingNodes in one process  
Source: docs/30-UC-system-use-cases.md:418

### Authored outgoing

_None._

### Generated incoming

- derived_from <- **SI01-REQ-003**

### Diagram references

_None._

## UC-015

Type: uc (Use Case)  
Title: Simulate a complete field toward backoffice  
Source: docs/30-UC-system-use-cases.md:488

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## UC-016

Type: uc (Use Case)  
Title: Replace real devices with controllable stubs  
Source: docs/30-UC-system-use-cases.md:505

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## UC-017

Type: uc (Use Case)  
Title: Use an alternative backoffice transport for loop testing  
Source: docs/30-UC-system-use-cases.md:521

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## UC-018

Type: uc (Use Case)  
Title: Verify production-shaped messaging through RabbitMQ  
Source: docs/30-UC-system-use-cases.md:541

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## UC-019

Type: uc (Use Case)  
Title: Handle provider-specific input classification  
Source: docs/30-UC-system-use-cases.md:561

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## UpstreamGateway

Type: arch (Architecture Element)  
Title: UpstreamGateway  
Source: docs/41-01-SSD-timing-application-specification-document.md:987

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:334 (diagram=layered-architecture, node=messaging-io)

## UpstreamMessageRouter

Type: arch (Architecture Element)  
Title: UpstreamMessageRouter  
Source: docs/41-01-SSD-timing-application-specification-document.md:633

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:157 (diagram=layered-architecture, node=upstream-message-router)

## UpstreamProtocol

Type: arch (Architecture Element)  
Title: UpstreamProtocol  
Source: docs/41-01-SSD-timing-application-specification-document.md:1159

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:252 (diagram=layered-architecture, node=upstream-protocol-domain)

## VC-ST1-001

Type: vc (Verification Case)  
Title: Query and resynchronise first-executable status  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:70

### Authored outgoing

- verifies -> **IF03-REQ-003**
- verifies -> **IF03-REQ-004**
- verifies -> **IF03-REQ-005**
- verifies -> **IF03-REQ-006**
- verifies -> **SI01-REQ-001**
- verifies -> **SI01-REQ-002**
- verifies -> **SI01-REQ-003**
- verifies -> **SI01-REQ-010**
- verifies -> **SI01-REQ-020**
- verifies -> **SI01-REQ-021**
- verifies -> **SI01-REQ-031**

### Generated incoming

_None._

### Diagram references

_None._

## VC-ST1-002

Type: vc (Verification Case)  
Title: Control and observe first committed registration  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:126

### Authored outgoing

- verifies -> **IF03-REQ-011**
- verifies -> **IF03-REQ-012**
- verifies -> **IF03-REQ-013**
- verifies -> **IF03-REQ-014**
- verifies -> **IF03-REQ-015**
- verifies -> **SI01-REQ-040**
- verifies -> **SI01-REQ-041**
- verifies -> **SI01-REQ-042**
- verifies -> **SI01-REQ-043**
- verifies -> **SI01-REQ-047**

### Generated incoming

_None._

### Diagram references

_None._

## VC-ST1-003

Type: vc (Verification Case)  
Title: Engineering Client reconnect/resynchronisation integration  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:204

### Authored outgoing

- verifies -> **IF03-REQ-016**
- verifies -> **SI01-REQ-044**

### Generated incoming

_None._

### Diagram references

_None._

## VendorAntenna

Type: arch (Architecture Element)  
Title: VendorAntenna  
Source: docs/41-01-SSD-timing-application-specification-document.md:919

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:296 (diagram=layered-architecture, node=devices-io)

## Web

Type: arch (Architecture Element)  
Title: Web  
Source: docs/41-01-SSD-timing-application-specification-document.md:546

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:116 (diagram=layered-architecture, node=web-interface)
