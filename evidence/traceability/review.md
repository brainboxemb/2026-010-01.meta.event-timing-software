# Engineering graph review

Source revision: 224a41f3598db02998de031a400008cdc4a770e6
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
| [DD-DomainIntegration](#dd-domainintegration) | design | 6 | 0 | 0 |
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
| [DD-TimingNodeExecution](#dd-timingnodeexecution) | design | 7 | 0 | 0 |
| [DD-TimingTimeComposition](#dd-timingtimecomposition) | design | 5 | 0 | 0 |
| [DeviceNetworks](#devicenetworks) | arch | 0 | 0 | 1 |
| [Devices](#devices) | arch | 0 | 0 | 1 |
| [Display](#display) | arch | 0 | 0 | 1 |
| [EngineeringApiConnector](#engineeringapiconnector) | arch | 0 | 0 | 1 |
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
| [IF03-REQ-012](#if03-req-012) | ifreq | 1 | 3 | 0 |
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
| [IF03-REQ-024](#if03-req-024) | ifreq | 0 | 1 | 0 |
| [IF03-REQ-025](#if03-req-025) | ifreq | 2 | 0 | 0 |
| [IF03-REQ-026](#if03-req-026) | ifreq | 2 | 0 | 0 |
| [IF03-REQ-027](#if03-req-027) | ifreq | 4 | 0 | 0 |
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
| [IF06-REQ-001](#if06-req-001) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-002](#if06-req-002) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-003](#if06-req-003) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-004](#if06-req-004) | ifreq | 0 | 1 | 0 |
| [IF06-REQ-005](#if06-req-005) | ifreq | 0 | 1 | 0 |
| [IF06-REQ-006](#if06-req-006) | ifreq | 0 | 1 | 0 |
| [IF06-REQ-007](#if06-req-007) | ifreq | 0 | 1 | 0 |
| [IF06-REQ-008](#if06-req-008) | ifreq | 0 | 1 | 0 |
| [IF06-REQ-009](#if06-req-009) | ifreq | 0 | 0 | 0 |
| [IF06-REQ-010](#if06-req-010) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-011](#if06-req-011) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-012](#if06-req-012) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-013](#if06-req-013) | ifreq | 0 | 3 | 0 |
| [IF06-REQ-014](#if06-req-014) | ifreq | 0 | 1 | 0 |
| [IF06-REQ-015](#if06-req-015) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-016](#if06-req-016) | ifreq | 0 | 1 | 0 |
| [IF06-REQ-017](#if06-req-017) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-018](#if06-req-018) | ifreq | 0 | 0 | 0 |
| [IF06-REQ-019](#if06-req-019) | ifreq | 0 | 1 | 0 |
| [IF06-REQ-020](#if06-req-020) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-021](#if06-req-021) | ifreq | 0 | 1 | 0 |
| [Keypad](#keypad) | arch | 0 | 0 | 1 |
| [LogBook](#logbook) | arch | 0 | 1 | 1 |
| [LogBookProcessor](#logbookprocessor) | arch | 0 | 1 | 0 |
| [Logging](#logging) | arch | 0 | 1 | 1 |
| [LoggingServer](#loggingserver) | arch | 0 | 1 | 1 |
| [Messaging](#messaging) | arch | 0 | 0 | 1 |
| [MonotonicClock](#monotonicclock) | arch | 0 | 0 | 1 |
| [NetworkDeviceService](#networkdeviceservice) | arch | 0 | 1 | 1 |
| [NextUpTeams](#nextupteams) | arch | 0 | 0 | 1 |
| [NodeTaskProcessor](#nodetaskprocessor) | arch | 0 | 1 | 0 |
| [OperatingSystem](#operatingsystem) | arch | 0 | 0 | 1 |
| [PlatformEnvironment](#platformenvironment) | arch | 0 | 1 | 1 |
| [PlatformEvents](#platformevents) | arch | 0 | 1 | 1 |
| [PlatformExecution](#platformexecution) | arch | 0 | 3 | 1 |
| [PlatformTime](#platformtime) | arch | 0 | 1 | 1 |
| [PowerDevice](#powerdevice) | arch | 0 | 1 | 1 |
| [PresentationGateway](#presentationgateway) | arch | 5 | 1 | 1 |
| [PresentationRuntime](#presentationruntime) | arch | 0 | 1 | 1 |
| [RabbitMqConnector](#rabbitmqconnector) | arch | 0 | 0 | 1 |
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
| [SI01-REQ-042](#si01-req-042) | req | 4 | 12 | 0 |
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
| [SI01-REQ-063](#si01-req-063) | req | 3 | 2 | 0 |
| [SI01-REQ-064](#si01-req-064) | req | 7 | 4 | 0 |
| [SI01-REQ-065](#si01-req-065) | req | 5 | 2 | 0 |
| [SI01-REQ-066](#si01-req-066) | req | 4 | 0 | 0 |
| [SI01-REQ-067](#si01-req-067) | req | 3 | 0 | 0 |
| [SI01-REQ-068](#si01-req-068) | req | 2 | 3 | 0 |
| [SI01-REQ-069](#si01-req-069) | req | 3 | 0 | 0 |
| [SI01-REQ-070](#si01-req-070) | req | 1 | 0 | 0 |
| [SI01-REQ-071](#si01-req-071) | req | 3 | 2 | 0 |
| [SI01-REQ-072](#si01-req-072) | req | 3 | 3 | 0 |
| [SI01-REQ-073](#si01-req-073) | req | 3 | 0 | 0 |
| [SI01-REQ-074](#si01-req-074) | req | 4 | 0 | 0 |
| [SI01-REQ-075](#si01-req-075) | req | 3 | 1 | 0 |
| [SI01-REQ-076](#si01-req-076) | req | 1 | 1 | 0 |
| [SI01-REQ-077](#si01-req-077) | req | 3 | 2 | 0 |
| [SI01-REQ-078](#si01-req-078) | req | 6 | 3 | 0 |
| [SI01-REQ-079](#si01-req-079) | req | 3 | 1 | 0 |
| [SI01-REQ-080](#si01-req-080) | req | 3 | 0 | 0 |
| [SI01-REQ-081](#si01-req-081) | req | 6 | 4 | 0 |
| [SI01-REQ-082](#si01-req-082) | req | 5 | 1 | 0 |
| [SI01-REQ-083](#si01-req-083) | req | 4 | 0 | 0 |
| [SI01-REQ-084](#si01-req-084) | req | 4 | 1 | 0 |
| [SI01-REQ-085](#si01-req-085) | req | 6 | 1 | 0 |
| [SI02-REQ-001](#si02-req-001) | req | 3 | 0 | 0 |
| [SI02-REQ-002](#si02-req-002) | req | 3 | 0 | 0 |
| [SI02-REQ-003](#si02-req-003) | req | 2 | 0 | 0 |
| [SI02-REQ-004](#si02-req-004) | req | 7 | 0 | 0 |
| [SI02-REQ-005](#si02-req-005) | req | 5 | 0 | 0 |
| [SI02-REQ-006](#si02-req-006) | req | 6 | 0 | 0 |
| [SI02-REQ-007](#si02-req-007) | req | 5 | 0 | 0 |
| [SI02-REQ-008](#si02-req-008) | req | 6 | 0 | 0 |
| [SI02-REQ-009](#si02-req-009) | req | 2 | 0 | 0 |
| [SI02-REQ-010](#si02-req-010) | req | 3 | 0 | 0 |
| [ScheduledTaskRunner](#scheduledtaskrunner) | arch | 0 | 1 | 1 |
| [SerialLane](#seriallane) | arch | 0 | 1 | 1 |
| [SerialScheduledLane](#serialscheduledlane) | arch | 0 | 1 | 1 |
| [SerialTaskRunner](#serialtaskrunner) | arch | 0 | 1 | 1 |
| [Settings](#settings) | arch | 0 | 0 | 1 |
| [SharedTerminalHandler](#sharedterminalhandler) | arch | 0 | 1 | 1 |
| [SimulatedAntenna](#simulatedantenna) | arch | 0 | 1 | 1 |
| [SimulatedPowerDevice](#simulatedpowerdevice) | arch | 0 | 1 | 1 |
| [SimulationRuntime](#simulationruntime) | arch | 0 | 0 | 1 |
| [StagePassageList](#stagepassagelist) | arch | 0 | 0 | 1 |
| [StageRanking](#stageranking) | arch | 0 | 0 | 1 |
| [StageStartTimes](#stagestarttimes) | arch | 0 | 0 | 1 |
| [Storage](#storage) | arch | 0 | 0 | 1 |
| [SystemConductor](#systemconductor) | arch | 1 | 1 | 1 |
| [SystemStatus](#systemstatus) | arch | 0 | 1 | 1 |
| [TagProcessor](#tagprocessor) | arch | 0 | 2 | 1 |
| [TeamAssignments](#teamassignments) | arch | 0 | 0 | 1 |
| [TimeSource](#timesource) | arch | 0 | 1 | 1 |
| [TimingApplicationRuntime](#timingapplicationruntime) | arch | 0 | 1 | 1 |
| [TimingData](#timingdata) | arch | 0 | 2 | 1 |
| [TimingNode](#timingnode) | arch | 4 | 2 | 1 |
| [TimingNodeData](#timingnodedata) | arch | 0 | 0 | 1 |
| [TimingNodeProcessing](#timingnodeprocessing) | arch | 0 | 0 | 1 |
| [TimingNodeProxy](#timingnodeproxy) | arch | 0 | 1 | 1 |
| [TimingNodeRaceData](#timingnoderacedata) | arch | 0 | 0 | 1 |
| [TimingNodeTiming](#timingnodetiming) | arch | 0 | 0 | 1 |
| [TimingNodeUpstreamHandler](#timingnodeupstreamhandler) | arch | 0 | 1 | 1 |
| [TimingSystem](#timingsystem) | arch | 0 | 2 | 1 |
| [UC-001](#uc-001) | uc | 0 | 8 | 0 |
| [UC-002](#uc-002) | uc | 0 | 7 | 0 |
| [UC-003](#uc-003) | uc | 0 | 8 | 0 |
| [UC-004](#uc-004) | uc | 0 | 2 | 0 |
| [UC-005](#uc-005) | uc | 0 | 1 | 0 |
| [UC-006](#uc-006) | uc | 0 | 1 | 0 |
| [UC-007](#uc-007) | uc | 0 | 1 | 0 |
| [UC-009](#uc-009) | uc | 0 | 25 | 0 |
| [UC-010](#uc-010) | uc | 0 | 4 | 0 |
| [UC-011](#uc-011) | uc | 0 | 7 | 0 |
| [UC-012](#uc-012) | uc | 0 | 8 | 0 |
| [UC-013](#uc-013) | uc | 0 | 3 | 0 |
| [UC-014](#uc-014) | uc | 0 | 1 | 0 |
| [UC-015](#uc-015) | uc | 0 | 3 | 0 |
| [UC-016](#uc-016) | uc | 0 | 2 | 0 |
| [UC-017](#uc-017) | uc | 0 | 4 | 0 |
| [UC-018](#uc-018) | uc | 0 | 1 | 0 |
| [UC-019](#uc-019) | uc | 0 | 1 | 0 |
| [UC-020](#uc-020) | uc | 0 | 3 | 0 |
| [UC-021](#uc-021) | uc | 0 | 4 | 0 |
| [UC-022](#uc-022) | uc | 0 | 4 | 0 |
| [UC-023](#uc-023) | uc | 0 | 1 | 0 |
| [UC-024](#uc-024) | uc | 0 | 2 | 0 |
| [UniqueTeamRegistrations](#uniqueteamregistrations) | arch | 0 | 0 | 1 |
| [UpstreamData](#upstreamdata) | arch | 0 | 1 | 1 |
| [UpstreamGateway](#upstreamgateway) | arch | 0 | 1 | 1 |
| [UpstreamStream](#upstreamstream) | arch | 0 | 1 | 1 |
| [VC-ST1-001](#vc-st1-001) | vc | 11 | 0 | 0 |
| [VC-ST1-002](#vc-st1-002) | vc | 13 | 0 | 0 |
| [VC-ST1-003](#vc-st1-003) | vc | 6 | 0 | 0 |
| [VC-ST1-004](#vc-st1-004) | vc | 5 | 0 | 0 |
| [VC-ST1-005](#vc-st1-005) | vc | 8 | 0 | 0 |
| [VC-ST1-006](#vc-st1-006) | vc | 9 | 0 | 0 |
| [VC-ST1-007](#vc-st1-007) | vc | 12 | 0 | 0 |
| [VC-ST1-008](#vc-st1-008) | vc | 12 | 0 | 0 |
| [VC-ST1-009](#vc-st1-009) | vc | 5 | 0 | 0 |
| [VC-ST1-010](#vc-st1-010) | vc | 5 | 0 | 0 |
| [VendorAntenna](#vendorantenna) | arch | 0 | 0 | 1 |
| [Web](#web) | arch | 0 | 0 | 1 |

## Antenna

Type: arch (Architecture Element)  
Title: Antenna  
Source: docs/41-01-SSD-timing-application-specification-document.md:1793

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:347 (diagram=layered-architecture, node=devices-io)

## AntennaManager

Type: arch (Architecture Element)  
Title: AntennaManager  
Source: docs/41-01-SSD-timing-application-specification-document.md:1785

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:344 (diagram=layered-architecture, node=devices-io)

## Api

Type: arch (Architecture Element)  
Title: API  
Source: docs/41-01-SSD-timing-application-specification-document.md:1111

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
Source: docs/41-01-SSD-timing-application-specification-document.md:1196

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:159 (diagram=layered-architecture, node=application-conductor)

## ApplicationConfiguration

Type: arch (Architecture Element)  
Title: Application configuration  
Source: docs/41-01-SSD-timing-application-specification-document.md:2089

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RunningConfiguration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:507 (diagram=layered-architecture, node=application-configuration-runtime)

## Beeper

Type: arch (Architecture Element)  
Title: Beeper  
Source: docs/41-01-SSD-timing-application-specification-document.md:1872

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:371 (diagram=layered-architecture, node=devices-io)

## CanNetworkController

Type: arch (Architecture Element)  
Title: CanNetworkController  
Source: docs/41-01-SSD-timing-application-specification-document.md:1879

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-IOComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:383 (diagram=layered-architecture, node=device-network-io)

## ClockTimeSource

Type: arch (Architecture Element)  
Title: ClockTimeSource  
Source: docs/41-01-SSD-timing-application-specification-document.md:2075

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:461 (diagram=layered-architecture, node=platform-time)

## Configuration

Type: arch (Architecture Element)  
Title: Typed configuration values  
Source: docs/41-01-SSD-timing-application-specification-document.md:2098

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RunningConfiguration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:536 (diagram=layered-architecture, node=configuration-infra)

## ConfigurationControl

Type: arch (Architecture Element)  
Title: Configuration control  
Source: docs/41-01-SSD-timing-application-specification-document.md:1206

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RunningConfiguration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:184 (diagram=layered-architecture, node=configuration-control)

## Connector

Type: arch (Architecture Element)  
Title: Connector  
Source: docs/41-01-SSD-timing-application-specification-document.md:1912

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:400 (diagram=layered-architecture, node=messaging-io)

## Console

Type: arch (Architecture Element)  
Title: Console  
Source: docs/41-01-SSD-timing-application-specification-document.md:1143

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:106 (diagram=layered-architecture, node=local-console)

## CooperativeTaskController

Type: arch (Architecture Element)  
Title: CooperativeTaskController  
Source: docs/41-01-SSD-timing-application-specification-document.md:2002

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-CooperativeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:424 (diagram=layered-architecture, node=platform-execution)

## DD-AntennaRuntime

Type: design (Detailed Design)  
Title: Antenna runtime and device control  
Source: docs/43-01-SDD-02-java-component-design.md:1813

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
Source: docs/43-01-SDD-02-java-component-design.md:499

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
Source: docs/43-01-SDD-02-java-component-design.md:1059

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## DD-DomainIntegration

Type: design (Detailed Design)  
Title: Domain data, upstream and system-status composition  
Source: docs/43-01-SDD-02-java-component-design.md:997

### Authored outgoing

- elaborates -> **SystemStatus**
- elaborates -> **TimingNodeUpstreamHandler**
- elaborates -> **TimingSystem**
- elaborates -> **UpstreamData**
- elaborates -> **UpstreamGateway**
- elaborates -> **UpstreamStream**

### Generated incoming

_None._

### Diagram references

_None._

## DD-EventTagProcessing

Type: design (Detailed Design)  
Title: EventData and TagProcessor realization  
Source: docs/43-01-SDD-02-java-component-design.md:722

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
Source: docs/43-01-SDD-02-java-component-design.md:1296

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
Source: docs/43-01-SDD-02-java-component-design.md:3654

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
Source: docs/43-01-SDD-02-java-component-design.md:969

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
Source: docs/43-01-SDD-02-java-component-design.md:1176

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
Source: docs/43-01-SDD-02-java-component-design.md:842

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
Source: docs/43-01-SDD-02-java-component-design.md:1559

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
Source: docs/43-01-SDD-02-java-component-design.md:2734

### Authored outgoing

- elaborates -> **PlatformExecution**
- elaborates -> **RuntimeExecutors**
- elaborates -> **SerialLane**
- elaborates -> **SerialScheduledLane**

### Generated incoming

_None._

### Diagram references

_None._

## DD-RuntimeWorkAndMeasurements

Type: design (Detailed Design)  
Title: Registration workload and runtime measurement  
Source: docs/43-01-SDD-02-java-component-design.md:2542

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
Source: docs/43-01-SDD-02-java-component-design.md:3446

### Authored outgoing

- elaborates -> **TimingData**

### Generated incoming

_None._

### Diagram references

_None._

## DD-TimingNodeExecution

Type: design (Detailed Design)  
Title: TimingNode execution, LogBook and local events  
Source: docs/43-01-SDD-02-java-component-design.md:2841

### Authored outgoing

- elaborates -> **Event**
- elaborates -> **EventSource**
- elaborates -> **LogBook**
- elaborates -> **LogBookProcessor**
- elaborates -> **NodeTaskProcessor**
- elaborates -> **PlatformEvents**
- elaborates -> **TimingNode**

### Generated incoming

_None._

### Diagram references

_None._

## DD-TimingTimeComposition

Type: design (Detailed Design)  
Title: Timing-time composition  
Source: docs/43-01-SDD-02-java-component-design.md:948

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

## DeviceNetworks

Type: arch (Architecture Element)  
Title: DeviceNetworks  
Source: docs/41-01-SSD-timing-application-specification-document.md:1748

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:378 (diagram=layered-architecture, node=device-network-io)

## Devices

Type: arch (Architecture Element)  
Title: Devices  
Source: docs/41-01-SSD-timing-application-specification-document.md:1733

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:339 (diagram=layered-architecture, node=devices-io)

## Display

Type: arch (Architecture Element)  
Title: Display  
Source: docs/41-01-SSD-timing-application-specification-document.md:1836

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:359 (diagram=layered-architecture, node=devices-io)

## EngineeringApiConnector

Type: arch (Architecture Element)  
Title: EngineeringApiConnector  
Source: docs/41-01-SSD-timing-application-specification-document.md:1927

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:405 (diagram=layered-architecture, node=messaging-io)

## Event

Type: arch (Architecture Element)  
Title: Event  
Source: docs/41-01-SSD-timing-application-specification-document.md:2018

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:434 (diagram=layered-architecture, node=platform-events)

## EventData

Type: arch (Architecture Element)  
Title: EventData  
Source: docs/41-01-SSD-timing-application-specification-document.md:1464

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-EventTagProcessing**
- elaborates <- **DD-ExtensionAndComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:298 (diagram=layered-architecture, node=event-data-domain)

## EventSource

Type: arch (Architecture Element)  
Title: EventSource  
Source: docs/41-01-SSD-timing-application-specification-document.md:2025

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:436 (diagram=layered-architecture, node=platform-events)

## IF03-REQ-001

Type: ifreq (Interface Requirement)  
Title: Shared application semantics  
Source: docs/32-03-ISD-application-control-status.md:443

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
Source: docs/32-03-ISD-application-control-status.md:452

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
Source: docs/32-03-ISD-application-control-status.md:461

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
Source: docs/32-03-ISD-application-control-status.md:469

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
Source: docs/32-03-ISD-application-control-status.md:477

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
Source: docs/32-03-ISD-application-control-status.md:485

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
Source: docs/32-03-ISD-application-control-status.md:494

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI02-REQ-001**

### Diagram references

_None._

## IF03-REQ-008

Type: ifreq (Interface Requirement)  
Title: Explicit failure outcome  
Source: docs/32-03-ISD-application-control-status.md:503

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
Source: docs/32-03-ISD-application-control-status.md:512

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI02-REQ-002**

### Diagram references

_None._

## IF03-REQ-010

Type: ifreq (Interface Requirement)  
Title: Compatible extension  
Source: docs/32-03-ISD-application-control-status.md:521

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-011

Type: ifreq (Interface Requirement)  
Title: TimingNode location and lifecycle control  
Source: docs/32-03-ISD-application-control-status.md:530

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
Source: docs/32-03-ISD-application-control-status.md:541

### Authored outgoing

- specifies -> **UC-009**

### Generated incoming

- depends_on <- **SI02-REQ-009**
- depends_on <- **SI02-REQ-010**
- verifies <- **VC-ST1-002**

### Diagram references

_None._

## IF03-REQ-013

Type: ifreq (Interface Requirement)  
Title: Direct accepted-registration simulation  
Source: docs/32-03-ISD-application-control-status.md:550

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
Source: docs/32-03-ISD-application-control-status.md:564

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
Source: docs/32-03-ISD-application-control-status.md:573

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
Source: docs/32-03-ISD-application-control-status.md:582

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
Source: docs/32-03-ISD-application-control-status.md:714

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
Source: docs/32-03-ISD-application-control-status.md:606

### Authored outgoing

- depends_on -> **SI01-REQ-001**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-019

Type: ifreq (Interface Requirement)  
Title: Runtime configuration override  
Source: docs/32-03-ISD-application-control-status.md:616

### Authored outgoing

- depends_on -> **SI01-REQ-001**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-020

Type: ifreq (Interface Requirement)  
Title: Runtime configuration change notification  
Source: docs/32-03-ISD-application-control-status.md:627

### Authored outgoing

- depends_on -> **SI01-REQ-001**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-021

Type: ifreq (Interface Requirement)  
Title: Bounded live-event delivery  
Source: docs/32-03-ISD-application-control-status.md:593

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI02-REQ-005**

### Diagram references

_None._

## IF03-REQ-022

Type: ifreq (Interface Requirement)  
Title: Registration revoke  
Source: docs/32-03-ISD-application-control-status.md:638

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
Source: docs/32-03-ISD-application-control-status.md:650

### Authored outgoing

- refines -> **SI01-REQ-071**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-024

Type: ifreq (Interface Requirement)  
Title: Simulated tag passage control  
Source: docs/32-03-ISD-application-control-status.md:701

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI02-REQ-010**

### Diagram references

_None._

## IF03-REQ-025

Type: ifreq (Interface Requirement)  
Title: Engineering backoffice UpstreamData ingress  
Source: docs/32-03-ISD-application-control-status.md:662

### Authored outgoing

- refines -> **SI01-REQ-068**
- specifies -> **UC-017**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-026

Type: ifreq (Interface Requirement)  
Title: Reuse one IF-03 event connection for the Central System simulator peer  
Source: docs/32-03-ISD-application-control-status.md:674

### Authored outgoing

- refines -> **SI01-REQ-068**
- specifies -> **UC-017**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-027

Type: ifreq (Interface Requirement)  
Title: Expose Engineering API upstream connection and sync status  
Source: docs/32-03-ISD-application-control-status.md:688

### Authored outgoing

- refines -> **SI01-REQ-068**
- refines -> **SI01-REQ-084**
- refines -> **SI01-REQ-085**
- specifies -> **UC-017**

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

## IF06-REQ-001

Type: ifreq (Interface Requirement)  
Title: Transport-independent UpstreamData semantics  
Source: docs/32-06-ISD-backend-integration.md:415

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-064**
- verifies <- **VC-ST1-010**

### Diagram references

_None._

## IF06-REQ-002

Type: ifreq (Interface Requirement)  
Title: Preserve TimingData semantics  
Source: docs/32-06-ISD-backend-integration.md:423

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-064**
- verifies <- **VC-ST1-010**

### Diagram references

_None._

## IF06-REQ-003

Type: ifreq (Interface Requirement)  
Title: Keep transport identity separate from TimingData identity  
Source: docs/32-06-ISD-backend-integration.md:432

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-064**
- verifies <- **VC-ST1-010**

### Diagram references

_None._

## IF06-REQ-004

Type: ifreq (Interface Requirement)  
Title: Support node-scoped reference data  
Source: docs/32-06-ISD-backend-integration.md:440

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-063**

### Diagram references

_None._

## IF06-REQ-005

Type: ifreq (Interface Requirement)  
Title: Explicit reference-data outcome  
Source: docs/32-06-ISD-backend-integration.md:449

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-063**

### Diagram references

_None._

## IF06-REQ-006

Type: ifreq (Interface Requirement)  
Title: Synchronization preserves source identity  
Source: docs/32-06-ISD-backend-integration.md:458

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-065**

### Diagram references

_None._

## IF06-REQ-007

Type: ifreq (Interface Requirement)  
Title: Local TimingData commit independent from backend delivery  
Source: docs/32-06-ISD-backend-integration.md:467

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-065**

### Diagram references

_None._

## IF06-REQ-008

Type: ifreq (Interface Requirement)  
Title: Public default JSON representation  
Source: docs/32-06-ISD-backend-integration.md:476

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-010**

### Diagram references

_None._

## IF06-REQ-009

Type: ifreq (Interface Requirement)  
Title: Alternative representation support  
Source: docs/32-06-ISD-backend-integration.md:487

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## IF06-REQ-010

Type: ifreq (Interface Requirement)  
Title: Connector transport independence  
Source: docs/32-06-ISD-backend-integration.md:496

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-064**
- verifies <- **VC-ST1-010**

### Diagram references

_None._

## IF06-REQ-011

Type: ifreq (Interface Requirement)  
Title: Immediate upstream PING on connect  
Source: docs/32-06-ISD-backend-integration.md:592

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-075**
- verifies <- **VC-ST1-009**

### Diagram references

_None._

## IF06-REQ-012

Type: ifreq (Interface Requirement)  
Title: Periodic upstream PING while connected  
Source: docs/32-06-ISD-backend-integration.md:601

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-075**
- verifies <- **VC-ST1-009**

### Diagram references

_None._

## IF06-REQ-013

Type: ifreq (Interface Requirement)  
Title: PING request op, answer and optional heartbeat mode  
Source: docs/32-06-ISD-backend-integration.md:613

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-075**
- depends_on <- **SI01-REQ-076**
- verifies <- **VC-ST1-009**

### Diagram references

_None._

## IF06-REQ-014

Type: ifreq (Interface Requirement)  
Title: Ordered RaceData application and acknowledgement  
Source: docs/32-06-ISD-backend-integration.md:557

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-078**

### Diagram references

_None._

## IF06-REQ-015

Type: ifreq (Interface Requirement)  
Title: Separate stable EventData from live RaceData  
Source: docs/32-06-ISD-backend-integration.md:568

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-077**
- depends_on <- **SI01-REQ-078**

### Diagram references

_None._

## IF06-REQ-016

Type: ifreq (Interface Requirement)  
Title: Define StageStartTimes reference semantics  
Source: docs/32-06-ISD-backend-integration.md:579

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-079**

### Diagram references

_None._

## IF06-REQ-017

Type: ifreq (Interface Requirement)  
Title: Synchronize by contiguous TimingData source sequence  
Source: docs/32-06-ISD-backend-integration.md:505

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-081**
- depends_on <- **SI01-REQ-084**

### Diagram references

_None._

## IF06-REQ-018

Type: ifreq (Interface Requirement)  
Title: Keep transport acknowledgement separate from semantic acknowledgement  
Source: docs/32-06-ISD-backend-integration.md:516

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## IF06-REQ-019

Type: ifreq (Interface Requirement)  
Title: Make TimingData retransmission idempotent by record identity  
Source: docs/32-06-ISD-backend-integration.md:526

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-082**

### Diagram references

_None._

## IF06-REQ-020

Type: ifreq (Interface Requirement)  
Title: Reconcile reference-data freshness through SYNC state  
Source: docs/32-06-ISD-backend-integration.md:536

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-082**
- depends_on <- **SI01-REQ-084**

### Diagram references

_None._

## IF06-REQ-021

Type: ifreq (Interface Requirement)  
Title: Re-establish synchronization after connection changes  
Source: docs/32-06-ISD-backend-integration.md:546

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-085**

### Diagram references

_None._

## Keypad

Type: arch (Architecture Element)  
Title: Keypad  
Source: docs/41-01-SSD-timing-application-specification-document.md:1858

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:366 (diagram=layered-architecture, node=devices-io)

## LogBook

Type: arch (Architecture Element)  
Title: LogBook  
Source: docs/41-01-SSD-timing-application-specification-document.md:2182

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:274 (diagram=layered-architecture, node=node-data)

## LogBookProcessor

Type: arch (Architecture Element)  
Title: LogBookProcessor  
Source: docs/41-01-SSD-timing-application-specification-document.md:2398

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

_None._

## Logging

Type: arch (Architecture Element)  
Title: Logging  
Source: docs/41-01-SSD-timing-application-specification-document.md:2126

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-LoggingRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:523 (diagram=layered-architecture, node=logging-infra)

## LoggingServer

Type: arch (Architecture Element)  
Title: LoggingServer  
Source: docs/41-01-SSD-timing-application-specification-document.md:2136

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-LoggingRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:515 (diagram=layered-architecture, node=logging-server)

## Messaging

Type: arch (Architecture Element)  
Title: Messaging  
Source: docs/41-01-SSD-timing-application-specification-document.md:1762

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:390 (diagram=layered-architecture, node=messaging-io)

## MonotonicClock

Type: arch (Architecture Element)  
Title: MonotonicClock  
Source: docs/41-01-SSD-timing-application-specification-document.md:2043

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:447 (diagram=layered-architecture, node=platform-environment)

## NetworkDeviceService

Type: arch (Architecture Element)  
Title: NetworkDeviceService  
Source: docs/41-01-SSD-timing-application-specification-document.md:1886

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-IOComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:385 (diagram=layered-architecture, node=device-network-io)

## NextUpTeams

Type: arch (Architecture Element)  
Title: NextUpTeams  
Source: docs/41-01-SSD-timing-application-specification-document.md:1370

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:215 (diagram=layered-architecture, node=next-up-teams)

## NodeTaskProcessor

Type: arch (Architecture Element)  
Title: NodeTaskProcessor  
Source: docs/41-01-SSD-timing-application-specification-document.md:2409

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

_None._

## OperatingSystem

Type: arch (Architecture Element)  
Title: OperatingSystem  
Source: docs/41-01-SSD-timing-application-specification-document.md:2050

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:449 (diagram=layered-architecture, node=platform-environment)

## PlatformEnvironment

Type: arch (Architecture Element)  
Title: PlatformEnvironment  
Source: docs/41-01-SSD-timing-application-specification-document.md:2032

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:441 (diagram=layered-architecture, node=platform-environment)

## PlatformEvents

Type: arch (Architecture Element)  
Title: PlatformEvents  
Source: docs/41-01-SSD-timing-application-specification-document.md:2010

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:429 (diagram=layered-architecture, node=platform-events)

## PlatformExecution

Type: arch (Architecture Element)  
Title: PlatformExecution  
Source: docs/41-01-SSD-timing-application-specification-document.md:1960

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-CooperativeExecution**
- elaborates <- **DD-RuntimeExecution**
- elaborates <- **DD-RuntimeWorkAndMeasurements**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:411 (diagram=layered-architecture, node=platform-execution)

## PlatformTime

Type: arch (Architecture Element)  
Title: PlatformTime  
Source: docs/41-01-SSD-timing-application-specification-document.md:2057

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:454 (diagram=layered-architecture, node=platform-time)

## PowerDevice

Type: arch (Architecture Element)  
Title: PowerDevice  
Source: docs/41-01-SSD-timing-application-specification-document.md:1801

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:354 (diagram=layered-architecture, node=devices-io)

## PresentationGateway

Type: arch (Architecture Element)  
Title: PresentationGateway  
Source: docs/41-01-SSD-timing-application-specification-document.md:1215

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
Source: docs/41-01-SSD-timing-application-specification-document.md:978

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:483 (diagram=layered-architecture, node=presentation-runtime)

## RabbitMqConnector

Type: arch (Architecture Element)  
Title: RabbitMqConnector  
Source: docs/41-01-SSD-timing-application-specification-document.md:1920

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:403 (diagram=layered-architecture, node=messaging-io)

## RemoteShell

Type: arch (Architecture Element)  
Title: RemoteShell  
Source: docs/41-01-SSD-timing-application-specification-document.md:1152

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:116 (diagram=layered-architecture, node=remote-shell)

## Rev1CanDisplay

Type: arch (Architecture Element)  
Title: Rev1CanDisplay  
Source: docs/41-01-SSD-timing-application-specification-document.md:1844

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:362 (diagram=layered-architecture, node=devices-io)

## Rev1CanKeypad

Type: arch (Architecture Element)  
Title: Rev1CanKeypad  
Source: docs/41-01-SSD-timing-application-specification-document.md:1865

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:369 (diagram=layered-architecture, node=devices-io)

## Rev2WifiDisplay

Type: arch (Architecture Element)  
Title: Rev2WifiDisplay  
Source: docs/41-01-SSD-timing-application-specification-document.md:1851

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:364 (diagram=layered-architecture, node=devices-io)

## RuntimeExecutors

Type: arch (Architecture Element)  
Title: RuntimeExecutors  
Source: docs/41-01-SSD-timing-application-specification-document.md:987

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RuntimeExecution**
- elaborates <- **DD-RuntimeWorkAndMeasurements**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:491 (diagram=layered-architecture, node=runtime-executors)

## RuntimeTimeSources

Type: arch (Architecture Element)  
Title: RuntimeTimeSources  
Source: docs/41-01-SSD-timing-application-specification-document.md:993

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:499 (diagram=layered-architecture, node=runtime-time-sources)

## SI01-REQ-001

Type: req (Requirement)  
Title: Start from external configuration  
Source: docs/41-01-SSD-timing-application-specification-document.md:734

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
Source: docs/41-01-SSD-timing-application-specification-document.md:741

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-003

Type: req (Requirement)  
Title: Configured TimingNode availability  
Source: docs/41-01-SSD-timing-application-specification-document.md:749

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
Source: docs/41-01-SSD-timing-application-specification-document.md:762

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-011

Type: req (Requirement)  
Title: Consistent identity across interfaces  
Source: docs/41-01-SSD-timing-application-specification-document.md:770

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-020

Type: req (Requirement)  
Title: Current application status snapshot  
Source: docs/41-01-SSD-timing-application-specification-document.md:273

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
Source: docs/41-01-SSD-timing-application-specification-document.md:282

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
Source: docs/41-01-SSD-timing-application-specification-document.md:810

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
Source: docs/41-01-SSD-timing-application-specification-document.md:300

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
Source: docs/41-01-SSD-timing-application-specification-document.md:258

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
Source: docs/41-01-SSD-timing-application-specification-document.md:313

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
Source: docs/41-01-SSD-timing-application-specification-document.md:136

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
Source: docs/41-01-SSD-timing-application-specification-document.md:820

### Authored outgoing

_None._

### Generated incoming

- realizes <- **PresentationGateway**

### Diagram references

_None._

## SI01-REQ-031

Type: req (Requirement)  
Title: Externally testable executable  
Source: docs/41-01-SSD-timing-application-specification-document.md:669

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
Source: docs/41-01-SSD-timing-application-specification-document.md:829

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-033

Type: req (Requirement)  
Title: Compatible IF-03 evolution  
Source: docs/41-01-SSD-timing-application-specification-document.md:838

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-040

Type: req (Requirement)  
Title: Open registration point at a location  
Source: docs/41-01-SSD-timing-application-specification-document.md:83

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
Source: docs/41-01-SSD-timing-application-specification-document.md:151

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
Source: docs/41-01-SSD-timing-application-specification-document.md:177

### Authored outgoing

- specifies -> **UC-003**
- specifies -> **UC-009**
- specifies -> **UC-011**
- specifies -> **UC-021**

### Generated incoming

- depends_on <- **SI01-REQ-064**
- depends_on <- **SI01-REQ-071**
- depends_on <- **SI01-REQ-080**
- depends_on <- **SI01-REQ-081**
- depends_on <- **SI01-REQ-083**
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
Source: docs/41-01-SSD-timing-application-specification-document.md:656

### Authored outgoing

- specifies -> **UC-009**

### Generated incoming

- verifies <- **VC-ST1-002**

### Diagram references

_None._

## SI01-REQ-044

Type: req (Requirement)  
Title: Reconnect rebuild before live presentation  
Source: docs/41-01-SSD-timing-application-specification-document.md:326

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
Source: docs/41-01-SSD-timing-application-specification-document.md:782

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
Source: docs/41-01-SSD-timing-application-specification-document.md:794

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
Source: docs/41-01-SSD-timing-application-specification-document.md:606

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
Source: docs/41-01-SSD-timing-application-specification-document.md:622

### Authored outgoing

- specifies -> **UC-013**

### Generated incoming

- verifies <- **VC-ST1-004**

### Diagram references

_None._

## SI01-REQ-049

Type: req (Requirement)  
Title: Contain TimingNode recovery failure  
Source: docs/41-01-SSD-timing-application-specification-document.md:634

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
Source: docs/41-01-SSD-timing-application-specification-document.md:187

### Authored outgoing

- specifies -> **UC-003**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-051

Type: req (Requirement)  
Title: Keep local registration independent from presentation, logging and upstream delivery  
Source: docs/41-01-SSD-timing-application-specification-document.md:203

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
Source: docs/41-01-SSD-timing-application-specification-document.md:574

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
Source: docs/41-01-SSD-timing-application-specification-document.md:214

### Authored outgoing

- specifies -> **UC-003**

### Generated incoming

- realizes <- **SystemConductor**

### Diagram references

_None._

## SI01-REQ-054

Type: req (Requirement)  
Title: Multiplex mutually exclusive antenna inventory  
Source: docs/41-01-SSD-timing-application-specification-document.md:231

### Authored outgoing

- specifies -> **UC-003**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-055

Type: req (Requirement)  
Title: Allow antenna recovery without process restart  
Source: docs/41-01-SSD-timing-application-specification-document.md:588

### Authored outgoing

- specifies -> **UC-004**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-060

Type: req (Requirement)  
Title: Traceable ready-team registry  
Source: docs/41-01-SSD-timing-application-specification-document.md:339

### Authored outgoing

- specifies -> **UC-005**

### Generated incoming

- depends_on <- **SI01-REQ-061**

### Diagram references

_None._

## SI01-REQ-061

Type: req (Requirement)  
Title: Drive passive CAN display from current application state  
Source: docs/41-01-SSD-timing-application-specification-document.md:352

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
Source: docs/41-01-SSD-timing-application-specification-document.md:364

### Authored outgoing

- specifies -> **UC-007**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-063

Type: req (Requirement)  
Title: Apply TimingNode-scoped RaceData from the Central System  
Source: docs/41-01-SSD-timing-application-specification-document.md:378

### Authored outgoing

- depends_on -> **IF06-REQ-004**
- depends_on -> **IF06-REQ-005**
- specifies -> **UC-010**

### Generated incoming

- depends_on <- **SI01-REQ-077**
- depends_on <- **SI01-REQ-078**

### Diagram references

_None._

## SI01-REQ-064

Type: req (Requirement)  
Title: Transport-independent upstream synchronization  
Source: docs/41-01-SSD-timing-application-specification-document.md:391

### Authored outgoing

- depends_on -> **IF06-REQ-001**
- depends_on -> **IF06-REQ-002**
- depends_on -> **IF06-REQ-003**
- depends_on -> **IF06-REQ-010**
- depends_on -> **SI01-REQ-042**
- depends_on -> **SI01-REQ-045**
- specifies -> **UC-011**

### Generated incoming

- depends_on <- **SI01-REQ-065**
- depends_on <- **SI01-REQ-068**
- depends_on <- **SI01-REQ-069**
- depends_on <- **SI01-REQ-081**

### Diagram references

_None._

## SI01-REQ-065

Type: req (Requirement)  
Title: Preserve replayability across upstream outage  
Source: docs/41-01-SSD-timing-application-specification-document.md:403

### Authored outgoing

- depends_on -> **IF06-REQ-006**
- depends_on -> **IF06-REQ-007**
- depends_on -> **SI01-REQ-064**
- specifies -> **UC-011**
- specifies -> **UC-012**

### Generated incoming

- depends_on <- **SI01-REQ-069**
- depends_on <- **SI01-REQ-081**

### Diagram references

_None._

## SI01-REQ-066

Type: req (Requirement)  
Title: Simulate complete multi-node behaviour through normal application paths  
Source: docs/41-01-SSD-timing-application-specification-document.md:679

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
Source: docs/41-01-SSD-timing-application-specification-document.md:691

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
Title: Select alternative upstream transport for loop testing  
Source: docs/41-01-SSD-timing-application-specification-document.md:703

### Authored outgoing

- depends_on -> **SI01-REQ-064**
- specifies -> **UC-017**

### Generated incoming

- refines <- **IF03-REQ-025**
- refines <- **IF03-REQ-026**
- refines <- **IF03-REQ-027**

### Diagram references

_None._

## SI01-REQ-069

Type: req (Requirement)  
Title: Verify production-shaped RabbitMQ connector behaviour  
Source: docs/41-01-SSD-timing-application-specification-document.md:718

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
Source: docs/41-01-SSD-timing-application-specification-document.md:245

### Authored outgoing

- specifies -> **UC-019**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-071

Type: req (Requirement)  
Title: Operator manual registration  
Source: docs/41-01-SSD-timing-application-specification-document.md:163

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
Source: docs/41-01-SSD-timing-application-specification-document.md:94

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
Source: docs/41-01-SSD-timing-application-specification-document.md:124

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
Source: docs/41-01-SSD-timing-application-specification-document.md:110

### Authored outgoing

- depends_on -> **SI01-REQ-024**
- depends_on -> **SI01-REQ-049**
- depends_on -> **SI01-REQ-052**
- specifies -> **UC-001**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-075

Type: req (Requirement)  
Title: Maintain upstream PING request/answer lifecycle  
Source: docs/41-01-SSD-timing-application-specification-document.md:539

### Authored outgoing

- depends_on -> **IF06-REQ-011**
- depends_on -> **IF06-REQ-012**
- depends_on -> **IF06-REQ-013**

### Generated incoming

- verifies <- **VC-ST1-009**

### Diagram references

_None._

## SI01-REQ-076

Type: req (Requirement)  
Title: Answer inbound upstream PING  
Source: docs/41-01-SSD-timing-application-specification-document.md:557

### Authored outgoing

- depends_on -> **IF06-REQ-013**

### Generated incoming

- verifies <- **VC-ST1-009**

### Diagram references

_None._

## SI01-REQ-077

Type: req (Requirement)  
Title: Resolve TeamId without rewriting TimingData  
Source: docs/41-01-SSD-timing-application-specification-document.md:476

### Authored outgoing

- depends_on -> **IF06-REQ-015**
- depends_on -> **SI01-REQ-063**
- specifies -> **UC-010**

### Generated incoming

- depends_on <- **SI01-REQ-078**
- depends_on <- **SI01-REQ-080**

### Diagram references

_None._

## SI01-REQ-078

Type: req (Requirement)  
Title: Apply ordered incremental RaceData and acknowledge it  
Source: docs/41-01-SSD-timing-application-specification-document.md:491

### Authored outgoing

- depends_on -> **IF06-REQ-014**
- depends_on -> **IF06-REQ-015**
- depends_on -> **SI01-REQ-063**
- depends_on -> **SI01-REQ-077**
- specifies -> **UC-010**
- specifies -> **UC-012**

### Generated incoming

- depends_on <- **SI01-REQ-079**
- depends_on <- **SI01-REQ-084**
- depends_on <- **SI01-REQ-085**

### Diagram references

_None._

## SI01-REQ-079

Type: req (Requirement)  
Title: Apply RaceData stage-start-time changes  
Source: docs/41-01-SSD-timing-application-specification-document.md:507

### Authored outgoing

- depends_on -> **IF06-REQ-016**
- depends_on -> **SI01-REQ-078**
- specifies -> **UC-010**

### Generated incoming

- depends_on <- **SI01-REQ-080**

### Diagram references

_None._

## SI01-REQ-080

Type: req (Requirement)  
Title: Derive StageTiming from committed timing and current race state  
Source: docs/41-01-SSD-timing-application-specification-document.md:521

### Authored outgoing

- depends_on -> **SI01-REQ-042**
- depends_on -> **SI01-REQ-077**
- depends_on -> **SI01-REQ-079**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-081

Type: req (Requirement)  
Title: Advertise TimingData source head from the LogBook  
Source: docs/41-01-SSD-timing-application-specification-document.md:415

### Authored outgoing

- depends_on -> **IF06-REQ-017**
- depends_on -> **SI01-REQ-042**
- depends_on -> **SI01-REQ-064**
- depends_on -> **SI01-REQ-065**
- specifies -> **UC-011**
- specifies -> **UC-012**

### Generated incoming

- depends_on <- **SI01-REQ-082**
- depends_on <- **SI01-REQ-083**
- depends_on <- **SI01-REQ-084**
- depends_on <- **SI01-REQ-085**

### Diagram references

_None._

## SI01-REQ-082

Type: req (Requirement)  
Title: Serve TimingData requests from the retained LogBook  
Source: docs/41-01-SSD-timing-application-specification-document.md:427

### Authored outgoing

- depends_on -> **IF06-REQ-019**
- depends_on -> **IF06-REQ-020**
- depends_on -> **SI01-REQ-081**
- specifies -> **UC-011**
- specifies -> **UC-012**

### Generated incoming

- depends_on <- **SI01-REQ-085**

### Diagram references

_None._

## SI01-REQ-083

Type: req (Requirement)  
Title: Rebuild TimingData pending work without a second payload history  
Source: docs/41-01-SSD-timing-application-specification-document.md:439

### Authored outgoing

- depends_on -> **SI01-REQ-042**
- depends_on -> **SI01-REQ-081**
- specifies -> **UC-012**
- specifies -> **UC-013**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-084

Type: req (Requirement)  
Title: Expose diagnosable source synchronization state  
Source: docs/41-01-SSD-timing-application-specification-document.md:451

### Authored outgoing

- depends_on -> **IF06-REQ-017**
- depends_on -> **IF06-REQ-020**
- depends_on -> **SI01-REQ-078**
- depends_on -> **SI01-REQ-081**

### Generated incoming

- refines <- **IF03-REQ-027**

### Diagram references

_None._

## SI01-REQ-085

Type: req (Requirement)  
Title: Re-establish both ordered streams on connect and reconnect  
Source: docs/41-01-SSD-timing-application-specification-document.md:462

### Authored outgoing

- depends_on -> **IF06-REQ-021**
- depends_on -> **SI01-REQ-078**
- depends_on -> **SI01-REQ-081**
- depends_on -> **SI01-REQ-082**
- specifies -> **UC-011**
- specifies -> **UC-012**

### Generated incoming

- refines <- **IF03-REQ-027**

### Diagram references

_None._

## SI02-REQ-001

Type: req (Requirement)  
Title: Use only supported public SI-01 boundaries  
Source: docs/41-02-SSD-gui-application-specification-document.md:53

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
Source: docs/41-02-SSD-gui-application-specification-document.md:65

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
Source: docs/41-02-SSD-gui-application-specification-document.md:77

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
Source: docs/41-02-SSD-gui-application-specification-document.md:87

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
Source: docs/41-02-SSD-gui-application-specification-document.md:100

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
Source: docs/41-02-SSD-gui-application-specification-document.md:112

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
Source: docs/41-02-SSD-gui-application-specification-document.md:125

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
Source: docs/41-02-SSD-gui-application-specification-document.md:137

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

## SI02-REQ-009

Type: req (Requirement)  
Title: Display connected IF-03 engineering capabilities  
Source: docs/41-02-SSD-gui-application-specification-document.md:151

### Authored outgoing

- depends_on -> **IF03-REQ-012**
- specifies -> **UC-009**

### Generated incoming

_None._

### Diagram references

_None._

## SI02-REQ-010

Type: req (Requirement)  
Title: Support explicit client-side Lua engineering scripts  
Source: docs/41-02-SSD-gui-application-specification-document.md:165

### Authored outgoing

- depends_on -> **IF03-REQ-012**
- depends_on -> **IF03-REQ-024**
- specifies -> **UC-009**

### Generated incoming

_None._

### Diagram references

_None._

## ScheduledTaskRunner

Type: arch (Architecture Element)  
Title: ScheduledTaskRunner  
Source: docs/41-01-SSD-timing-application-specification-document.md:1994

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-CooperativeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:422 (diagram=layered-architecture, node=platform-execution)

## SerialLane

Type: arch (Architecture Element)  
Title: SerialLane  
Source: docs/41-01-SSD-timing-application-specification-document.md:1971

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RuntimeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:416 (diagram=layered-architecture, node=platform-execution)

## SerialScheduledLane

Type: arch (Architecture Element)  
Title: SerialScheduledLane  
Source: docs/41-01-SSD-timing-application-specification-document.md:1978

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RuntimeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:418 (diagram=layered-architecture, node=platform-execution)

## SerialTaskRunner

Type: arch (Architecture Element)  
Title: SerialTaskRunner  
Source: docs/41-01-SSD-timing-application-specification-document.md:1986

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-CooperativeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:420 (diagram=layered-architecture, node=platform-execution)

## Settings

Type: arch (Architecture Element)  
Title: Shared settings  
Source: docs/41-01-SSD-timing-application-specification-document.md:2107

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:544 (diagram=layered-architecture, node=settings-infra)

## SharedTerminalHandler

Type: arch (Architecture Element)  
Title: SharedTerminalHandler  
Source: docs/41-01-SSD-timing-application-specification-document.md:1160

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:148 (diagram=layered-architecture, node=shared-terminal)

## SimulatedAntenna

Type: arch (Architecture Element)  
Title: SimulatedAntenna  
Source: docs/41-01-SSD-timing-application-specification-document.md:1819

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:350 (diagram=layered-architecture, node=devices-io)

## SimulatedPowerDevice

Type: arch (Architecture Element)  
Title: SimulatedPowerDevice  
Source: docs/41-01-SSD-timing-application-specification-document.md:1811

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:357 (diagram=layered-architecture, node=devices-io)

## SimulationRuntime

Type: arch (Architecture Element)  
Title: SimulationRuntime  
Source: docs/41-01-SSD-timing-application-specification-document.md:969

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:475 (diagram=layered-architecture, node=simulation-runtime)

## StagePassageList

Type: arch (Architecture Element)  
Title: StagePassageList  
Source: docs/41-01-SSD-timing-application-specification-document.md:1477

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:259 (diagram=layered-architecture, node=node-timing)

## StageRanking

Type: arch (Architecture Element)  
Title: StageRanking  
Source: docs/41-01-SSD-timing-application-specification-document.md:1493

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:261 (diagram=layered-architecture, node=node-timing)

## StageStartTimes

Type: arch (Architecture Element)  
Title: StageStartTimes  
Source: docs/41-01-SSD-timing-application-specification-document.md:1432

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:245 (diagram=layered-architecture, node=node-racedata)

## Storage

Type: arch (Architecture Element)  
Title: Storage  
Source: docs/41-01-SSD-timing-application-specification-document.md:1727

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:326 (diagram=layered-architecture, node=storage-io)

## SystemConductor

Type: arch (Architecture Element)  
Title: TimingSystem Conductor  
Source: docs/41-01-SSD-timing-application-specification-document.md:1301

### Authored outgoing

- realizes -> **SI01-REQ-053**

### Generated incoming

- elaborates <- **DD-CooperativeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:192 (diagram=layered-architecture, node=system-conductor)

## SystemStatus

Type: arch (Architecture Element)  
Title: SystemStatus  
Source: docs/41-01-SSD-timing-application-specification-document.md:2160

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:201 (diagram=layered-architecture, node=system-status-domain)

## TagProcessor

Type: arch (Architecture Element)  
Title: TagProcessor  
Source: docs/41-01-SSD-timing-application-specification-document.md:1420

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-EventTagProcessing**
- elaborates <- **DD-RuntimeWorkAndMeasurements**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:229 (diagram=layered-architecture, node=node-processing)

## TeamAssignments

Type: arch (Architecture Element)  
Title: TeamAssignments  
Source: docs/41-01-SSD-timing-application-specification-document.md:1443

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:243 (diagram=layered-architecture, node=node-racedata)

## TimeSource

Type: arch (Architecture Element)  
Title: TimeSource  
Source: docs/41-01-SSD-timing-application-specification-document.md:2065

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:459 (diagram=layered-architecture, node=platform-time)

## TimingApplicationRuntime

Type: arch (Architecture Element)  
Title: TimingApplicationRuntime  
Source: docs/41-01-SSD-timing-application-specification-document.md:959

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:467 (diagram=layered-architecture, node=timing-application-runtime)

## TimingData

Type: arch (Architecture Element)  
Title: TimingData  
Source: docs/41-01-SSD-timing-application-specification-document.md:2191

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExtensionAndComposition**
- elaborates <- **DD-TimingDataProfiles**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:307 (diagram=layered-architecture, node=timing-data-domain)

## TimingNode

Type: arch (Architecture Element)  
Title: TimingNode  
Source: docs/41-01-SSD-timing-application-specification-document.md:2171

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

## TimingNodeData

Type: arch (Architecture Element)  
Title: TimingNode Data  
Source: docs/41-01-SSD-timing-application-specification-document.md:1400

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:269 (diagram=layered-architecture, node=node-data)

## TimingNodeProcessing

Type: arch (Architecture Element)  
Title: TimingNode Processing  
Source: docs/41-01-SSD-timing-application-specification-document.md:1383

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:224 (diagram=layered-architecture, node=node-processing)

## TimingNodeProxy

Type: arch (Architecture Element)  
Title: TimingNodeProxy  
Source: docs/41-01-SSD-timing-application-specification-document.md:1236

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-PresentationAccess**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:176 (diagram=layered-architecture, node=timing-node-proxy)

## TimingNodeRaceData

Type: arch (Architecture Element)  
Title: TimingNode RaceData  
Source: docs/41-01-SSD-timing-application-specification-document.md:1392

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:238 (diagram=layered-architecture, node=node-racedata)

## TimingNodeTiming

Type: arch (Architecture Element)  
Title: TimingNode Timing  
Source: docs/41-01-SSD-timing-application-specification-document.md:1409

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:252 (diagram=layered-architecture, node=node-timing)

## TimingNodeUpstreamHandler

Type: arch (Architecture Element)  
Title: TimingNode UpstreamHandler  
Source: docs/41-01-SSD-timing-application-specification-document.md:1351

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:283 (diagram=layered-architecture, node=upstream-message-port)

## TimingSystem

Type: arch (Architecture Element)  
Title: TimingSystem  
Source: docs/41-01-SSD-timing-application-specification-document.md:2149

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
- specifies <- **SI02-REQ-009**
- specifies <- **SI02-REQ-010**

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
- specifies <- **SI01-REQ-077**
- specifies <- **SI01-REQ-078**
- specifies <- **SI01-REQ-079**

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
- specifies <- **SI01-REQ-081**
- specifies <- **SI01-REQ-082**
- specifies <- **SI01-REQ-085**

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
- specifies <- **SI01-REQ-078**
- specifies <- **SI01-REQ-081**
- specifies <- **SI01-REQ-082**
- specifies <- **SI01-REQ-083**
- specifies <- **SI01-REQ-085**

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
- specifies <- **SI01-REQ-083**

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

- specifies <- **IF03-REQ-025**
- specifies <- **IF03-REQ-026**
- specifies <- **IF03-REQ-027**
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

## UniqueTeamRegistrations

Type: arch (Architecture Element)  
Title: UniqueTeamRegistrations  
Source: docs/41-01-SSD-timing-application-specification-document.md:1453

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:257 (diagram=layered-architecture, node=node-timing)

## UpstreamData

Type: arch (Architecture Element)  
Title: UpstreamData  
Source: docs/41-01-SSD-timing-application-specification-document.md:2201

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:316 (diagram=layered-architecture, node=upstream-data-domain)

## UpstreamGateway

Type: arch (Architecture Element)  
Title: UpstreamGateway  
Source: docs/41-01-SSD-timing-application-specification-document.md:1894

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:395 (diagram=layered-architecture, node=messaging-io)

## UpstreamStream

Type: arch (Architecture Element)  
Title: UpstreamStream  
Source: docs/41-01-SSD-timing-application-specification-document.md:1902

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:398 (diagram=layered-architecture, node=messaging-io)

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

## VC-ST1-009

Type: vc (Verification Case)  
Title: Verify upstream PING request/answer lifecycle  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:507

### Authored outgoing

- verifies -> **IF06-REQ-011**
- verifies -> **IF06-REQ-012**
- verifies -> **IF06-REQ-013**
- verifies -> **SI01-REQ-075**
- verifies -> **SI01-REQ-076**

### Generated incoming

_None._

### Diagram references

_None._

## VC-ST1-010

Type: vc (Verification Case)  
Title: Verify default UpstreamData envelope and embedded TimingData  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:566

### Authored outgoing

- verifies -> **IF06-REQ-001**
- verifies -> **IF06-REQ-002**
- verifies -> **IF06-REQ-003**
- verifies -> **IF06-REQ-008**
- verifies -> **IF06-REQ-010**

### Generated incoming

_None._

### Diagram references

_None._

## VendorAntenna

Type: arch (Architecture Element)  
Title: VendorAntenna  
Source: docs/41-01-SSD-timing-application-specification-document.md:1826

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:352 (diagram=layered-architecture, node=devices-io)

## Web

Type: arch (Architecture Element)  
Title: Web  
Source: docs/41-01-SSD-timing-application-specification-document.md:1128

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:126 (diagram=layered-architecture, node=web-interface)
