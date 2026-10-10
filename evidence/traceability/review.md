# Engineering graph review

Source revision: f8182beec8d5634e7f288e74166744a594d38614
Source graph: sphinx-needs Event timing engineering graph migration-013

Engineering objects and outgoing relations come from the Sphinx-Needs export.
Incoming relations below are derived from those outgoing relations.
Diagram identities are references to existing engineering objects.

## Overview

| Object | Type | Authored outgoing | Generated incoming | Diagram refs |
| --- | --- | ---: | ---: | ---: |
| [Antenna](#antenna) | arch | 0 | 1 | 1 |
| [AntennaManager](#antennamanager) | arch | 0 | 1 | 1 |
| [Api](#api) | arch | 4 | 1 | 1 |
| [ApplicationConductor](#applicationconductor) | arch | 0 | 0 | 1 |
| [ApplicationConfiguration](#applicationconfiguration) | arch | 0 | 1 | 1 |
| [Beeper](#beeper) | arch | 0 | 0 | 1 |
| [CanNetworkController](#cannetworkcontroller) | arch | 0 | 1 | 1 |
| [ClockTimeSource](#clocktimesource) | arch | 0 | 1 | 1 |
| [Configuration](#configuration) | arch | 0 | 1 | 1 |
| [ConfigurationControl](#configurationcontrol) | arch | 0 | 1 | 1 |
| [Connector](#connector) | arch | 0 | 0 | 1 |
| [Console](#console) | arch | 0 | 1 | 1 |
| [CooperativeTaskController](#cooperativetaskcontroller) | arch | 0 | 1 | 1 |
| [DD-AntennaRuntime](#dd-antennaruntime) | design | 5 | 0 | 0 |
| [DD-CooperativeExecution](#dd-cooperativeexecution) | design | 5 | 0 | 0 |
| [DD-DependencyPlacement](#dd-dependencyplacement) | design | 0 | 0 | 0 |
| [DD-DomainIntegration](#dd-domainintegration) | design | 7 | 0 | 0 |
| [DD-EventTagProcessing](#dd-eventtagprocessing) | design | 2 | 0 | 0 |
| [DD-ExecutableComposition](#dd-executablecomposition) | design | 6 | 0 | 0 |
| [DD-ExtensionAndComposition](#dd-extensionandcomposition) | design | 2 | 0 | 0 |
| [DD-IOComposition](#dd-iocomposition) | design | 3 | 0 | 0 |
| [DD-LoggingRuntime](#dd-loggingruntime) | design | 2 | 0 | 0 |
| [DD-PresentationAccess](#dd-presentationaccess) | design | 2 | 0 | 0 |
| [DD-RunningConfiguration](#dd-runningconfiguration) | design | 3 | 0 | 0 |
| [DD-RuntimeExecution](#dd-runtimeexecution) | design | 4 | 0 | 0 |
| [DD-RuntimeWorkAndMeasurements](#dd-runtimeworkandmeasurements) | design | 4 | 0 | 0 |
| [DD-TimingDataProfiles](#dd-timingdataprofiles) | design | 1 | 0 | 0 |
| [DD-TimingNodeExecution](#dd-timingnodeexecution) | design | 5 | 0 | 0 |
| [DD-TimingTimeComposition](#dd-timingtimecomposition) | design | 5 | 0 | 0 |
| [DebugConnector](#debugconnector) | arch | 0 | 0 | 1 |
| [DeviceNetworks](#devicenetworks) | arch | 0 | 0 | 1 |
| [Devices](#devices) | arch | 0 | 0 | 1 |
| [Display](#display) | arch | 0 | 0 | 1 |
| [Event](#event) | arch | 0 | 1 | 1 |
| [EventData](#eventdata) | arch | 0 | 2 | 1 |
| [EventSource](#eventsource) | arch | 0 | 1 | 1 |
| [IF03-REQ-001](#if03-req-001) | ifreq | 0 | 3 | 0 |
| [IF03-REQ-002](#if03-req-002) | ifreq | 0 | 2 | 0 |
| [IF03-REQ-003](#if03-req-003) | ifreq | 1 | 2 | 0 |
| [IF03-REQ-004](#if03-req-004) | ifreq | 1 | 5 | 0 |
| [IF03-REQ-005](#if03-req-005) | ifreq | 1 | 2 | 0 |
| [IF03-REQ-006](#if03-req-006) | ifreq | 1 | 4 | 0 |
| [IF03-REQ-007](#if03-req-007) | ifreq | 0 | 1 | 0 |
| [IF03-REQ-008](#if03-req-008) | ifreq | 1 | 3 | 0 |
| [IF03-REQ-009](#if03-req-009) | ifreq | 0 | 1 | 0 |
| [IF03-REQ-010](#if03-req-010) | ifreq | 0 | 0 | 0 |
| [IF03-REQ-011](#if03-req-011) | ifreq | 2 | 6 | 0 |
| [IF03-REQ-012](#if03-req-012) | ifreq | 1 | 1 | 0 |
| [IF03-REQ-013](#if03-req-013) | ifreq | 2 | 3 | 0 |
| [IF03-REQ-014](#if03-req-014) | ifreq | 1 | 7 | 0 |
| [IF03-REQ-015](#if03-req-015) | ifreq | 1 | 6 | 0 |
| [IF03-REQ-016](#if03-req-016) | ifreq | 1 | 2 | 0 |
| [IF03-REQ-017](#if03-req-017) | ifreq | 2 | 2 | 0 |
| [IF03-REQ-018](#if03-req-018) | ifreq | 1 | 0 | 0 |
| [IF03-REQ-019](#if03-req-019) | ifreq | 1 | 0 | 0 |
| [IF03-REQ-020](#if03-req-020) | ifreq | 1 | 0 | 0 |
| [IF03-REQ-021](#if03-req-021) | ifreq | 0 | 1 | 0 |
| [IF03-REQ-022](#if03-req-022) | ifreq | 0 | 2 | 0 |
| [IF03-REQ-023](#if03-req-023) | ifreq | 1 | 0 | 0 |
| [IF03-REQ-024](#if03-req-024) | ifreq | 0 | 0 | 0 |
| [IF04-REQ-001](#if04-req-001) | ifreq | 0 | 0 | 0 |
| [IF04-REQ-002](#if04-req-002) | ifreq | 1 | 0 | 0 |
| [IF04-REQ-003](#if04-req-003) | ifreq | 1 | 0 | 0 |
| [IF04-REQ-004](#if04-req-004) | ifreq | 1 | 0 | 0 |
| [IF04-REQ-005](#if04-req-005) | ifreq | 2 | 0 | 0 |
| [IF04-REQ-006](#if04-req-006) | ifreq | 1 | 0 | 0 |
| [IF04-REQ-007](#if04-req-007) | ifreq | 0 | 0 | 0 |
| [IF04-REQ-008](#if04-req-008) | ifreq | 1 | 0 | 0 |
| [IF04-REQ-009](#if04-req-009) | ifreq | 1 | 0 | 0 |
| [IF04-REQ-010](#if04-req-010) | ifreq | 1 | 0 | 0 |
| [IF04-REQ-011](#if04-req-011) | ifreq | 0 | 0 | 0 |
| [IF04-REQ-012](#if04-req-012) | ifreq | 1 | 0 | 0 |
| [IF05-REQ-001](#if05-req-001) | ifreq | 0 | 1 | 0 |
| [IF05-REQ-002](#if05-req-002) | ifreq | 0 | 4 | 0 |
| [IF05-REQ-003](#if05-req-003) | ifreq | 0 | 7 | 0 |
| [IF05-REQ-004](#if05-req-004) | ifreq | 0 | 1 | 0 |
| [IF05-REQ-005](#if05-req-005) | ifreq | 0 | 2 | 0 |
| [IF05-REQ-006](#if05-req-006) | ifreq | 0 | 3 | 0 |
| [IF05-REQ-007](#if05-req-007) | ifreq | 0 | 4 | 0 |
| [IF05-REQ-008](#if05-req-008) | ifreq | 0 | 5 | 0 |
| [IF05-REQ-009](#if05-req-009) | ifreq | 0 | 4 | 0 |
| [IF05-REQ-010](#if05-req-010) | ifreq | 0 | 1 | 0 |
| [Keypad](#keypad) | arch | 0 | 0 | 1 |
| [LogBook](#logbook) | arch | 0 | 1 | 1 |
| [Logging](#logging) | arch | 0 | 1 | 1 |
| [LoggingServer](#loggingserver) | arch | 0 | 1 | 1 |
| [Messaging](#messaging) | arch | 0 | 0 | 1 |
| [MonotonicClock](#monotonicclock) | arch | 0 | 0 | 1 |
| [NetworkDeviceService](#networkdeviceservice) | arch | 0 | 1 | 1 |
| [NextUpTeams](#nextupteams) | arch | 0 | 0 | 1 |
| [OperatingSystem](#operatingsystem) | arch | 0 | 0 | 1 |
| [PlatformEnvironment](#platformenvironment) | arch | 0 | 1 | 1 |
| [PlatformEvents](#platformevents) | arch | 0 | 1 | 1 |
| [PlatformExecution](#platformexecution) | arch | 0 | 3 | 1 |
| [PlatformTime](#platformtime) | arch | 0 | 1 | 1 |
| [PowerDevice](#powerdevice) | arch | 0 | 1 | 1 |
| [PresentationGateway](#presentationgateway) | arch | 5 | 1 | 1 |
| [PresentationRuntime](#presentationruntime) | arch | 0 | 1 | 1 |
| [RabbitMqConnector](#rabbitmqconnector) | arch | 0 | 0 | 1 |
| [RaceData](#racedata) | arch | 0 | 0 | 1 |
| [RemoteShell](#remoteshell) | arch | 0 | 1 | 1 |
| [Rev1CanDisplay](#rev1candisplay) | arch | 0 | 0 | 1 |
| [Rev1CanKeypad](#rev1cankeypad) | arch | 0 | 0 | 1 |
| [Rev2WifiDisplay](#rev2wifidisplay) | arch | 0 | 0 | 1 |
| [RuntimeExecutors](#runtimeexecutors) | arch | 0 | 2 | 1 |
| [RuntimeTimeSources](#runtimetimesources) | arch | 0 | 1 | 1 |
| [SI01-REQ-001](#si01-req-001) | req | 0 | 4 | 0 |
| [SI01-REQ-002](#si01-req-002) | req | 0 | 1 | 0 |
| [SI01-REQ-003](#si01-req-003) | req | 2 | 5 | 0 |
| [SI01-REQ-010](#si01-req-010) | req | 0 | 1 | 0 |
| [SI01-REQ-011](#si01-req-011) | req | 0 | 0 | 0 |
| [SI01-REQ-020](#si01-req-020) | req | 1 | 2 | 0 |
| [SI01-REQ-021](#si01-req-021) | req | 3 | 2 | 0 |
| [SI01-REQ-022](#si01-req-022) | req | 3 | 1 | 0 |
| [SI01-REQ-023](#si01-req-023) | req | 4 | 3 | 0 |
| [SI01-REQ-024](#si01-req-024) | req | 4 | 12 | 0 |
| [SI01-REQ-025](#si01-req-025) | req | 5 | 4 | 0 |
| [SI01-REQ-026](#si01-req-026) | req | 5 | 3 | 0 |
| [SI01-REQ-030](#si01-req-030) | req | 0 | 1 | 0 |
| [SI01-REQ-031](#si01-req-031) | req | 2 | 5 | 0 |
| [SI01-REQ-032](#si01-req-032) | req | 0 | 0 | 0 |
| [SI01-REQ-033](#si01-req-033) | req | 0 | 0 | 0 |
| [SI01-REQ-040](#si01-req-040) | req | 2 | 6 | 0 |
| [SI01-REQ-041](#si01-req-041) | req | 3 | 5 | 0 |
| [SI01-REQ-042](#si01-req-042) | req | 4 | 9 | 0 |
| [SI01-REQ-043](#si01-req-043) | req | 1 | 1 | 0 |
| [SI01-REQ-044](#si01-req-044) | req | 1 | 2 | 0 |
| [SI01-REQ-045](#si01-req-045) | req | 8 | 1 | 0 |
| [SI01-REQ-046](#si01-req-046) | req | 3 | 3 | 0 |
| [SI01-REQ-047](#si01-req-047) | req | 4 | 3 | 0 |
| [SI01-REQ-048](#si01-req-048) | req | 1 | 1 | 0 |
| [SI01-REQ-049](#si01-req-049) | req | 1 | 2 | 0 |
| [SI01-REQ-050](#si01-req-050) | req | 1 | 0 | 0 |
| [SI01-REQ-051](#si01-req-051) | req | 2 | 0 | 0 |
| [SI01-REQ-052](#si01-req-052) | req | 2 | 1 | 0 |
| [SI01-REQ-053](#si01-req-053) | req | 1 | 1 | 0 |
| [SI01-REQ-054](#si01-req-054) | req | 1 | 0 | 0 |
| [SI01-REQ-055](#si01-req-055) | req | 1 | 0 | 0 |
| [SI01-REQ-060](#si01-req-060) | req | 1 | 1 | 0 |
| [SI01-REQ-061](#si01-req-061) | req | 2 | 0 | 0 |
| [SI01-REQ-062](#si01-req-062) | req | 1 | 0 | 0 |
| [SI01-REQ-063](#si01-req-063) | req | 1 | 0 | 0 |
| [SI01-REQ-064](#si01-req-064) | req | 3 | 3 | 0 |
| [SI01-REQ-065](#si01-req-065) | req | 3 | 1 | 0 |
| [SI01-REQ-066](#si01-req-066) | req | 4 | 0 | 0 |
| [SI01-REQ-067](#si01-req-067) | req | 3 | 0 | 0 |
| [SI01-REQ-068](#si01-req-068) | req | 2 | 0 | 0 |
| [SI01-REQ-069](#si01-req-069) | req | 3 | 0 | 0 |
| [SI01-REQ-070](#si01-req-070) | req | 1 | 0 | 0 |
| [SI01-REQ-071](#si01-req-071) | req | 3 | 2 | 0 |
| [SI01-REQ-072](#si01-req-072) | req | 3 | 3 | 0 |
| [SI01-REQ-073](#si01-req-073) | req | 3 | 0 | 0 |
| [SI01-REQ-074](#si01-req-074) | req | 4 | 0 | 0 |
| [SI02-REQ-001](#si02-req-001) | req | 3 | 0 | 0 |
| [SI02-REQ-002](#si02-req-002) | req | 3 | 0 | 0 |
| [SI02-REQ-003](#si02-req-003) | req | 2 | 0 | 0 |
| [SI02-REQ-004](#si02-req-004) | req | 7 | 0 | 0 |
| [SI02-REQ-005](#si02-req-005) | req | 5 | 0 | 0 |
| [SI02-REQ-006](#si02-req-006) | req | 6 | 0 | 0 |
| [SI02-REQ-007](#si02-req-007) | req | 5 | 0 | 0 |
| [SI02-REQ-008](#si02-req-008) | req | 6 | 0 | 0 |
| [ScheduledTaskRunner](#scheduledtaskrunner) | arch | 0 | 1 | 1 |
| [SerialExecutor](#serialexecutor) | arch | 0 | 1 | 1 |
| [SerialScheduledExecutor](#serialscheduledexecutor) | arch | 0 | 1 | 1 |
| [SerialTaskRunner](#serialtaskrunner) | arch | 0 | 1 | 1 |
| [SharedTerminalHandler](#sharedterminalhandler) | arch | 0 | 1 | 1 |
| [SimulatedAntenna](#simulatedantenna) | arch | 0 | 1 | 1 |
| [SimulatedPowerDevice](#simulatedpowerdevice) | arch | 0 | 1 | 1 |
| [SimulationRuntime](#simulationruntime) | arch | 0 | 0 | 1 |
| [StageStartTimes](#stagestarttimes) | arch | 0 | 0 | 1 |
| [StageTiming](#stagetiming) | arch | 0 | 0 | 1 |
| [Storage](#storage) | arch | 0 | 0 | 1 |
| [SystemConductor](#systemconductor) | arch | 1 | 1 | 1 |
| [SystemStatus](#systemstatus) | arch | 0 | 1 | 1 |
| [SystemUpstreamMessagePort](#systemupstreammessageport) | arch | 0 | 1 | 1 |
| [TagProcessor](#tagprocessor) | arch | 0 | 2 | 1 |
| [TimeSource](#timesource) | arch | 0 | 1 | 1 |
| [TimingApplicationRuntime](#timingapplicationruntime) | arch | 0 | 1 | 1 |
| [TimingData](#timingdata) | arch | 0 | 2 | 1 |
| [TimingNode](#timingnode) | arch | 4 | 2 | 1 |
| [TimingNodeProxy](#timingnodeproxy) | arch | 0 | 1 | 1 |
| [TimingNodeUpstreamMessagePort](#timingnodeupstreammessageport) | arch | 0 | 1 | 1 |
| [TimingSystem](#timingsystem) | arch | 0 | 2 | 1 |
| [UC-001](#uc-001) | uc | 0 | 8 | 0 |
| [UC-002](#uc-002) | uc | 0 | 7 | 0 |
| [UC-003](#uc-003) | uc | 0 | 8 | 0 |
| [UC-004](#uc-004) | uc | 0 | 2 | 0 |
| [UC-005](#uc-005) | uc | 0 | 1 | 0 |
| [UC-006](#uc-006) | uc | 0 | 1 | 0 |
| [UC-007](#uc-007) | uc | 0 | 1 | 0 |
| [UC-009](#uc-009) | uc | 0 | 23 | 0 |
| [UC-010](#uc-010) | uc | 0 | 1 | 0 |
| [UC-011](#uc-011) | uc | 0 | 4 | 0 |
| [UC-012](#uc-012) | uc | 0 | 3 | 0 |
| [UC-013](#uc-013) | uc | 0 | 2 | 0 |
| [UC-014](#uc-014) | uc | 0 | 1 | 0 |
| [UC-015](#uc-015) | uc | 0 | 3 | 0 |
| [UC-016](#uc-016) | uc | 0 | 2 | 0 |
| [UC-017](#uc-017) | uc | 0 | 1 | 0 |
| [UC-018](#uc-018) | uc | 0 | 1 | 0 |
| [UC-019](#uc-019) | uc | 0 | 1 | 0 |
| [UC-020](#uc-020) | uc | 0 | 3 | 0 |
| [UC-021](#uc-021) | uc | 0 | 4 | 0 |
| [UC-022](#uc-022) | uc | 0 | 4 | 0 |
| [UC-023](#uc-023) | uc | 0 | 1 | 0 |
| [UC-024](#uc-024) | uc | 0 | 2 | 0 |
| [UpstreamGateway](#upstreamgateway) | arch | 0 | 1 | 1 |
| [UpstreamMessageRouter](#upstreammessagerouter) | arch | 0 | 1 | 1 |
| [UpstreamProtocol](#upstreamprotocol) | arch | 0 | 1 | 1 |
| [VC-ST1-001](#vc-st1-001) | vc | 11 | 0 | 0 |
| [VC-ST1-002](#vc-st1-002) | vc | 13 | 0 | 0 |
| [VC-ST1-003](#vc-st1-003) | vc | 6 | 0 | 0 |
| [VC-ST1-004](#vc-st1-004) | vc | 5 | 0 | 0 |
| [VC-ST1-005](#vc-st1-005) | vc | 8 | 0 | 0 |
| [VC-ST1-006](#vc-st1-006) | vc | 9 | 0 | 0 |
| [VC-ST1-007](#vc-st1-007) | vc | 12 | 0 | 0 |
| [VC-ST1-008](#vc-st1-008) | vc | 12 | 0 | 0 |
| [VendorAntenna](#vendorantenna) | arch | 0 | 0 | 1 |
| [Web](#web) | arch | 0 | 0 | 1 |

## Antenna

Type: arch (Architecture Element)  
Title: Antenna  
Source: docs/41-01-SSD-timing-application-specification-document.md:1525

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:335 (diagram=layered-architecture, node=devices-io)

## AntennaManager

Type: arch (Architecture Element)  
Title: AntennaManager  
Source: docs/41-01-SSD-timing-application-specification-document.md:1517

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:332 (diagram=layered-architecture, node=devices-io)

## Api

Type: arch (Architecture Element)  
Title: API  
Source: docs/41-01-SSD-timing-application-specification-document.md:929

### Authored outgoing

- realizes -> **IF03-REQ-001**
- realizes -> **IF03-REQ-002**
- realizes -> **IF03-REQ-004**
- realizes -> **SI01-REQ-031**

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:137 (diagram=layered-architecture, node=remote-api)

## ApplicationConductor

Type: arch (Architecture Element)  
Title: Application Conductor  
Source: docs/41-01-SSD-timing-application-specification-document.md:1017

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:159 (diagram=layered-architecture, node=application-conductor)

## ApplicationConfiguration

Type: arch (Architecture Element)  
Title: Application configuration  
Source: docs/41-01-SSD-timing-application-specification-document.md:1812

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RunningConfiguration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:493 (diagram=layered-architecture, node=application-configuration-runtime)

## Beeper

Type: arch (Architecture Element)  
Title: Beeper  
Source: docs/41-01-SSD-timing-application-specification-document.md:1604

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:359 (diagram=layered-architecture, node=devices-io)

## CanNetworkController

Type: arch (Architecture Element)  
Title: CanNetworkController  
Source: docs/41-01-SSD-timing-application-specification-document.md:1611

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-IOComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:371 (diagram=layered-architecture, node=device-network-io)

## ClockTimeSource

Type: arch (Architecture Element)  
Title: ClockTimeSource  
Source: docs/41-01-SSD-timing-application-specification-document.md:1798

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:447 (diagram=layered-architecture, node=platform-time)

## Configuration

Type: arch (Architecture Element)  
Title: Typed configuration values  
Source: docs/41-01-SSD-timing-application-specification-document.md:1821

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RunningConfiguration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:522 (diagram=layered-architecture, node=configuration-infra)

## ConfigurationControl

Type: arch (Architecture Element)  
Title: Configuration control  
Source: docs/41-01-SSD-timing-application-specification-document.md:1027

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RunningConfiguration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:184 (diagram=layered-architecture, node=configuration-control)

## Connector

Type: arch (Architecture Element)  
Title: Connector  
Source: docs/41-01-SSD-timing-application-specification-document.md:1633

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:386 (diagram=layered-architecture, node=messaging-io)

## Console

Type: arch (Architecture Element)  
Title: Console  
Source: docs/41-01-SSD-timing-application-specification-document.md:961

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:106 (diagram=layered-architecture, node=local-console)

## CooperativeTaskController

Type: arch (Architecture Element)  
Title: CooperativeTaskController  
Source: docs/41-01-SSD-timing-application-specification-document.md:1725

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-CooperativeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:410 (diagram=layered-architecture, node=platform-execution)

## DD-AntennaRuntime

Type: design (Detailed Design)  
Title: Antenna runtime and device control  
Source: docs/43-01-SDD-02-java-component-design.md:1581

### Authored outgoing

- elaborates -> **Antenna**
- elaborates -> **AntennaManager**
- elaborates -> **PowerDevice**
- elaborates -> **SimulatedAntenna**
- elaborates -> **SimulatedPowerDevice**

### Generated incoming

_None._

### Diagram references

_None._

## DD-CooperativeExecution

Type: design (Detailed Design)  
Title: Cooperative execution and TimingSystem coordination  
Source: docs/43-01-SDD-02-java-component-design.md:401

### Authored outgoing

- elaborates -> **CooperativeTaskController**
- elaborates -> **PlatformExecution**
- elaborates -> **ScheduledTaskRunner**
- elaborates -> **SerialTaskRunner**
- elaborates -> **SystemConductor**

### Generated incoming

_None._

### Diagram references

_None._

## DD-DependencyPlacement

Type: design (Detailed Design)  
Title: Contract and internal dependency placement  
Source: docs/43-01-SDD-02-java-component-design.md:942

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## DD-DomainIntegration

Type: design (Detailed Design)  
Title: Domain data, upstream and system-status composition  
Source: docs/43-01-SDD-02-java-component-design.md:897

### Authored outgoing

- elaborates -> **SystemStatus**
- elaborates -> **SystemUpstreamMessagePort**
- elaborates -> **TimingNodeUpstreamMessagePort**
- elaborates -> **TimingSystem**
- elaborates -> **UpstreamGateway**
- elaborates -> **UpstreamMessageRouter**
- elaborates -> **UpstreamProtocol**

### Generated incoming

_None._

### Diagram references

_None._

## DD-EventTagProcessing

Type: design (Detailed Design)  
Title: EventData and TagProcessor realization  
Source: docs/43-01-SDD-02-java-component-design.md:626

### Authored outgoing

- elaborates -> **EventData**
- elaborates -> **TagProcessor**

### Generated incoming

_None._

### Diagram references

_None._

## DD-ExecutableComposition

Type: design (Detailed Design)  
Title: Executable and presentation composition  
Source: docs/43-01-SDD-02-java-component-design.md:1079

### Authored outgoing

- elaborates -> **Api**
- elaborates -> **Console**
- elaborates -> **PresentationRuntime**
- elaborates -> **RemoteShell**
- elaborates -> **SharedTerminalHandler**
- elaborates -> **TimingApplicationRuntime**

### Generated incoming

_None._

### Diagram references

_None._

## DD-ExtensionAndComposition

Type: design (Detailed Design)  
Title: Extension and product composition  
Source: docs/43-01-SDD-02-java-component-design.md:3360

### Authored outgoing

- elaborates -> **EventData**
- elaborates -> **TimingData**

### Generated incoming

_None._

### Diagram references

_None._

## DD-IOComposition

Type: design (Detailed Design)  
Title: I/O composition and network-device boundary  
Source: docs/43-01-SDD-02-java-component-design.md:869

### Authored outgoing

- elaborates -> **CanNetworkController**
- elaborates -> **NetworkDeviceService**
- elaborates -> **TimingSystem**

### Generated incoming

_None._

### Diagram references

_None._

## DD-LoggingRuntime

Type: design (Detailed Design)  
Title: Runtime logging infrastructure  
Source: docs/43-01-SDD-02-java-component-design.md:1017

### Authored outgoing

- elaborates -> **Logging**
- elaborates -> **LoggingServer**

### Generated incoming

_None._

### Diagram references

_None._

## DD-PresentationAccess

Type: design (Detailed Design)  
Title: Presentation-facing application access  
Source: docs/43-01-SDD-02-java-component-design.md:742

### Authored outgoing

- elaborates -> **PresentationGateway**
- elaborates -> **TimingNodeProxy**

### Generated incoming

_None._

### Diagram references

_None._

## DD-RunningConfiguration

Type: design (Detailed Design)  
Title: Running configuration model  
Source: docs/43-01-SDD-02-java-component-design.md:1327

### Authored outgoing

- elaborates -> **ApplicationConfiguration**
- elaborates -> **Configuration**
- elaborates -> **ConfigurationControl**

### Generated incoming

_None._

### Diagram references

_None._

## DD-RuntimeExecution

Type: design (Detailed Design)  
Title: Runtime execution model  
Source: docs/43-01-SDD-02-java-component-design.md:2496

### Authored outgoing

- elaborates -> **PlatformExecution**
- elaborates -> **RuntimeExecutors**
- elaborates -> **SerialExecutor**
- elaborates -> **SerialScheduledExecutor**

### Generated incoming

_None._

### Diagram references

_None._

## DD-RuntimeWorkAndMeasurements

Type: design (Detailed Design)  
Title: Registration workload and runtime measurement  
Source: docs/43-01-SDD-02-java-component-design.md:2304

### Authored outgoing

- elaborates -> **PlatformExecution**
- elaborates -> **RuntimeExecutors**
- elaborates -> **TagProcessor**
- elaborates -> **TimingNode**

### Generated incoming

_None._

### Diagram references

_None._

## DD-TimingDataProfiles

Type: design (Detailed Design)  
Title: TimingData shared contract and profiles  
Source: docs/43-01-SDD-02-java-component-design.md:3158

### Authored outgoing

- elaborates -> **TimingData**

### Generated incoming

_None._

### Diagram references

_None._

## DD-TimingNodeExecution

Type: design (Detailed Design)  
Title: TimingNode execution, LogBook and local events  
Source: docs/43-01-SDD-02-java-component-design.md:2576

### Authored outgoing

- elaborates -> **Event**
- elaborates -> **EventSource**
- elaborates -> **LogBook**
- elaborates -> **PlatformEvents**
- elaborates -> **TimingNode**

### Generated incoming

_None._

### Diagram references

_None._

## DD-TimingTimeComposition

Type: design (Detailed Design)  
Title: Timing-time composition  
Source: docs/43-01-SDD-02-java-component-design.md:848

### Authored outgoing

- elaborates -> **ClockTimeSource**
- elaborates -> **PlatformEnvironment**
- elaborates -> **PlatformTime**
- elaborates -> **RuntimeTimeSources**
- elaborates -> **TimeSource**

### Generated incoming

_None._

### Diagram references

_None._

## DebugConnector

Type: arch (Architecture Element)  
Title: DebugConnector  
Source: docs/41-01-SSD-timing-application-specification-document.md:1648

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:391 (diagram=layered-architecture, node=messaging-io)

## DeviceNetworks

Type: arch (Architecture Element)  
Title: DeviceNetworks  
Source: docs/41-01-SSD-timing-application-specification-document.md:1482

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:366 (diagram=layered-architecture, node=device-network-io)

## Devices

Type: arch (Architecture Element)  
Title: Devices  
Source: docs/41-01-SSD-timing-application-specification-document.md:1467

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:327 (diagram=layered-architecture, node=devices-io)

## Display

Type: arch (Architecture Element)  
Title: Display  
Source: docs/41-01-SSD-timing-application-specification-document.md:1568

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:347 (diagram=layered-architecture, node=devices-io)

## Event

Type: arch (Architecture Element)  
Title: Event  
Source: docs/41-01-SSD-timing-application-specification-document.md:1741

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:420 (diagram=layered-architecture, node=platform-events)

## EventData

Type: arch (Architecture Element)  
Title: EventData  
Source: docs/41-01-SSD-timing-application-specification-document.md:1222

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-EventTagProcessing**
- elaborates <- **DD-ExtensionAndComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:287 (diagram=layered-architecture, node=event-data-domain)

## EventSource

Type: arch (Architecture Element)  
Title: EventSource  
Source: docs/41-01-SSD-timing-application-specification-document.md:1748

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:422 (diagram=layered-architecture, node=platform-events)

## IF03-REQ-001

Type: ifreq (Interface Requirement)  
Title: Shared application semantics  
Source: docs/32-03-ISD-application-control-status.md:421

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI02-REQ-001**
- realizes <- **Api**
- realizes <- **PresentationGateway**

### Diagram references

_None._

## IF03-REQ-002

Type: ifreq (Interface Requirement)  
Title: Remote-host operation  
Source: docs/32-03-ISD-application-control-status.md:430

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI02-REQ-002**
- realizes <- **Api**

### Diagram references

_None._

## IF03-REQ-003

Type: ifreq (Interface Requirement)  
Title: Version query  
Source: docs/32-03-ISD-application-control-status.md:439

### Authored outgoing

- specifies -> **UC-009**

### Generated incoming

- depends_on <- **SI02-REQ-003**
- verifies <- **VC-ST1-001**

### Diagram references

_None._

## IF03-REQ-004

Type: ifreq (Interface Requirement)  
Title: Status query  
Source: docs/32-03-ISD-application-control-status.md:447

### Authored outgoing

- refines -> **SI01-REQ-024**

### Generated incoming

- depends_on <- **SI02-REQ-004**
- realizes <- **Api**
- realizes <- **PresentationGateway**
- verifies <- **VC-ST1-001**
- verifies <- **VC-ST1-004**

### Diagram references

_None._

## IF03-REQ-005

Type: ifreq (Interface Requirement)  
Title: Live status and committed-data delivery  
Source: docs/32-03-ISD-application-control-status.md:455

### Authored outgoing

- refines -> **SI01-REQ-023**

### Generated incoming

- depends_on <- **SI02-REQ-004**
- verifies <- **VC-ST1-001**

### Diagram references

_None._

## IF03-REQ-006

Type: ifreq (Interface Requirement)  
Title: Reconnect to current state  
Source: docs/32-03-ISD-application-control-status.md:463

### Authored outgoing

- refines -> **SI01-REQ-025**

### Generated incoming

- depends_on <- **SI02-REQ-005**
- depends_on <- **SI02-REQ-006**
- verifies <- **VC-ST1-001**
- verifies <- **VC-ST1-004**

### Diagram references

_None._

## IF03-REQ-007

Type: ifreq (Interface Requirement)  
Title: Machine-readable API realization  
Source: docs/32-03-ISD-application-control-status.md:472

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI02-REQ-001**

### Diagram references

_None._

## IF03-REQ-008

Type: ifreq (Interface Requirement)  
Title: Explicit failure outcome  
Source: docs/32-03-ISD-application-control-status.md:481

### Authored outgoing

- refines -> **SI01-REQ-026**

### Generated incoming

- depends_on <- **SI02-REQ-008**
- verifies <- **VC-ST1-004**
- verifies <- **VC-ST1-006**

### Diagram references

_None._

## IF03-REQ-009

Type: ifreq (Interface Requirement)  
Title: Safe default listen scope  
Source: docs/32-03-ISD-application-control-status.md:490

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI02-REQ-002**

### Diagram references

_None._

## IF03-REQ-010

Type: ifreq (Interface Requirement)  
Title: Compatible extension  
Source: docs/32-03-ISD-application-control-status.md:499

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-011

Type: ifreq (Interface Requirement)  
Title: TimingNode location and lifecycle control  
Source: docs/32-03-ISD-application-control-status.md:508

### Authored outgoing

- refines -> **SI01-REQ-040**
- refines -> **SI01-REQ-072**

### Generated incoming

- depends_on <- **SI02-REQ-004**
- depends_on <- **SI02-REQ-008**
- verifies <- **VC-ST1-002**
- verifies <- **VC-ST1-005**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## IF03-REQ-012

Type: ifreq (Interface Requirement)  
Title: Engineering capability discovery  
Source: docs/32-03-ISD-application-control-status.md:519

### Authored outgoing

- specifies -> **UC-009**

### Generated incoming

- verifies <- **VC-ST1-002**

### Diagram references

_None._

## IF03-REQ-013

Type: ifreq (Interface Requirement)  
Title: Direct accepted-registration simulation  
Source: docs/32-03-ISD-application-control-status.md:528

### Authored outgoing

- refines -> **SI01-REQ-041**
- specifies -> **UC-009**

### Generated incoming

- verifies <- **VC-ST1-002**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## IF03-REQ-014

Type: ifreq (Interface Requirement)  
Title: Committed LogBook query  
Source: docs/32-03-ISD-application-control-status.md:542

### Authored outgoing

- refines -> **SI01-REQ-042**

### Generated incoming

- depends_on <- **SI02-REQ-006**
- depends_on <- **SI02-REQ-007**
- verifies <- **VC-ST1-002**
- verifies <- **VC-ST1-005**
- verifies <- **VC-ST1-006**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## IF03-REQ-015

Type: ifreq (Interface Requirement)  
Title: Live committed TimingData delivery  
Source: docs/32-03-ISD-application-control-status.md:551

### Authored outgoing

- refines -> **SI01-REQ-042**

### Generated incoming

- depends_on <- **SI02-REQ-007**
- verifies <- **VC-ST1-002**
- verifies <- **VC-ST1-005**
- verifies <- **VC-ST1-006**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## IF03-REQ-016

Type: ifreq (Interface Requirement)  
Title: Rebuild committed history before live presentation  
Source: docs/32-03-ISD-application-control-status.md:560

### Authored outgoing

- refines -> **SI01-REQ-044**

### Generated incoming

- depends_on <- **SI02-REQ-006**
- verifies <- **VC-ST1-003**

### Diagram references

_None._

## IF03-REQ-017

Type: ifreq (Interface Requirement)  
Title: Degraded TimingNode status  
Source: docs/32-03-ISD-application-control-status.md:653

### Authored outgoing

- refines -> **SI01-REQ-024**
- refines -> **SI01-REQ-049**

### Generated incoming

- depends_on <- **SI02-REQ-004**
- verifies <- **VC-ST1-004**

### Diagram references

_None._

## IF03-REQ-018

Type: ifreq (Interface Requirement)  
Title: Runtime configuration query  
Source: docs/32-03-ISD-application-control-status.md:584

### Authored outgoing

- depends_on -> **SI01-REQ-001**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-019

Type: ifreq (Interface Requirement)  
Title: Runtime configuration override  
Source: docs/32-03-ISD-application-control-status.md:594

### Authored outgoing

- depends_on -> **SI01-REQ-001**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-020

Type: ifreq (Interface Requirement)  
Title: Runtime configuration change notification  
Source: docs/32-03-ISD-application-control-status.md:605

### Authored outgoing

- depends_on -> **SI01-REQ-001**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-021

Type: ifreq (Interface Requirement)  
Title: Bounded live-event delivery  
Source: docs/32-03-ISD-application-control-status.md:571

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI02-REQ-005**

### Diagram references

_None._

## IF03-REQ-022

Type: ifreq (Interface Requirement)  
Title: Registration revoke  
Source: docs/32-03-ISD-application-control-status.md:616

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-003**
- verifies <- **VC-ST1-006**

### Diagram references

_None._

## IF03-REQ-023

Type: ifreq (Interface Requirement)  
Title: Manual registration add  
Source: docs/32-03-ISD-application-control-status.md:628

### Authored outgoing

- refines -> **SI01-REQ-071**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-024

Type: ifreq (Interface Requirement)  
Title: Simulated tag passage control  
Source: docs/32-03-ISD-application-control-status.md:640

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-001

Type: ifreq (Interface Requirement)  
Title: Per-TimingNode Web binding  
Source: docs/32-04-ISD-web-interface.md:230

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-002

Type: ifreq (Interface Requirement)  
Title: Current TimingNode state  
Source: docs/32-04-ISD-web-interface.md:240

### Authored outgoing

- refines -> **SI01-REQ-024**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-003

Type: ifreq (Interface Requirement)  
Title: Open with LocationId  
Source: docs/32-04-ISD-web-interface.md:249

### Authored outgoing

- refines -> **SI01-REQ-040**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-004

Type: ifreq (Interface Requirement)  
Title: Close operation  
Source: docs/32-04-ISD-web-interface.md:258

### Authored outgoing

- refines -> **SI01-REQ-072**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-005

Type: ifreq (Interface Requirement)  
Title: Shared TimingNode semantics  
Source: docs/32-04-ISD-web-interface.md:266

### Authored outgoing

- refines -> **SI01-REQ-040**
- refines -> **SI01-REQ-072**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-006

Type: ifreq (Interface Requirement)  
Title: Explicit failure outcome  
Source: docs/32-04-ISD-web-interface.md:275

### Authored outgoing

- refines -> **SI01-REQ-026**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-007

Type: ifreq (Interface Requirement)  
Title: Compatible Web realizations  
Source: docs/32-04-ISD-web-interface.md:285

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-008

Type: ifreq (Interface Requirement)  
Title: Current-state baseline after connect or reconnect  
Source: docs/32-04-ISD-web-interface.md:295

### Authored outgoing

- refines -> **SI01-REQ-025**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-009

Type: ifreq (Interface Requirement)  
Title: Live-state delivery and loss handling  
Source: docs/32-04-ISD-web-interface.md:305

### Authored outgoing

- refines -> **SI01-REQ-023**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-010

Type: ifreq (Interface Requirement)  
Title: Manual registration through Web interface  
Source: docs/32-04-ISD-web-interface.md:316

### Authored outgoing

- refines -> **SI01-REQ-071**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-011

Type: ifreq (Interface Requirement)  
Title: Local-network browser access  
Source: docs/32-04-ISD-web-interface.md:326

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-012

Type: ifreq (Interface Requirement)  
Title: Query committed registration history  
Source: docs/32-04-ISD-web-interface.md:336

### Authored outgoing

- refines -> **SI01-REQ-042**

### Generated incoming

_None._

### Diagram references

_None._

## IF05-REQ-001

Type: ifreq (Interface Requirement)  
Title: Common TimingData envelope  
Source: docs/32-05-ISD-timingdata-interchange.md:301

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-045**

### Diagram references

_None._

## IF05-REQ-002

Type: ifreq (Interface Requirement)  
Title: Record identity within a TimingSystem  
Source: docs/32-05-ISD-timingdata-interchange.md:310

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-045**
- depends_on <- **SI01-REQ-047**
- verifies <- **VC-ST1-005**
- verifies <- **VC-ST1-006**

### Diagram references

_None._

## IF05-REQ-003

Type: ifreq (Interface Requirement)  
Title: Sequence progression  
Source: docs/32-05-ISD-timingdata-interchange.md:319

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-045**
- depends_on <- **SI01-REQ-047**
- verifies <- **VC-ST1-002**
- verifies <- **VC-ST1-005**
- verifies <- **VC-ST1-006**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## IF05-REQ-004

Type: ifreq (Interface Requirement)  
Title: Automatic and manual registration  
Source: docs/32-05-ISD-timingdata-interchange.md:328

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-045**

### Diagram references

_None._

## IF05-REQ-005

Type: ifreq (Interface Requirement)  
Title: Registration record values  
Source: docs/32-05-ISD-timingdata-interchange.md:336

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-045**
- verifies <- **VC-ST1-006**

### Diagram references

_None._

## IF05-REQ-006

Type: ifreq (Interface Requirement)  
Title: Registration add and revoke  
Source: docs/32-05-ISD-timingdata-interchange.md:344

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-045**
- verifies <- **VC-ST1-003**
- verifies <- **VC-ST1-006**

### Diagram references

_None._

## IF05-REQ-007

Type: ifreq (Interface Requirement)  
Title: Committed record immutability  
Source: docs/32-05-ISD-timingdata-interchange.md:355

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-045**
- depends_on <- **SI01-REQ-047**
- verifies <- **VC-ST1-003**
- verifies <- **VC-ST1-006**

### Diagram references

_None._

## IF05-REQ-008

Type: ifreq (Interface Requirement)  
Title: TimingNode lifecycle records  
Source: docs/32-05-ISD-timingdata-interchange.md:365

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-002**
- verifies <- **VC-ST1-003**
- verifies <- **VC-ST1-005**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## IF05-REQ-009

Type: ifreq (Interface Requirement)  
Title: Lifecycle transition values  
Source: docs/32-05-ISD-timingdata-interchange.md:375

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-002**
- verifies <- **VC-ST1-005**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## IF05-REQ-010

Type: ifreq (Interface Requirement)  
Title: No lifecycle record without transition  
Source: docs/32-05-ISD-timingdata-interchange.md:385

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-005**

### Diagram references

_None._

## Keypad

Type: arch (Architecture Element)  
Title: Keypad  
Source: docs/41-01-SSD-timing-application-specification-document.md:1590

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:354 (diagram=layered-architecture, node=devices-io)

## LogBook

Type: arch (Architecture Element)  
Title: LogBook  
Source: docs/41-01-SSD-timing-application-specification-document.md:1895

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:278 (diagram=layered-architecture, node=logbook-domain)

## Logging

Type: arch (Architecture Element)  
Title: Logging  
Source: docs/41-01-SSD-timing-application-specification-document.md:1836

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-LoggingRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:509 (diagram=layered-architecture, node=logging-infra)

## LoggingServer

Type: arch (Architecture Element)  
Title: LoggingServer  
Source: docs/41-01-SSD-timing-application-specification-document.md:1846

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-LoggingRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:501 (diagram=layered-architecture, node=logging-server)

## Messaging

Type: arch (Architecture Element)  
Title: Messaging  
Source: docs/41-01-SSD-timing-application-specification-document.md:1496

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:378 (diagram=layered-architecture, node=messaging-io)

## MonotonicClock

Type: arch (Architecture Element)  
Title: MonotonicClock  
Source: docs/41-01-SSD-timing-application-specification-document.md:1766

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:433 (diagram=layered-architecture, node=platform-environment)

## NetworkDeviceService

Type: arch (Architecture Element)  
Title: NetworkDeviceService  
Source: docs/41-01-SSD-timing-application-specification-document.md:1618

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-IOComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:373 (diagram=layered-architecture, node=device-network-io)

## NextUpTeams

Type: arch (Architecture Element)  
Title: NextUpTeams  
Source: docs/41-01-SSD-timing-application-specification-document.md:1207

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:253 (diagram=layered-architecture, node=next-up-teams)

## OperatingSystem

Type: arch (Architecture Element)  
Title: OperatingSystem  
Source: docs/41-01-SSD-timing-application-specification-document.md:1773

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:435 (diagram=layered-architecture, node=platform-environment)

## PlatformEnvironment

Type: arch (Architecture Element)  
Title: PlatformEnvironment  
Source: docs/41-01-SSD-timing-application-specification-document.md:1755

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:427 (diagram=layered-architecture, node=platform-environment)

## PlatformEvents

Type: arch (Architecture Element)  
Title: PlatformEvents  
Source: docs/41-01-SSD-timing-application-specification-document.md:1733

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:415 (diagram=layered-architecture, node=platform-events)

## PlatformExecution

Type: arch (Architecture Element)  
Title: PlatformExecution  
Source: docs/41-01-SSD-timing-application-specification-document.md:1683

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-CooperativeExecution**
- elaborates <- **DD-RuntimeExecution**
- elaborates <- **DD-RuntimeWorkAndMeasurements**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:397 (diagram=layered-architecture, node=platform-execution)

## PlatformTime

Type: arch (Architecture Element)  
Title: PlatformTime  
Source: docs/41-01-SSD-timing-application-specification-document.md:1780

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:440 (diagram=layered-architecture, node=platform-time)

## PowerDevice

Type: arch (Architecture Element)  
Title: PowerDevice  
Source: docs/41-01-SSD-timing-application-specification-document.md:1533

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:342 (diagram=layered-architecture, node=devices-io)

## PresentationGateway

Type: arch (Architecture Element)  
Title: PresentationGateway  
Source: docs/41-01-SSD-timing-application-specification-document.md:1036

### Authored outgoing

- realizes -> **IF03-REQ-001**
- realizes -> **IF03-REQ-004**
- realizes -> **SI01-REQ-022**
- realizes -> **SI01-REQ-030**
- realizes -> **SI01-REQ-031**

### Generated incoming

- elaborates <- **DD-PresentationAccess**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:168 (diagram=layered-architecture, node=presentation-gateway)

## PresentationRuntime

Type: arch (Architecture Element)  
Title: PresentationRuntime  
Source: docs/41-01-SSD-timing-application-specification-document.md:805

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:469 (diagram=layered-architecture, node=presentation-runtime)

## RabbitMqConnector

Type: arch (Architecture Element)  
Title: RabbitMqConnector  
Source: docs/41-01-SSD-timing-application-specification-document.md:1641

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:389 (diagram=layered-architecture, node=messaging-io)

## RaceData

Type: arch (Architecture Element)  
Title: RaceData  
Source: docs/41-01-SSD-timing-application-specification-document.md:1213

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:261 (diagram=layered-architecture, node=race-data)

## RemoteShell

Type: arch (Architecture Element)  
Title: RemoteShell  
Source: docs/41-01-SSD-timing-application-specification-document.md:970

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:116 (diagram=layered-architecture, node=remote-shell)

## Rev1CanDisplay

Type: arch (Architecture Element)  
Title: Rev1CanDisplay  
Source: docs/41-01-SSD-timing-application-specification-document.md:1576

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:350 (diagram=layered-architecture, node=devices-io)

## Rev1CanKeypad

Type: arch (Architecture Element)  
Title: Rev1CanKeypad  
Source: docs/41-01-SSD-timing-application-specification-document.md:1597

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:357 (diagram=layered-architecture, node=devices-io)

## Rev2WifiDisplay

Type: arch (Architecture Element)  
Title: Rev2WifiDisplay  
Source: docs/41-01-SSD-timing-application-specification-document.md:1583

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:352 (diagram=layered-architecture, node=devices-io)

## RuntimeExecutors

Type: arch (Architecture Element)  
Title: RuntimeExecutors  
Source: docs/41-01-SSD-timing-application-specification-document.md:814

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RuntimeExecution**
- elaborates <- **DD-RuntimeWorkAndMeasurements**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:477 (diagram=layered-architecture, node=runtime-executors)

## RuntimeTimeSources

Type: arch (Architecture Element)  
Title: RuntimeTimeSources  
Source: docs/41-01-SSD-timing-application-specification-document.md:820

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:485 (diagram=layered-architecture, node=runtime-time-sources)

## SI01-REQ-001

Type: req (Requirement)  
Title: Start from external configuration  
Source: docs/41-01-SSD-timing-application-specification-document.md:572

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **IF03-REQ-018**
- depends_on <- **IF03-REQ-019**
- depends_on <- **IF03-REQ-020**
- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-002

Type: req (Requirement)  
Title: Clean process shutdown  
Source: docs/41-01-SSD-timing-application-specification-document.md:579

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-003

Type: req (Requirement)  
Title: Configured TimingNode availability  
Source: docs/41-01-SSD-timing-application-specification-document.md:587

### Authored outgoing

- specifies -> **UC-014**
- specifies -> **UC-015**

### Generated incoming

- depends_on <- **SI01-REQ-066**
- realizes <- **TimingNode**
- verifies <- **VC-ST1-001**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## SI01-REQ-010

Type: req (Requirement)  
Title: Single application build identity  
Source: docs/41-01-SSD-timing-application-specification-document.md:600

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-011

Type: req (Requirement)  
Title: Consistent identity across interfaces  
Source: docs/41-01-SSD-timing-application-specification-document.md:608

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-020

Type: req (Requirement)  
Title: Current application status snapshot  
Source: docs/41-01-SSD-timing-application-specification-document.md:272

### Authored outgoing

- specifies -> **UC-009**

### Generated incoming

- realizes <- **TimingNode**
- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-021

Type: req (Requirement)  
Title: Application status content  
Source: docs/41-01-SSD-timing-application-specification-document.md:281

### Authored outgoing

- depends_on -> **SI01-REQ-024**
- specifies -> **UC-009**
- specifies -> **UC-020**

### Generated incoming

- realizes <- **TimingNode**
- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-022

Type: req (Requirement)  
Title: Equivalent status semantics across interfaces  
Source: docs/41-01-SSD-timing-application-specification-document.md:648

### Authored outgoing

- specifies -> **UC-001**
- specifies -> **UC-002**
- specifies -> **UC-009**

### Generated incoming

- realizes <- **PresentationGateway**

### Diagram references

_None._

## SI01-REQ-023

Type: req (Requirement)  
Title: TimingNode operational state-change publication  
Source: docs/41-01-SSD-timing-application-specification-document.md:299

### Authored outgoing

- depends_on -> **SI01-REQ-024**
- specifies -> **UC-001**
- specifies -> **UC-002**
- specifies -> **UC-009**

### Generated incoming

- depends_on <- **SI01-REQ-025**
- refines <- **IF03-REQ-005**
- refines <- **IF04-REQ-009**

### Diagram references

_None._

## SI01-REQ-024

Type: req (Requirement)  
Title: Current TimingNode operational state  
Source: docs/41-01-SSD-timing-application-specification-document.md:257

### Authored outgoing

- specifies -> **UC-001**
- specifies -> **UC-002**
- specifies -> **UC-009**
- specifies -> **UC-020**

### Generated incoming

- depends_on <- **SI01-REQ-021**
- depends_on <- **SI01-REQ-023**
- depends_on <- **SI01-REQ-025**
- depends_on <- **SI01-REQ-026**
- depends_on <- **SI01-REQ-072**
- depends_on <- **SI01-REQ-073**
- depends_on <- **SI01-REQ-074**
- realizes <- **TimingNode**
- refines <- **IF03-REQ-004**
- refines <- **IF03-REQ-017**
- refines <- **IF04-REQ-002**
- refines <- **SI02-REQ-004**

### Diagram references

_None._

## SI01-REQ-025

Type: req (Requirement)  
Title: Presentation current-state recovery  
Source: docs/41-01-SSD-timing-application-specification-document.md:312

### Authored outgoing

- depends_on -> **SI01-REQ-023**
- depends_on -> **SI01-REQ-024**
- specifies -> **UC-001**
- specifies -> **UC-002**
- specifies -> **UC-009**

### Generated incoming

- refines <- **IF03-REQ-006**
- refines <- **IF04-REQ-008**
- refines <- **SI02-REQ-005**
- refines <- **SI02-REQ-006**

### Diagram references

_None._

## SI01-REQ-026

Type: req (Requirement)  
Title: Lifecycle command outcome  
Source: docs/41-01-SSD-timing-application-specification-document.md:135

### Authored outgoing

- depends_on -> **SI01-REQ-024**
- depends_on -> **SI01-REQ-040**
- specifies -> **UC-001**
- specifies -> **UC-002**
- specifies -> **UC-009**

### Generated incoming

- refines <- **IF03-REQ-008**
- refines <- **IF04-REQ-006**
- refines <- **SI02-REQ-008**

### Diagram references

_None._

## SI01-REQ-030

Type: req (Requirement)  
Title: Equivalent command/query semantics across transports  
Source: docs/41-01-SSD-timing-application-specification-document.md:658

### Authored outgoing

_None._

### Generated incoming

- realizes <- **PresentationGateway**

### Diagram references

_None._

## SI01-REQ-031

Type: req (Requirement)  
Title: Externally testable executable  
Source: docs/41-01-SSD-timing-application-specification-document.md:509

### Authored outgoing

- specifies -> **UC-015**
- specifies -> **UC-016**

### Generated incoming

- depends_on <- **SI01-REQ-066**
- depends_on <- **SI01-REQ-067**
- realizes <- **Api**
- realizes <- **PresentationGateway**
- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-032

Type: req (Requirement)  
Title: Safe default network exposure  
Source: docs/41-01-SSD-timing-application-specification-document.md:667

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-033

Type: req (Requirement)  
Title: Compatible IF-03 evolution  
Source: docs/41-01-SSD-timing-application-specification-document.md:676

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-040

Type: req (Requirement)  
Title: Open registration point at a location  
Source: docs/41-01-SSD-timing-application-specification-document.md:82

### Authored outgoing

- specifies -> **UC-001**
- specifies -> **UC-009**

### Generated incoming

- depends_on <- **SI01-REQ-026**
- refines <- **IF03-REQ-011**
- refines <- **IF04-REQ-003**
- refines <- **IF04-REQ-005**
- refines <- **SI02-REQ-008**
- verifies <- **VC-ST1-002**

### Diagram references

_None._

## SI01-REQ-041

Type: req (Requirement)  
Title: Accepted registration commit semantics  
Source: docs/41-01-SSD-timing-application-specification-document.md:150

### Authored outgoing

- specifies -> **UC-003**
- specifies -> **UC-009**
- specifies -> **UC-021**

### Generated incoming

- depends_on <- **SI01-REQ-071**
- refines <- **IF03-REQ-013**
- verifies <- **VC-ST1-002**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## SI01-REQ-042

Type: req (Requirement)  
Title: Committed registration observability  
Source: docs/41-01-SSD-timing-application-specification-document.md:176

### Authored outgoing

- specifies -> **UC-003**
- specifies -> **UC-009**
- specifies -> **UC-011**
- specifies -> **UC-021**

### Generated incoming

- depends_on <- **SI01-REQ-064**
- depends_on <- **SI01-REQ-071**
- refines <- **IF03-REQ-014**
- refines <- **IF03-REQ-015**
- refines <- **IF04-REQ-012**
- refines <- **SI02-REQ-007**
- verifies <- **VC-ST1-002**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## SI01-REQ-043

Type: req (Requirement)  
Title: Gate development auto-registration by capability  
Source: docs/41-01-SSD-timing-application-specification-document.md:496

### Authored outgoing

- specifies -> **UC-009**

### Generated incoming

- verifies <- **VC-ST1-002**

### Diagram references

_None._

## SI01-REQ-044

Type: req (Requirement)  
Title: Reconnect rebuild before live presentation  
Source: docs/41-01-SSD-timing-application-specification-document.md:325

### Authored outgoing

- specifies -> **UC-009**

### Generated incoming

- refines <- **IF03-REQ-016**
- verifies <- **VC-ST1-003**

### Diagram references

_None._

## SI01-REQ-045

Type: req (Requirement)  
Title: Reference TimingData representation support  
Source: docs/41-01-SSD-timing-application-specification-document.md:620

### Authored outgoing

- depends_on -> **IF05-REQ-001**
- depends_on -> **IF05-REQ-002**
- depends_on -> **IF05-REQ-003**
- depends_on -> **IF05-REQ-004**
- depends_on -> **IF05-REQ-005**
- depends_on -> **IF05-REQ-006**
- depends_on -> **IF05-REQ-007**
- specifies -> **UC-011**

### Generated incoming

- depends_on <- **SI01-REQ-064**

### Diagram references

_None._

## SI01-REQ-046

Type: req (Requirement)  
Title: Write TimingData before commit completion  
Source: docs/41-01-SSD-timing-application-specification-document.md:632

### Authored outgoing

- specifies -> **UC-003**
- specifies -> **UC-012**
- specifies -> **UC-021**

### Generated incoming

- depends_on <- **SI01-REQ-072**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## SI01-REQ-047

Type: req (Requirement)  
Title: Restore committed TimingData after restart  
Source: docs/41-01-SSD-timing-application-specification-document.md:446

### Authored outgoing

- depends_on -> **IF05-REQ-002**
- depends_on -> **IF05-REQ-003**
- depends_on -> **IF05-REQ-007**
- specifies -> **UC-013**

### Generated incoming

- verifies <- **VC-ST1-002**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## SI01-REQ-048

Type: req (Requirement)  
Title: Reject invalid TimingData recovery input  
Source: docs/41-01-SSD-timing-application-specification-document.md:462

### Authored outgoing

- specifies -> **UC-013**

### Generated incoming

- verifies <- **VC-ST1-004**

### Diagram references

_None._

## SI01-REQ-049

Type: req (Requirement)  
Title: Contain TimingNode recovery failure  
Source: docs/41-01-SSD-timing-application-specification-document.md:474

### Authored outgoing

- specifies -> **UC-020**

### Generated incoming

- depends_on <- **SI01-REQ-074**
- refines <- **IF03-REQ-017**

### Diagram references

_None._

## SI01-REQ-050

Type: req (Requirement)  
Title: Use maximum-RSSI tag observation for registration  
Source: docs/41-01-SSD-timing-application-specification-document.md:186

### Authored outgoing

- specifies -> **UC-003**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-051

Type: req (Requirement)  
Title: Keep local registration independent from presentation, logging and backoffice delivery  
Source: docs/41-01-SSD-timing-application-specification-document.md:202

### Authored outgoing

- specifies -> **UC-003**
- specifies -> **UC-012**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-052

Type: req (Requirement)  
Title: Contain and expose antenna startup and runtime failure  
Source: docs/41-01-SSD-timing-application-specification-document.md:414

### Authored outgoing

- specifies -> **UC-003**
- specifies -> **UC-004**

### Generated incoming

- depends_on <- **SI01-REQ-074**

### Diagram references

_None._

## SI01-REQ-053

Type: req (Requirement)  
Title: Couple antenna operation to assigned TimingNode lifecycle  
Source: docs/41-01-SSD-timing-application-specification-document.md:213

### Authored outgoing

- specifies -> **UC-003**

### Generated incoming

- realizes <- **SystemConductor**

### Diagram references

_None._

## SI01-REQ-054

Type: req (Requirement)  
Title: Multiplex mutually exclusive antenna inventory  
Source: docs/41-01-SSD-timing-application-specification-document.md:230

### Authored outgoing

- specifies -> **UC-003**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-055

Type: req (Requirement)  
Title: Allow antenna recovery without process restart  
Source: docs/41-01-SSD-timing-application-specification-document.md:428

### Authored outgoing

- specifies -> **UC-004**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-060

Type: req (Requirement)  
Title: Traceable ready-team registry  
Source: docs/41-01-SSD-timing-application-specification-document.md:338

### Authored outgoing

- specifies -> **UC-005**

### Generated incoming

- depends_on <- **SI01-REQ-061**

### Diagram references

_None._

## SI01-REQ-061

Type: req (Requirement)  
Title: Drive passive CAN display from current application state  
Source: docs/41-01-SSD-timing-application-specification-document.md:351

### Authored outgoing

- depends_on -> **SI01-REQ-060**
- specifies -> **UC-006**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-062

Type: req (Requirement)  
Title: Provide synchronisable data to smart displays  
Source: docs/41-01-SSD-timing-application-specification-document.md:363

### Authored outgoing

- specifies -> **UC-007**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-063

Type: req (Requirement)  
Title: Apply TimingNode-scoped reference data from backoffice  
Source: docs/41-01-SSD-timing-application-specification-document.md:377

### Authored outgoing

- specifies -> **UC-010**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-064

Type: req (Requirement)  
Title: Transport-independent outbound backoffice synchronisation  
Source: docs/41-01-SSD-timing-application-specification-document.md:389

### Authored outgoing

- depends_on -> **SI01-REQ-042**
- depends_on -> **SI01-REQ-045**
- specifies -> **UC-011**

### Generated incoming

- depends_on <- **SI01-REQ-065**
- depends_on <- **SI01-REQ-068**
- depends_on <- **SI01-REQ-069**

### Diagram references

_None._

## SI01-REQ-065

Type: req (Requirement)  
Title: Preserve pending outbound work across backoffice outage  
Source: docs/41-01-SSD-timing-application-specification-document.md:401

### Authored outgoing

- depends_on -> **SI01-REQ-064**
- specifies -> **UC-011**
- specifies -> **UC-012**

### Generated incoming

- depends_on <- **SI01-REQ-069**

### Diagram references

_None._

## SI01-REQ-066

Type: req (Requirement)  
Title: Simulate complete multi-node behaviour through normal application paths  
Source: docs/41-01-SSD-timing-application-specification-document.md:519

### Authored outgoing

- depends_on -> **SI01-REQ-003**
- depends_on -> **SI01-REQ-031**
- specifies -> **UC-015**
- specifies -> **UC-024**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-067

Type: req (Requirement)  
Title: Substitute controllable stubs through public contracts  
Source: docs/41-01-SSD-timing-application-specification-document.md:531

### Authored outgoing

- depends_on -> **SI01-REQ-031**
- specifies -> **UC-016**
- specifies -> **UC-024**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-068

Type: req (Requirement)  
Title: Select alternative backoffice transport for loop testing  
Source: docs/41-01-SSD-timing-application-specification-document.md:543

### Authored outgoing

- depends_on -> **SI01-REQ-064**
- specifies -> **UC-017**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-069

Type: req (Requirement)  
Title: Verify production-shaped RabbitMQ connector behaviour  
Source: docs/41-01-SSD-timing-application-specification-document.md:555

### Authored outgoing

- depends_on -> **SI01-REQ-064**
- depends_on -> **SI01-REQ-065**
- specifies -> **UC-018**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-070

Type: req (Requirement)  
Title: Preserve public provider semantic classification  
Source: docs/41-01-SSD-timing-application-specification-document.md:244

### Authored outgoing

- specifies -> **UC-019**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-071

Type: req (Requirement)  
Title: Operator manual registration  
Source: docs/41-01-SSD-timing-application-specification-document.md:162

### Authored outgoing

- depends_on -> **SI01-REQ-041**
- depends_on -> **SI01-REQ-042**
- specifies -> **UC-021**

### Generated incoming

- refines <- **IF03-REQ-023**
- refines <- **IF04-REQ-010**

### Diagram references

_None._

## SI01-REQ-072

Type: req (Requirement)  
Title: Close registration point  
Source: docs/41-01-SSD-timing-application-specification-document.md:93

### Authored outgoing

- depends_on -> **SI01-REQ-024**
- depends_on -> **SI01-REQ-046**
- specifies -> **UC-002**

### Generated incoming

- refines <- **IF03-REQ-011**
- refines <- **IF04-REQ-004**
- refines <- **IF04-REQ-005**

### Diagram references

_None._

## SI01-REQ-073

Type: req (Requirement)  
Title: Registration lifecycle independent of operator sessions  
Source: docs/41-01-SSD-timing-application-specification-document.md:123

### Authored outgoing

- depends_on -> **SI01-REQ-024**
- specifies -> **UC-001**
- specifies -> **UC-002**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-074

Type: req (Requirement)  
Title: Reject opening when operational errors are blocking  
Source: docs/41-01-SSD-timing-application-specification-document.md:109

### Authored outgoing

- depends_on -> **SI01-REQ-024**
- depends_on -> **SI01-REQ-049**
- depends_on -> **SI01-REQ-052**
- specifies -> **UC-001**

### Generated incoming

_None._

### Diagram references

_None._

## SI02-REQ-001

Type: req (Requirement)  
Title: Use only supported public SI-01 boundaries  
Source: docs/41-02-SSD-gui-application-specification-document.md:52

### Authored outgoing

- depends_on -> **IF03-REQ-001**
- depends_on -> **IF03-REQ-007**
- specifies -> **UC-009**

### Generated incoming

_None._

### Diagram references

_None._

## SI02-REQ-002

Type: req (Requirement)  
Title: Select target and expose connection state  
Source: docs/41-02-SSD-gui-application-specification-document.md:64

### Authored outgoing

- depends_on -> **IF03-REQ-002**
- depends_on -> **IF03-REQ-009**
- specifies -> **UC-009**

### Generated incoming

_None._

### Diagram references

_None._

## SI02-REQ-003

Type: req (Requirement)  
Title: Show connected application identity  
Source: docs/41-02-SSD-gui-application-specification-document.md:76

### Authored outgoing

- depends_on -> **IF03-REQ-003**
- specifies -> **UC-009**

### Generated incoming

_None._

### Diagram references

_None._

## SI02-REQ-004

Type: req (Requirement)  
Title: Present current TimingNode operational status  
Source: docs/41-02-SSD-gui-application-specification-document.md:86

### Authored outgoing

- depends_on -> **IF03-REQ-004**
- depends_on -> **IF03-REQ-005**
- depends_on -> **IF03-REQ-011**
- depends_on -> **IF03-REQ-017**
- refines -> **SI01-REQ-024**
- specifies -> **UC-009**
- specifies -> **UC-022**

### Generated incoming

_None._

### Diagram references

_None._

## SI02-REQ-005

Type: req (Requirement)  
Title: Mark disconnected cached state as stale  
Source: docs/41-02-SSD-gui-application-specification-document.md:99

### Authored outgoing

- depends_on -> **IF03-REQ-006**
- depends_on -> **IF03-REQ-021**
- refines -> **SI01-REQ-025**
- specifies -> **UC-009**
- specifies -> **UC-022**

### Generated incoming

_None._

### Diagram references

_None._

## SI02-REQ-006

Type: req (Requirement)  
Title: Rebuild baseline before declaring the view live  
Source: docs/41-02-SSD-gui-application-specification-document.md:111

### Authored outgoing

- depends_on -> **IF03-REQ-006**
- depends_on -> **IF03-REQ-014**
- depends_on -> **IF03-REQ-016**
- refines -> **SI01-REQ-025**
- specifies -> **UC-009**
- specifies -> **UC-022**

### Generated incoming

_None._

### Diagram references

_None._

## SI02-REQ-007

Type: req (Requirement)  
Title: Present committed registration history and live updates  
Source: docs/41-02-SSD-gui-application-specification-document.md:124

### Authored outgoing

- depends_on -> **IF03-REQ-014**
- depends_on -> **IF03-REQ-015**
- refines -> **SI01-REQ-042**
- specifies -> **UC-009**
- specifies -> **UC-022**

### Generated incoming

_None._

### Diagram references

_None._

## SI02-REQ-008

Type: req (Requirement)  
Title: Execute engineering controls with explicit outcome  
Source: docs/41-02-SSD-gui-application-specification-document.md:136

### Authored outgoing

- depends_on -> **IF03-REQ-008**
- depends_on -> **IF03-REQ-011**
- refines -> **SI01-REQ-026**
- refines -> **SI01-REQ-040**
- specifies -> **UC-009**
- specifies -> **UC-023**

### Generated incoming

_None._

### Diagram references

_None._

## ScheduledTaskRunner

Type: arch (Architecture Element)  
Title: ScheduledTaskRunner  
Source: docs/41-01-SSD-timing-application-specification-document.md:1717

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-CooperativeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:408 (diagram=layered-architecture, node=platform-execution)

## SerialExecutor

Type: arch (Architecture Element)  
Title: SerialExecutor  
Source: docs/41-01-SSD-timing-application-specification-document.md:1694

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RuntimeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:402 (diagram=layered-architecture, node=platform-execution)

## SerialScheduledExecutor

Type: arch (Architecture Element)  
Title: SerialScheduledExecutor  
Source: docs/41-01-SSD-timing-application-specification-document.md:1701

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RuntimeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:404 (diagram=layered-architecture, node=platform-execution)

## SerialTaskRunner

Type: arch (Architecture Element)  
Title: SerialTaskRunner  
Source: docs/41-01-SSD-timing-application-specification-document.md:1709

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-CooperativeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:406 (diagram=layered-architecture, node=platform-execution)

## SharedTerminalHandler

Type: arch (Architecture Element)  
Title: SharedTerminalHandler  
Source: docs/41-01-SSD-timing-application-specification-document.md:978

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:148 (diagram=layered-architecture, node=shared-terminal)

## SimulatedAntenna

Type: arch (Architecture Element)  
Title: SimulatedAntenna  
Source: docs/41-01-SSD-timing-application-specification-document.md:1551

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:338 (diagram=layered-architecture, node=devices-io)

## SimulatedPowerDevice

Type: arch (Architecture Element)  
Title: SimulatedPowerDevice  
Source: docs/41-01-SSD-timing-application-specification-document.md:1543

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:345 (diagram=layered-architecture, node=devices-io)

## SimulationRuntime

Type: arch (Architecture Element)  
Title: SimulationRuntime  
Source: docs/41-01-SSD-timing-application-specification-document.md:796

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:461 (diagram=layered-architecture, node=simulation-runtime)

## StageStartTimes

Type: arch (Architecture Element)  
Title: StageStartTimes  
Source: docs/41-01-SSD-timing-application-specification-document.md:1201

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:245 (diagram=layered-architecture, node=stage-start-times)

## StageTiming

Type: arch (Architecture Element)  
Title: StageTiming  
Source: docs/41-01-SSD-timing-application-specification-document.md:1235

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:269 (diagram=layered-architecture, node=stage-timing)

## Storage

Type: arch (Architecture Element)  
Title: Storage  
Source: docs/41-01-SSD-timing-application-specification-document.md:1461

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:314 (diagram=layered-architecture, node=storage-io)

## SystemConductor

Type: arch (Architecture Element)  
Title: TimingSystem Conductor  
Source: docs/41-01-SSD-timing-application-specification-document.md:1134

### Authored outgoing

- realizes -> **SI01-REQ-053**

### Generated incoming

- elaborates <- **DD-CooperativeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:201 (diagram=layered-architecture, node=system-conductor)

## SystemStatus

Type: arch (Architecture Element)  
Title: SystemStatus  
Source: docs/41-01-SSD-timing-application-specification-document.md:1871

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:210 (diagram=layered-architecture, node=system-status-domain)

## SystemUpstreamMessagePort

Type: arch (Architecture Element)  
Title: TimingSystem UpstreamMessagePort  
Source: docs/41-01-SSD-timing-application-specification-document.md:1171

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:219 (diagram=layered-architecture, node=system-upstream-message-port)

## TagProcessor

Type: arch (Architecture Element)  
Title: TagProcessor  
Source: docs/41-01-SSD-timing-application-specification-document.md:1189

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-EventTagProcessing**
- elaborates <- **DD-RuntimeWorkAndMeasurements**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:237 (diagram=layered-architecture, node=tag-processor)

## TimeSource

Type: arch (Architecture Element)  
Title: TimeSource  
Source: docs/41-01-SSD-timing-application-specification-document.md:1788

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:445 (diagram=layered-architecture, node=platform-time)

## TimingApplicationRuntime

Type: arch (Architecture Element)  
Title: TimingApplicationRuntime  
Source: docs/41-01-SSD-timing-application-specification-document.md:786

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:453 (diagram=layered-architecture, node=timing-application-runtime)

## TimingData

Type: arch (Architecture Element)  
Title: TimingData  
Source: docs/41-01-SSD-timing-application-specification-document.md:1904

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExtensionAndComposition**
- elaborates <- **DD-TimingDataProfiles**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:296 (diagram=layered-architecture, node=timing-data-domain)

## TimingNode

Type: arch (Architecture Element)  
Title: TimingNode  
Source: docs/41-01-SSD-timing-application-specification-document.md:1882

### Authored outgoing

- realizes -> **SI01-REQ-003**
- realizes -> **SI01-REQ-020**
- realizes -> **SI01-REQ-021**
- realizes -> **SI01-REQ-024**

### Generated incoming

- elaborates <- **DD-RuntimeWorkAndMeasurements**
- elaborates <- **DD-TimingNodeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:60 (diagram=layered-architecture, node=timing-node-aggregate)

## TimingNodeProxy

Type: arch (Architecture Element)  
Title: TimingNodeProxy  
Source: docs/41-01-SSD-timing-application-specification-document.md:1057

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-PresentationAccess**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:176 (diagram=layered-architecture, node=timing-node-proxy)

## TimingNodeUpstreamMessagePort

Type: arch (Architecture Element)  
Title: TimingNode UpstreamMessagePort  
Source: docs/41-01-SSD-timing-application-specification-document.md:1180

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:228 (diagram=layered-architecture, node=upstream-message-port)

## TimingSystem

Type: arch (Architecture Element)  
Title: TimingSystem  
Source: docs/41-01-SSD-timing-application-specification-document.md:1859

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**
- elaborates <- **DD-IOComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:51 (diagram=layered-architecture, node=timing-system-aggregate)

## UC-001

Type: uc (Use Case)  
Title: Open a registration point  
Source: docs/30-UC-system-use-cases.md:128

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-022**
- specifies <- **SI01-REQ-023**
- specifies <- **SI01-REQ-024**
- specifies <- **SI01-REQ-025**
- specifies <- **SI01-REQ-026**
- specifies <- **SI01-REQ-040**
- specifies <- **SI01-REQ-073**
- specifies <- **SI01-REQ-074**

### Diagram references

_None._

## UC-002

Type: uc (Use Case)  
Title: Close a registration point  
Source: docs/30-UC-system-use-cases.md:175

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-022**
- specifies <- **SI01-REQ-023**
- specifies <- **SI01-REQ-024**
- specifies <- **SI01-REQ-025**
- specifies <- **SI01-REQ-026**
- specifies <- **SI01-REQ-072**
- specifies <- **SI01-REQ-073**

### Diagram references

_None._

## UC-003

Type: uc (Use Case)  
Title: Register a participant through RFID  
Source: docs/30-UC-system-use-cases.md:213

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-041**
- specifies <- **SI01-REQ-042**
- specifies <- **SI01-REQ-046**
- specifies <- **SI01-REQ-050**
- specifies <- **SI01-REQ-051**
- specifies <- **SI01-REQ-052**
- specifies <- **SI01-REQ-053**
- specifies <- **SI01-REQ-054**

### Diagram references

_None._

## UC-004

Type: uc (Use Case)  
Title: Recover or reinitialise RFID equipment  
Source: docs/30-UC-system-use-cases.md:392

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-052**
- specifies <- **SI01-REQ-055**

### Diagram references

_None._

## UC-005

Type: uc (Use Case)  
Title: Manage ready teams through keypad/operator input  
Source: docs/30-UC-system-use-cases.md:296

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-060**

### Diagram references

_None._

## UC-006

Type: uc (Use Case)  
Title: Drive a passive CAN display from current system state  
Source: docs/30-UC-system-use-cases.md:315

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-061**

### Diagram references

_None._

## UC-007

Type: uc (Use Case)  
Title: Provide data to a smart network display  
Source: docs/30-UC-system-use-cases.md:332

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-062**

### Diagram references

_None._

## UC-009

Type: uc (Use Case)  
Title: Exercise the registration system through the Engineering Client  
Source: docs/30-UC-system-use-cases.md:512

### Authored outgoing

_None._

### Generated incoming

- specifies <- **IF03-REQ-003**
- specifies <- **IF03-REQ-012**
- specifies <- **IF03-REQ-013**
- specifies <- **SI01-REQ-020**
- specifies <- **SI01-REQ-021**
- specifies <- **SI01-REQ-022**
- specifies <- **SI01-REQ-023**
- specifies <- **SI01-REQ-024**
- specifies <- **SI01-REQ-025**
- specifies <- **SI01-REQ-026**
- specifies <- **SI01-REQ-040**
- specifies <- **SI01-REQ-041**
- specifies <- **SI01-REQ-042**
- specifies <- **SI01-REQ-043**
- specifies <- **SI01-REQ-044**
- specifies <- **SI02-REQ-001**
- specifies <- **SI02-REQ-002**
- specifies <- **SI02-REQ-003**
- specifies <- **SI02-REQ-004**
- specifies <- **SI02-REQ-005**
- specifies <- **SI02-REQ-006**
- specifies <- **SI02-REQ-007**
- specifies <- **SI02-REQ-008**

### Diagram references

_None._

## UC-010

Type: uc (Use Case)  
Title: Synchronise reference data from backoffice  
Source: docs/30-UC-system-use-cases.md:351

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-063**

### Diagram references

_None._

## UC-011

Type: uc (Use Case)  
Title: Synchronise TimingNodeId-scoped data to backoffice  
Source: docs/30-UC-system-use-cases.md:373

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-042**
- specifies <- **SI01-REQ-045**
- specifies <- **SI01-REQ-064**
- specifies <- **SI01-REQ-065**

### Diagram references

_None._

## UC-012

Type: uc (Use Case)  
Title: Continue local operation during backoffice outage  
Source: docs/30-UC-system-use-cases.md:429

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-046**
- specifies <- **SI01-REQ-051**
- specifies <- **SI01-REQ-065**

### Diagram references

_None._

## UC-013

Type: uc (Use Case)  
Title: Restart and restore local state  
Source: docs/30-UC-system-use-cases.md:446

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-047**
- specifies <- **SI01-REQ-048**

### Diagram references

_None._

## UC-014

Type: uc (Use Case)  
Title: Run multiple TimingNodes in one process  
Source: docs/30-UC-system-use-cases.md:654

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-003**

### Diagram references

_None._

## UC-015

Type: uc (Use Case)  
Title: Simulate a complete field toward backoffice  
Source: docs/30-UC-system-use-cases.md:679

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-003**
- specifies <- **SI01-REQ-031**
- specifies <- **SI01-REQ-066**

### Diagram references

_None._

## UC-016

Type: uc (Use Case)  
Title: Replace real devices with controllable stubs  
Source: docs/30-UC-system-use-cases.md:696

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-031**
- specifies <- **SI01-REQ-067**

### Diagram references

_None._

## UC-017

Type: uc (Use Case)  
Title: Use an alternative backoffice transport for loop testing  
Source: docs/30-UC-system-use-cases.md:713

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-068**

### Diagram references

_None._

## UC-018

Type: uc (Use Case)  
Title: Verify production-shaped messaging through RabbitMQ  
Source: docs/30-UC-system-use-cases.md:731

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-069**

### Diagram references

_None._

## UC-019

Type: uc (Use Case)  
Title: Handle provider-specific input classification  
Source: docs/30-UC-system-use-cases.md:749

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-070**

### Diagram references

_None._

## UC-020

Type: uc (Use Case)  
Title: Diagnose degraded TimingNode startup  
Source: docs/30-UC-system-use-cases.md:465

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-021**
- specifies <- **SI01-REQ-024**
- specifies <- **SI01-REQ-049**

### Diagram references

_None._

## UC-021

Type: uc (Use Case)  
Title: Manually register a participant using an iPad  
Source: docs/30-UC-system-use-cases.md:253

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-041**
- specifies <- **SI01-REQ-042**
- specifies <- **SI01-REQ-046**
- specifies <- **SI01-REQ-071**

### Diagram references

_None._

## UC-022

Type: uc (Use Case)  
Title: Inspect registration state and history with the Engineering Client  
Source: docs/30-UC-system-use-cases.md:555

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI02-REQ-004**
- specifies <- **SI02-REQ-005**
- specifies <- **SI02-REQ-006**
- specifies <- **SI02-REQ-007**

### Diagram references

_None._

## UC-023

Type: uc (Use Case)  
Title: Exercise registration controls with the Engineering Client  
Source: docs/30-UC-system-use-cases.md:587

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI02-REQ-008**

### Diagram references

_None._

## UC-024

Type: uc (Use Case)  
Title: Simulate participant passage and device failure for verification  
Source: docs/30-UC-system-use-cases.md:621

### Authored outgoing

_None._

### Generated incoming

- specifies <- **SI01-REQ-066**
- specifies <- **SI01-REQ-067**

### Diagram references

_None._

## UpstreamGateway

Type: arch (Architecture Element)  
Title: UpstreamGateway  
Source: docs/41-01-SSD-timing-application-specification-document.md:1626

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:383 (diagram=layered-architecture, node=messaging-io)

## UpstreamMessageRouter

Type: arch (Architecture Element)  
Title: UpstreamMessageRouter  
Source: docs/41-01-SSD-timing-application-specification-document.md:1079

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:192 (diagram=layered-architecture, node=upstream-message-router)

## UpstreamProtocol

Type: arch (Architecture Element)  
Title: UpstreamProtocol  
Source: docs/41-01-SSD-timing-application-specification-document.md:1914

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:305 (diagram=layered-architecture, node=upstream-protocol-domain)

## VC-ST1-001

Type: vc (Verification Case)  
Title: Query and resynchronise first-executable status  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:85

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
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:135

### Authored outgoing

- verifies -> **IF03-REQ-011**
- verifies -> **IF03-REQ-012**
- verifies -> **IF03-REQ-013**
- verifies -> **IF03-REQ-014**
- verifies -> **IF03-REQ-015**
- verifies -> **IF05-REQ-003**
- verifies -> **IF05-REQ-008**
- verifies -> **IF05-REQ-009**
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
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:210

### Authored outgoing

- verifies -> **IF03-REQ-016**
- verifies -> **IF03-REQ-022**
- verifies -> **IF05-REQ-006**
- verifies -> **IF05-REQ-007**
- verifies -> **IF05-REQ-008**
- verifies -> **SI01-REQ-044**

### Generated incoming

_None._

### Diagram references

_None._

## VC-ST1-004

Type: vc (Verification Case)  
Title: Contain TimingData recovery failure and keep diagnostics available  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:271

### Authored outgoing

- verifies -> **IF03-REQ-004**
- verifies -> **IF03-REQ-006**
- verifies -> **IF03-REQ-008**
- verifies -> **IF03-REQ-017**
- verifies -> **SI01-REQ-048**

### Generated incoming

_None._

### Diagram references

_None._

## VC-ST1-005

Type: vc (Verification Case)  
Title: Verify lifecycle TimingData source ordering and recovery  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:307

### Authored outgoing

- verifies -> **IF03-REQ-011**
- verifies -> **IF03-REQ-014**
- verifies -> **IF03-REQ-015**
- verifies -> **IF05-REQ-002**
- verifies -> **IF05-REQ-003**
- verifies -> **IF05-REQ-008**
- verifies -> **IF05-REQ-009**
- verifies -> **IF05-REQ-010**

### Generated incoming

_None._

### Diagram references

_None._

## VC-ST1-006

Type: vc (Verification Case)  
Title: Verify append-only registration revoke bookkeeping  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:347

### Authored outgoing

- verifies -> **IF03-REQ-008**
- verifies -> **IF03-REQ-014**
- verifies -> **IF03-REQ-015**
- verifies -> **IF03-REQ-022**
- verifies -> **IF05-REQ-002**
- verifies -> **IF05-REQ-003**
- verifies -> **IF05-REQ-005**
- verifies -> **IF05-REQ-006**
- verifies -> **IF05-REQ-007**

### Generated incoming

_None._

### Diagram references

_None._

## VC-ST1-007

Type: vc (Verification Case)  
Title: Verify two TimingNodes in one TimingSystem with separate LogBooks  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:401

### Authored outgoing

- verifies -> **IF03-REQ-011**
- verifies -> **IF03-REQ-013**
- verifies -> **IF03-REQ-014**
- verifies -> **IF03-REQ-015**
- verifies -> **IF05-REQ-003**
- verifies -> **IF05-REQ-008**
- verifies -> **IF05-REQ-009**
- verifies -> **SI01-REQ-003**
- verifies -> **SI01-REQ-041**
- verifies -> **SI01-REQ-042**
- verifies -> **SI01-REQ-046**
- verifies -> **SI01-REQ-047**

### Generated incoming

_None._

### Diagram references

_None._

## VC-ST1-008

Type: vc (Verification Case)  
Title: Verify two TimingSystems with one TimingNode each and separate LogBooks  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:450

### Authored outgoing

- verifies -> **IF03-REQ-011**
- verifies -> **IF03-REQ-013**
- verifies -> **IF03-REQ-014**
- verifies -> **IF03-REQ-015**
- verifies -> **IF05-REQ-003**
- verifies -> **IF05-REQ-008**
- verifies -> **IF05-REQ-009**
- verifies -> **SI01-REQ-003**
- verifies -> **SI01-REQ-041**
- verifies -> **SI01-REQ-042**
- verifies -> **SI01-REQ-046**
- verifies -> **SI01-REQ-047**

### Generated incoming

_None._

### Diagram references

_None._

## VendorAntenna

Type: arch (Architecture Element)  
Title: VendorAntenna  
Source: docs/41-01-SSD-timing-application-specification-document.md:1558

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:340 (diagram=layered-architecture, node=devices-io)

## Web

Type: arch (Architecture Element)  
Title: Web  
Source: docs/41-01-SSD-timing-application-specification-document.md:946

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:126 (diagram=layered-architecture, node=web-interface)
