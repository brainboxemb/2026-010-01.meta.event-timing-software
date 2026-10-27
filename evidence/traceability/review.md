# Engineering graph review

Source revision: 0e53a7155a2e2e3b9dcac4822abf070daf72748e
Source graph: sphinx-needs Event timing engineering graph migration-013

Engineering objects and outgoing relations come from the Sphinx-Needs export.
Incoming relations below are derived from those outgoing relations.
Diagram identities are references to existing engineering objects.

## Overview

| Object | Type | Authored outgoing | Generated incoming | Diagram refs |
| --- | --- | ---: | ---: | ---: |
| [AbstractTask](#abstracttask) | arch | 0 | 1 | 1 |
| [ActiveRegistrations](#activeregistrations) | arch | 0 | 0 | 1 |
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
| [DD-AntennaRuntime](#dd-antennaruntime) | design | 5 | 0 | 0 |
| [DD-CooperativeExecution](#dd-cooperativeexecution) | design | 6 | 0 | 0 |
| [DD-DependencyPlacement](#dd-dependencyplacement) | design | 0 | 0 | 0 |
| [DD-DomainIntegration](#dd-domainintegration) | design | 5 | 0 | 0 |
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
| [IF03-REQ-017](#if03-req-017) | ifreq | 1 | 2 | 0 |
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
| [IF03-REQ-028](#if03-req-028) | ifreq | 1 | 0 | 0 |
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
| [IF06-REQ-004](#if06-req-004) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-005](#if06-req-005) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-006](#if06-req-006) | ifreq | 0 | 1 | 0 |
| [IF06-REQ-007](#if06-req-007) | ifreq | 0 | 1 | 0 |
| [IF06-REQ-008](#if06-req-008) | ifreq | 0 | 1 | 0 |
| [IF06-REQ-009](#if06-req-009) | ifreq | 0 | 0 | 0 |
| [IF06-REQ-010](#if06-req-010) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-011](#if06-req-011) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-012](#if06-req-012) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-013](#if06-req-013) | ifreq | 0 | 3 | 0 |
| [IF06-REQ-014](#if06-req-014) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-015](#if06-req-015) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-016](#if06-req-016) | ifreq | 0 | 1 | 0 |
| [IF06-REQ-017](#if06-req-017) | ifreq | 0 | 3 | 0 |
| [IF06-REQ-018](#if06-req-018) | ifreq | 0 | 3 | 0 |
| [IF06-REQ-019](#if06-req-019) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-020](#if06-req-020) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-021](#if06-req-021) | ifreq | 0 | 2 | 0 |
| [IF06-REQ-022](#if06-req-022) | ifreq | 0 | 0 | 0 |
| [Keypad](#keypad) | arch | 0 | 0 | 1 |
| [LogBook](#logbook) | arch | 0 | 1 | 1 |
| [Logging](#logging) | arch | 0 | 1 | 1 |
| [LoggingServer](#loggingserver) | arch | 0 | 1 | 1 |
| [Messaging](#messaging) | arch | 0 | 0 | 1 |
| [MonotonicClock](#monotonicclock) | arch | 0 | 0 | 1 |
| [NetworkDeviceService](#networkdeviceservice) | arch | 0 | 1 | 1 |
| [NextUpTeams](#nextupteams) | arch | 0 | 0 | 1 |
| [NodeUpstream](#nodeupstream) | arch | 0 | 0 | 1 |
| [OperatingSystem](#operatingsystem) | arch | 0 | 0 | 1 |
| [PlatformEnvironment](#platformenvironment) | arch | 0 | 1 | 1 |
| [PlatformEvents](#platformevents) | arch | 0 | 1 | 1 |
| [PlatformExecution](#platformexecution) | arch | 0 | 3 | 1 |
| [PlatformTime](#platformtime) | arch | 0 | 1 | 1 |
| [PowerDevice](#powerdevice) | arch | 0 | 1 | 1 |
| [PresentationGateway](#presentationgateway) | arch | 5 | 1 | 1 |
| [PresentationRuntime](#presentationruntime) | arch | 0 | 1 | 1 |
| [RabbitMqConnector](#rabbitmqconnector) | arch | 0 | 0 | 1 |
| [RegisteredTeams](#registeredteams) | arch | 0 | 0 | 1 |
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
| [SI01-REQ-021](#si01-req-021) | req | 2 | 2 | 0 |
| [SI01-REQ-022](#si01-req-022) | req | 3 | 1 | 0 |
| [SI01-REQ-023](#si01-req-023) | req | 4 | 3 | 0 |
| [SI01-REQ-024](#si01-req-024) | req | 3 | 13 | 0 |
| [SI01-REQ-025](#si01-req-025) | req | 5 | 4 | 0 |
| [SI01-REQ-026](#si01-req-026) | req | 5 | 4 | 0 |
| [SI01-REQ-030](#si01-req-030) | req | 0 | 1 | 0 |
| [SI01-REQ-031](#si01-req-031) | req | 2 | 5 | 0 |
| [SI01-REQ-032](#si01-req-032) | req | 0 | 0 | 0 |
| [SI01-REQ-033](#si01-req-033) | req | 0 | 0 | 0 |
| [SI01-REQ-040](#si01-req-040) | req | 2 | 7 | 0 |
| [SI01-REQ-041](#si01-req-041) | req | 3 | 5 | 0 |
| [SI01-REQ-042](#si01-req-042) | req | 4 | 12 | 0 |
| [SI01-REQ-043](#si01-req-043) | req | 1 | 1 | 0 |
| [SI01-REQ-044](#si01-req-044) | req | 1 | 2 | 0 |
| [SI01-REQ-045](#si01-req-045) | req | 8 | 2 | 0 |
| [SI01-REQ-046](#si01-req-046) | req | 3 | 6 | 0 |
| [SI01-REQ-047](#si01-req-047) | req | 4 | 4 | 0 |
| [SI01-REQ-048](#si01-req-048) | req | 1 | 2 | 0 |
| [SI01-REQ-049](#si01-req-049) | req | 1 | 1 | 0 |
| [SI01-REQ-050](#si01-req-050) | req | 1 | 0 | 0 |
| [SI01-REQ-051](#si01-req-051) | req | 2 | 0 | 0 |
| [SI01-REQ-052](#si01-req-052) | req | 2 | 1 | 0 |
| [SI01-REQ-053](#si01-req-053) | req | 1 | 1 | 0 |
| [SI01-REQ-054](#si01-req-054) | req | 1 | 0 | 0 |
| [SI01-REQ-055](#si01-req-055) | req | 1 | 0 | 0 |
| [SI01-REQ-060](#si01-req-060) | req | 1 | 1 | 0 |
| [SI01-REQ-061](#si01-req-061) | req | 2 | 0 | 0 |
| [SI01-REQ-062](#si01-req-062) | req | 1 | 0 | 0 |
| [SI01-REQ-063](#si01-req-063) | req | 3 | 3 | 0 |
| [SI01-REQ-064](#si01-req-064) | req | 7 | 4 | 0 |
| [SI01-REQ-065](#si01-req-065) | req | 5 | 2 | 0 |
| [SI01-REQ-066](#si01-req-066) | req | 4 | 0 | 0 |
| [SI01-REQ-067](#si01-req-067) | req | 3 | 0 | 0 |
| [SI01-REQ-068](#si01-req-068) | req | 2 | 4 | 0 |
| [SI01-REQ-069](#si01-req-069) | req | 3 | 0 | 0 |
| [SI01-REQ-070](#si01-req-070) | req | 1 | 0 | 0 |
| [SI01-REQ-071](#si01-req-071) | req | 3 | 2 | 0 |
| [SI01-REQ-072](#si01-req-072) | req | 3 | 4 | 0 |
| [SI01-REQ-073](#si01-req-073) | req | 3 | 0 | 0 |
| [SI01-REQ-074](#si01-req-074) | req | 3 | 0 | 0 |
| [SI01-REQ-075](#si01-req-075) | req | 3 | 1 | 0 |
| [SI01-REQ-076](#si01-req-076) | req | 1 | 1 | 0 |
| [SI01-REQ-077](#si01-req-077) | req | 3 | 2 | 0 |
| [SI01-REQ-078](#si01-req-078) | req | 6 | 4 | 0 |
| [SI01-REQ-079](#si01-req-079) | req | 3 | 1 | 0 |
| [SI01-REQ-080](#si01-req-080) | req | 3 | 0 | 0 |
| [SI01-REQ-081](#si01-req-081) | req | 6 | 5 | 0 |
| [SI01-REQ-082](#si01-req-082) | req | 5 | 2 | 0 |
| [SI01-REQ-083](#si01-req-083) | req | 4 | 1 | 0 |
| [SI01-REQ-084](#si01-req-084) | req | 4 | 3 | 0 |
| [SI01-REQ-085](#si01-req-085) | req | 6 | 2 | 0 |
| [SI01-REQ-086](#si01-req-086) | req | 7 | 0 | 0 |
| [SI01-REQ-087](#si01-req-087) | req | 7 | 0 | 0 |
| [SI01-REQ-088](#si01-req-088) | req | 4 | 0 | 0 |
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
| [SI02-REQ-011](#si02-req-011) | req | 1 | 0 | 0 |
| [SerialLane](#seriallane) | arch | 0 | 1 | 1 |
| [SerialTaskRunner](#serialtaskrunner) | arch | 0 | 2 | 1 |
| [SharedTerminalHandler](#sharedterminalhandler) | arch | 0 | 1 | 1 |
| [SimulatedAntenna](#simulatedantenna) | arch | 0 | 1 | 1 |
| [SimulatedPowerDevice](#simulatedpowerdevice) | arch | 0 | 1 | 1 |
| [SimulationRuntime](#simulationruntime) | arch | 0 | 0 | 1 |
| [StageStartTimes](#stagestarttimes) | arch | 0 | 0 | 1 |
| [Storage](#storage) | arch | 0 | 0 | 1 |
| [TagProcessor](#tagprocessor) | arch | 0 | 2 | 1 |
| [TaskStep](#taskstep) | arch | 0 | 1 | 0 |
| [TeamAssignments](#teamassignments) | arch | 0 | 0 | 1 |
| [TimeSource](#timesource) | arch | 0 | 1 | 1 |
| [TimingApplicationRuntime](#timingapplicationruntime) | arch | 0 | 1 | 1 |
| [TimingData](#timingdata) | arch | 0 | 2 | 1 |
| [TimingNode](#timingnode) | arch | 4 | 2 | 1 |
| [TimingNodeData](#timingnodedata) | arch | 0 | 0 | 1 |
| [TimingNodeDataLane](#timingnodedatalane) | arch | 0 | 0 | 0 |
| [TimingNodeProcessing](#timingnodeprocessing) | arch | 0 | 0 | 1 |
| [TimingNodeProxy](#timingnodeproxy) | arch | 0 | 1 | 1 |
| [TimingNodeRaceData](#timingnoderacedata) | arch | 0 | 0 | 1 |
| [TimingNodeRegistration](#timingnoderegistration) | arch | 0 | 0 | 1 |
| [TimingNodeTaskLane](#timingnodetasklane) | arch | 0 | 0 | 0 |
| [TimingSystem](#timingsystem) | arch | 0 | 2 | 1 |
| [TimingSystemConductor](#timingsystemconductor) | arch | 1 | 1 | 1 |
| [TimingSystemUpstream](#timingsystemupstream) | arch | 0 | 1 | 1 |
| [UC-001](#uc-001) | uc | 0 | 9 | 0 |
| [UC-002](#uc-002) | uc | 0 | 9 | 0 |
| [UC-003](#uc-003) | uc | 0 | 8 | 0 |
| [UC-004](#uc-004) | uc | 0 | 2 | 0 |
| [UC-005](#uc-005) | uc | 0 | 1 | 0 |
| [UC-006](#uc-006) | uc | 0 | 1 | 0 |
| [UC-007](#uc-007) | uc | 0 | 1 | 0 |
| [UC-009](#uc-009) | uc | 0 | 28 | 0 |
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
| [UC-020](#uc-020) | uc | 0 | 2 | 0 |
| [UC-021](#uc-021) | uc | 0 | 5 | 0 |
| [UC-022](#uc-022) | uc | 0 | 4 | 0 |
| [UC-023](#uc-023) | uc | 0 | 1 | 0 |
| [UC-024](#uc-024) | uc | 0 | 2 | 0 |
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
| [VC-ST1-010](#vc-st1-010) | vc | 6 | 0 | 0 |
| [VC-ST1-011](#vc-st1-011) | vc | 7 | 0 | 0 |
| [VC-ST1-012](#vc-st1-012) | vc | 9 | 0 | 0 |
| [VendorAntenna](#vendorantenna) | arch | 0 | 0 | 1 |
| [Web](#web) | arch | 0 | 0 | 1 |
| [YieldingTask](#yieldingtask) | arch | 0 | 1 | 0 |

## AbstractTask

Type: arch (Architecture Element)  
Title: AbstractTask  
Source: docs/41-01-SSD-timing-application-specification-document.md:2032

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-CooperativeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:410 (diagram=layered-architecture, node=platform-execution)

## ActiveRegistrations

Type: arch (Architecture Element)  
Title: ActiveRegistrations  
Source: docs/41-01-SSD-timing-application-specification-document.md:1569

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:248 (diagram=layered-architecture, node=node-registration)

## Antenna

Type: arch (Architecture Element)  
Title: Antenna  
Source: docs/41-01-SSD-timing-application-specification-document.md:1836

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:336 (diagram=layered-architecture, node=devices-io)

## AntennaManager

Type: arch (Architecture Element)  
Title: AntennaManager  
Source: docs/41-01-SSD-timing-application-specification-document.md:1828

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:333 (diagram=layered-architecture, node=devices-io)

## Api

Type: arch (Architecture Element)  
Title: API  
Source: docs/41-01-SSD-timing-application-specification-document.md:1210

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
Source: docs/41-01-SSD-timing-application-specification-document.md:1295

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:159 (diagram=layered-architecture, node=application-conductor)

## ApplicationConfiguration

Type: arch (Architecture Element)  
Title: Application configuration  
Source: docs/41-01-SSD-timing-application-specification-document.md:2118

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RunningConfiguration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:493 (diagram=layered-architecture, node=application-configuration-runtime)

## Beeper

Type: arch (Architecture Element)  
Title: Beeper  
Source: docs/41-01-SSD-timing-application-specification-document.md:1915

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:360 (diagram=layered-architecture, node=devices-io)

## CanNetworkController

Type: arch (Architecture Element)  
Title: CanNetworkController  
Source: docs/41-01-SSD-timing-application-specification-document.md:1922

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-IOComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:372 (diagram=layered-architecture, node=device-network-io)

## ClockTimeSource

Type: arch (Architecture Element)  
Title: ClockTimeSource  
Source: docs/41-01-SSD-timing-application-specification-document.md:2104

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:447 (diagram=layered-architecture, node=platform-time)

## Configuration

Type: arch (Architecture Element)  
Title: Typed configuration values  
Source: docs/41-01-SSD-timing-application-specification-document.md:2127

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RunningConfiguration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:522 (diagram=layered-architecture, node=configuration-infra)

## ConfigurationControl

Type: arch (Architecture Element)  
Title: Configuration control  
Source: docs/41-01-SSD-timing-application-specification-document.md:1306

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RunningConfiguration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:184 (diagram=layered-architecture, node=configuration-control)

## Connector

Type: arch (Architecture Element)  
Title: Connector  
Source: docs/41-01-SSD-timing-application-specification-document.md:1955

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:389 (diagram=layered-architecture, node=messaging-io)

## Console

Type: arch (Architecture Element)  
Title: Console  
Source: docs/41-01-SSD-timing-application-specification-document.md:1242

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:106 (diagram=layered-architecture, node=local-console)

## DD-AntennaRuntime

Type: design (Detailed Design)  
Title: Antenna runtime and device control  
Source: docs/43-01-SDD-02-java-component-design.md:1895

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
Source: docs/43-01-SDD-02-java-component-design.md:535

### Authored outgoing

- elaborates -> **AbstractTask**
- elaborates -> **PlatformExecution**
- elaborates -> **SerialTaskRunner**
- elaborates -> **TaskStep**
- elaborates -> **TimingSystemConductor**
- elaborates -> **YieldingTask**

### Generated incoming

_None._

### Diagram references

_None._

## DD-DependencyPlacement

Type: design (Detailed Design)  
Title: Contract and internal dependency placement  
Source: docs/43-01-SDD-02-java-component-design.md:1094

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## DD-DomainIntegration

Type: design (Detailed Design)  
Title: Domain data and upstream composition  
Source: docs/43-01-SDD-02-java-component-design.md:1048

### Authored outgoing

- elaborates -> **TimingSystem**
- elaborates -> **TimingSystemUpstream**
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
Source: docs/43-01-SDD-02-java-component-design.md:677

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
Source: docs/43-01-SDD-02-java-component-design.md:1336

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
Source: docs/43-01-SDD-02-java-component-design.md:3580

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
Source: docs/43-01-SDD-02-java-component-design.md:1020

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
Source: docs/43-01-SDD-02-java-component-design.md:1216

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
Source: docs/43-01-SDD-02-java-component-design.md:861

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
Source: docs/43-01-SDD-02-java-component-design.md:1642

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
Source: docs/43-01-SDD-02-java-component-design.md:2835

### Authored outgoing

- elaborates -> **PlatformExecution**
- elaborates -> **RuntimeExecutors**
- elaborates -> **SerialLane**
- elaborates -> **SerialTaskRunner**

### Generated incoming

_None._

### Diagram references

_None._

## DD-RuntimeWorkAndMeasurements

Type: design (Detailed Design)  
Title: Registration workload and runtime measurement  
Source: docs/43-01-SDD-02-java-component-design.md:2646

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
Source: docs/43-01-SDD-02-java-component-design.md:3372

### Authored outgoing

- elaborates -> **TimingData**

### Generated incoming

_None._

### Diagram references

_None._

## DD-TimingNodeExecution

Type: design (Detailed Design)  
Title: TimingNode execution, LogBook and local events  
Source: docs/43-01-SDD-02-java-component-design.md:2947

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
Source: docs/43-01-SDD-02-java-component-design.md:997

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
Source: docs/41-01-SSD-timing-application-specification-document.md:1791

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:367 (diagram=layered-architecture, node=device-network-io)

## Devices

Type: arch (Architecture Element)  
Title: Devices  
Source: docs/41-01-SSD-timing-application-specification-document.md:1776

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:328 (diagram=layered-architecture, node=devices-io)

## Display

Type: arch (Architecture Element)  
Title: Display  
Source: docs/41-01-SSD-timing-application-specification-document.md:1879

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:348 (diagram=layered-architecture, node=devices-io)

## EngineeringApiConnector

Type: arch (Architecture Element)  
Title: EngineeringApiConnector  
Source: docs/41-01-SSD-timing-application-specification-document.md:1970

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:394 (diagram=layered-architecture, node=messaging-io)

## Event

Type: arch (Architecture Element)  
Title: Event  
Source: docs/41-01-SSD-timing-application-specification-document.md:2047

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:420 (diagram=layered-architecture, node=platform-events)

## EventData

Type: arch (Architecture Element)  
Title: EventData  
Source: docs/41-01-SSD-timing-application-specification-document.md:1582

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
Source: docs/41-01-SSD-timing-application-specification-document.md:2054

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:422 (diagram=layered-architecture, node=platform-events)

## IF03-REQ-001

Type: ifreq (Interface Requirement)  
Title: Shared application semantics  
Source: docs/32-03-ISD-application-control-status.md:449

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
Source: docs/32-03-ISD-application-control-status.md:458

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
Source: docs/32-03-ISD-application-control-status.md:467

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
Source: docs/32-03-ISD-application-control-status.md:475

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
Source: docs/32-03-ISD-application-control-status.md:483

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
Source: docs/32-03-ISD-application-control-status.md:491

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
Source: docs/32-03-ISD-application-control-status.md:500

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI02-REQ-001**

### Diagram references

_None._

## IF03-REQ-008

Type: ifreq (Interface Requirement)  
Title: Explicit failure outcome  
Source: docs/32-03-ISD-application-control-status.md:509

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
Source: docs/32-03-ISD-application-control-status.md:518

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI02-REQ-002**

### Diagram references

_None._

## IF03-REQ-010

Type: ifreq (Interface Requirement)  
Title: Compatible extension  
Source: docs/32-03-ISD-application-control-status.md:527

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-011

Type: ifreq (Interface Requirement)  
Title: TimingNode location and lifecycle control  
Source: docs/32-03-ISD-application-control-status.md:536

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
Source: docs/32-03-ISD-application-control-status.md:547

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
Source: docs/32-03-ISD-application-control-status.md:556

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
Source: docs/32-03-ISD-application-control-status.md:570

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
Source: docs/32-03-ISD-application-control-status.md:579

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
Source: docs/32-03-ISD-application-control-status.md:588

### Authored outgoing

- refines -> **SI01-REQ-044**

### Generated incoming

- depends_on <- **SI02-REQ-006**
- verifies <- **VC-ST1-003**

### Diagram references

_None._

## IF03-REQ-017

Type: ifreq (Interface Requirement)  
Title: TimingNode current functional state  
Source: docs/32-03-ISD-application-control-status.md:735

### Authored outgoing

- refines -> **SI01-REQ-024**

### Generated incoming

- depends_on <- **SI02-REQ-004**
- verifies <- **VC-ST1-004**

### Diagram references

_None._

## IF03-REQ-018

Type: ifreq (Interface Requirement)  
Title: Runtime configuration query  
Source: docs/32-03-ISD-application-control-status.md:612

### Authored outgoing

- depends_on -> **SI01-REQ-001**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-019

Type: ifreq (Interface Requirement)  
Title: Runtime configuration override  
Source: docs/32-03-ISD-application-control-status.md:622

### Authored outgoing

- depends_on -> **SI01-REQ-001**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-020

Type: ifreq (Interface Requirement)  
Title: Runtime configuration change notification  
Source: docs/32-03-ISD-application-control-status.md:633

### Authored outgoing

- depends_on -> **SI01-REQ-001**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-021

Type: ifreq (Interface Requirement)  
Title: Bounded live-event delivery  
Source: docs/32-03-ISD-application-control-status.md:599

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI02-REQ-005**

### Diagram references

_None._

## IF03-REQ-022

Type: ifreq (Interface Requirement)  
Title: Registration revoke  
Source: docs/32-03-ISD-application-control-status.md:644

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
Source: docs/32-03-ISD-application-control-status.md:656

### Authored outgoing

- refines -> **SI01-REQ-071**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-024

Type: ifreq (Interface Requirement)  
Title: Simulated tag passage control  
Source: docs/32-03-ISD-application-control-status.md:722

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI02-REQ-010**

### Diagram references

_None._

## IF03-REQ-025

Type: ifreq (Interface Requirement)  
Title: Engineering backoffice UpstreamData ingress  
Source: docs/32-03-ISD-application-control-status.md:668

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
Source: docs/32-03-ISD-application-control-status.md:680

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
Source: docs/32-03-ISD-application-control-status.md:696

### Authored outgoing

- refines -> **SI01-REQ-068**
- refines -> **SI01-REQ-084**
- refines -> **SI01-REQ-085**
- specifies -> **UC-017**

### Generated incoming

_None._

### Diagram references

_None._

## IF03-REQ-028

Type: ifreq (Interface Requirement)  
Title: Applied StageStartTimes query  
Source: docs/32-03-ISD-application-control-status.md:710

### Authored outgoing

- refines -> **SI01-REQ-068**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-001

Type: ifreq (Interface Requirement)  
Title: Per-TimingNode Web binding  
Source: docs/32-04-ISD-web-interface.md:233

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-002

Type: ifreq (Interface Requirement)  
Title: Current TimingNode state  
Source: docs/32-04-ISD-web-interface.md:243

### Authored outgoing

- refines -> **SI01-REQ-024**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-003

Type: ifreq (Interface Requirement)  
Title: Open with LocationId  
Source: docs/32-04-ISD-web-interface.md:252

### Authored outgoing

- refines -> **SI01-REQ-040**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-004

Type: ifreq (Interface Requirement)  
Title: Close operation  
Source: docs/32-04-ISD-web-interface.md:261

### Authored outgoing

- refines -> **SI01-REQ-072**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-005

Type: ifreq (Interface Requirement)  
Title: Shared TimingNode semantics  
Source: docs/32-04-ISD-web-interface.md:269

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
Source: docs/32-04-ISD-web-interface.md:278

### Authored outgoing

- refines -> **SI01-REQ-026**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-007

Type: ifreq (Interface Requirement)  
Title: Compatible Web realizations  
Source: docs/32-04-ISD-web-interface.md:288

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-008

Type: ifreq (Interface Requirement)  
Title: Current-state baseline after connect or reconnect  
Source: docs/32-04-ISD-web-interface.md:298

### Authored outgoing

- refines -> **SI01-REQ-025**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-009

Type: ifreq (Interface Requirement)  
Title: Live-state delivery and loss handling  
Source: docs/32-04-ISD-web-interface.md:308

### Authored outgoing

- refines -> **SI01-REQ-023**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-010

Type: ifreq (Interface Requirement)  
Title: Manual registration through Web interface  
Source: docs/32-04-ISD-web-interface.md:319

### Authored outgoing

- refines -> **SI01-REQ-071**

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-011

Type: ifreq (Interface Requirement)  
Title: Local-network browser access  
Source: docs/32-04-ISD-web-interface.md:329

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## IF04-REQ-012

Type: ifreq (Interface Requirement)  
Title: Query committed registration history  
Source: docs/32-04-ISD-web-interface.md:339

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
Source: docs/32-06-ISD-backend-integration.md:472

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
Source: docs/32-06-ISD-backend-integration.md:480

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
Source: docs/32-06-ISD-backend-integration.md:489

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
Source: docs/32-06-ISD-backend-integration.md:497

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-063**
- verifies <- **VC-ST1-011**

### Diagram references

_None._

## IF06-REQ-005

Type: ifreq (Interface Requirement)  
Title: Explicit reference-data outcome  
Source: docs/32-06-ISD-backend-integration.md:507

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-063**
- verifies <- **VC-ST1-011**

### Diagram references

_None._

## IF06-REQ-006

Type: ifreq (Interface Requirement)  
Title: Synchronization preserves source identity  
Source: docs/32-06-ISD-backend-integration.md:517

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-065**

### Diagram references

_None._

## IF06-REQ-007

Type: ifreq (Interface Requirement)  
Title: Local TimingData commit independent from backend delivery  
Source: docs/32-06-ISD-backend-integration.md:526

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-065**

### Diagram references

_None._

## IF06-REQ-008

Type: ifreq (Interface Requirement)  
Title: Public default JSON representation  
Source: docs/32-06-ISD-backend-integration.md:535

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-010**

### Diagram references

_None._

## IF06-REQ-009

Type: ifreq (Interface Requirement)  
Title: Alternative representation support  
Source: docs/32-06-ISD-backend-integration.md:546

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## IF06-REQ-010

Type: ifreq (Interface Requirement)  
Title: Connector transport independence  
Source: docs/32-06-ISD-backend-integration.md:555

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
Source: docs/32-06-ISD-backend-integration.md:687

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
Source: docs/32-06-ISD-backend-integration.md:696

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
Source: docs/32-06-ISD-backend-integration.md:708

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
Title: Confirm downstream packets with stop-and-wait delivery  
Source: docs/32-06-ISD-backend-integration.md:644

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-078**
- verifies <- **VC-ST1-011**

### Diagram references

_None._

## IF06-REQ-015

Type: ifreq (Interface Requirement)  
Title: Separate stable EventData from live current reference data  
Source: docs/32-06-ISD-backend-integration.md:655

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
Source: docs/32-06-ISD-backend-integration.md:666

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-079**

### Diagram references

_None._

## IF06-REQ-017

Type: ifreq (Interface Requirement)  
Title: Exchange the TimingData sequence position  
Source: docs/32-06-ISD-backend-integration.md:564

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-081**
- depends_on <- **SI01-REQ-084**
- verifies <- **VC-ST1-012**

### Diagram references

_None._

## IF06-REQ-018

Type: ifreq (Interface Requirement)  
Title: Separate packet numbering from TimingData synchronization  
Source: docs/32-06-ISD-backend-integration.md:575

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-084**
- verifies <- **VC-ST1-010**
- verifies <- **VC-ST1-011**

### Diagram references

_None._

## IF06-REQ-019

Type: ifreq (Interface Requirement)  
Title: Make TimingData retransmission idempotent by record identity  
Source: docs/32-06-ISD-backend-integration.md:584

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-082**
- verifies <- **VC-ST1-012**

### Diagram references

_None._

## IF06-REQ-020

Type: ifreq (Interface Requirement)  
Title: Request retained TimingData by source sequence  
Source: docs/32-06-ISD-backend-integration.md:594

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-082**
- verifies <- **VC-ST1-012**

### Diagram references

_None._

## IF06-REQ-021

Type: ifreq (Interface Requirement)  
Title: Re-establish TimingData synchronization after connection changes  
Source: docs/32-06-ISD-backend-integration.md:604

### Authored outgoing

_None._

### Generated incoming

- depends_on <- **SI01-REQ-085**
- verifies <- **VC-ST1-012**

### Diagram references

_None._

## IF06-REQ-022

Type: ifreq (Interface Requirement)  
Title: Bound IF-06 data-message size  
Source: docs/32-06-ISD-backend-integration.md:633

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## Keypad

Type: arch (Architecture Element)  
Title: Keypad  
Source: docs/41-01-SSD-timing-application-specification-document.md:1901

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:355 (diagram=layered-architecture, node=devices-io)

## LogBook

Type: arch (Architecture Element)  
Title: LogBook  
Source: docs/41-01-SSD-timing-application-specification-document.md:2188

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:263 (diagram=layered-architecture, node=node-data)

## Logging

Type: arch (Architecture Element)  
Title: Logging  
Source: docs/41-01-SSD-timing-application-specification-document.md:2142

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-LoggingRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:509 (diagram=layered-architecture, node=logging-infra)

## LoggingServer

Type: arch (Architecture Element)  
Title: LoggingServer  
Source: docs/41-01-SSD-timing-application-specification-document.md:2152

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-LoggingRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:501 (diagram=layered-architecture, node=logging-server)

## Messaging

Type: arch (Architecture Element)  
Title: Messaging  
Source: docs/41-01-SSD-timing-application-specification-document.md:1805

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:379 (diagram=layered-architecture, node=messaging-io)

## MonotonicClock

Type: arch (Architecture Element)  
Title: MonotonicClock  
Source: docs/41-01-SSD-timing-application-specification-document.md:2072

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:433 (diagram=layered-architecture, node=platform-environment)

## NetworkDeviceService

Type: arch (Architecture Element)  
Title: NetworkDeviceService  
Source: docs/41-01-SSD-timing-application-specification-document.md:1929

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-IOComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:374 (diagram=layered-architecture, node=device-network-io)

## NextUpTeams

Type: arch (Architecture Element)  
Title: NextUpTeams  
Source: docs/41-01-SSD-timing-application-specification-document.md:1491

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:206 (diagram=layered-architecture, node=next-up-teams)

## NodeUpstream

Type: arch (Architecture Element)  
Title: NodeUpstream  
Source: docs/41-01-SSD-timing-application-specification-document.md:1476

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:277 (diagram=layered-architecture, node=upstream-message-port)

## OperatingSystem

Type: arch (Architecture Element)  
Title: OperatingSystem  
Source: docs/41-01-SSD-timing-application-specification-document.md:2079

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:435 (diagram=layered-architecture, node=platform-environment)

## PlatformEnvironment

Type: arch (Architecture Element)  
Title: PlatformEnvironment  
Source: docs/41-01-SSD-timing-application-specification-document.md:2061

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:427 (diagram=layered-architecture, node=platform-environment)

## PlatformEvents

Type: arch (Architecture Element)  
Title: PlatformEvents  
Source: docs/41-01-SSD-timing-application-specification-document.md:2039

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingNodeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:415 (diagram=layered-architecture, node=platform-events)

## PlatformExecution

Type: arch (Architecture Element)  
Title: PlatformExecution  
Source: docs/41-01-SSD-timing-application-specification-document.md:1994

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-CooperativeExecution**
- elaborates <- **DD-RuntimeExecution**
- elaborates <- **DD-RuntimeWorkAndMeasurements**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:400 (diagram=layered-architecture, node=platform-execution)

## PlatformTime

Type: arch (Architecture Element)  
Title: PlatformTime  
Source: docs/41-01-SSD-timing-application-specification-document.md:2086

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:440 (diagram=layered-architecture, node=platform-time)

## PowerDevice

Type: arch (Architecture Element)  
Title: PowerDevice  
Source: docs/41-01-SSD-timing-application-specification-document.md:1844

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:343 (diagram=layered-architecture, node=devices-io)

## PresentationGateway

Type: arch (Architecture Element)  
Title: PresentationGateway  
Source: docs/41-01-SSD-timing-application-specification-document.md:1315

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
Source: docs/41-01-SSD-timing-application-specification-document.md:1075

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:469 (diagram=layered-architecture, node=presentation-runtime)

## RabbitMqConnector

Type: arch (Architecture Element)  
Title: RabbitMqConnector  
Source: docs/41-01-SSD-timing-application-specification-document.md:1963

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:392 (diagram=layered-architecture, node=messaging-io)

## RegisteredTeams

Type: arch (Architecture Element)  
Title: RegisteredTeams  
Source: docs/41-01-SSD-timing-application-specification-document.md:1595

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:250 (diagram=layered-architecture, node=node-registration)

## RemoteShell

Type: arch (Architecture Element)  
Title: RemoteShell  
Source: docs/41-01-SSD-timing-application-specification-document.md:1251

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:116 (diagram=layered-architecture, node=remote-shell)

## Rev1CanDisplay

Type: arch (Architecture Element)  
Title: Rev1CanDisplay  
Source: docs/41-01-SSD-timing-application-specification-document.md:1887

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:351 (diagram=layered-architecture, node=devices-io)

## Rev1CanKeypad

Type: arch (Architecture Element)  
Title: Rev1CanKeypad  
Source: docs/41-01-SSD-timing-application-specification-document.md:1908

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:358 (diagram=layered-architecture, node=devices-io)

## Rev2WifiDisplay

Type: arch (Architecture Element)  
Title: Rev2WifiDisplay  
Source: docs/41-01-SSD-timing-application-specification-document.md:1894

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:353 (diagram=layered-architecture, node=devices-io)

## RuntimeExecutors

Type: arch (Architecture Element)  
Title: RuntimeExecutors  
Source: docs/41-01-SSD-timing-application-specification-document.md:1084

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
Source: docs/41-01-SSD-timing-application-specification-document.md:1090

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:485 (diagram=layered-architecture, node=runtime-time-sources)

## SI01-REQ-001

Type: req (Requirement)  
Title: Start from external configuration  
Source: docs/41-01-SSD-timing-application-specification-document.md:805

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
Source: docs/41-01-SSD-timing-application-specification-document.md:812

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-003

Type: req (Requirement)  
Title: Configured TimingNode availability  
Source: docs/41-01-SSD-timing-application-specification-document.md:820

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
Source: docs/41-01-SSD-timing-application-specification-document.md:833

### Authored outgoing

_None._

### Generated incoming

- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-011

Type: req (Requirement)  
Title: Consistent identity across interfaces  
Source: docs/41-01-SSD-timing-application-specification-document.md:841

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-020

Type: req (Requirement)  
Title: Current application status snapshot  
Source: docs/41-01-SSD-timing-application-specification-document.md:329

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
Source: docs/41-01-SSD-timing-application-specification-document.md:338

### Authored outgoing

- depends_on -> **SI01-REQ-024**
- specifies -> **UC-009**

### Generated incoming

- realizes <- **TimingNode**
- verifies <- **VC-ST1-001**

### Diagram references

_None._

## SI01-REQ-022

Type: req (Requirement)  
Title: Equivalent status semantics across interfaces  
Source: docs/41-01-SSD-timing-application-specification-document.md:903

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
Title: TimingNode current-state change publication  
Source: docs/41-01-SSD-timing-application-specification-document.md:357

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
Title: Current TimingNode states  
Source: docs/41-01-SSD-timing-application-specification-document.md:310

### Authored outgoing

- specifies -> **UC-001**
- specifies -> **UC-002**
- specifies -> **UC-009**

### Generated incoming

- depends_on <- **SI01-REQ-021**
- depends_on <- **SI01-REQ-023**
- depends_on <- **SI01-REQ-025**
- depends_on <- **SI01-REQ-026**
- depends_on <- **SI01-REQ-072**
- depends_on <- **SI01-REQ-073**
- depends_on <- **SI01-REQ-074**
- depends_on <- **SI01-REQ-087**
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
Source: docs/41-01-SSD-timing-application-specification-document.md:369

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
Source: docs/41-01-SSD-timing-application-specification-document.md:163

### Authored outgoing

- depends_on -> **SI01-REQ-024**
- depends_on -> **SI01-REQ-040**
- specifies -> **UC-001**
- specifies -> **UC-002**
- specifies -> **UC-009**

### Generated incoming

- depends_on <- **SI01-REQ-086**
- refines <- **IF03-REQ-008**
- refines <- **IF04-REQ-006**
- refines <- **SI02-REQ-008**

### Diagram references

_None._

## SI01-REQ-030

Type: req (Requirement)  
Title: Equivalent command/query semantics across transports  
Source: docs/41-01-SSD-timing-application-specification-document.md:913

### Authored outgoing

_None._

### Generated incoming

- realizes <- **PresentationGateway**

### Diagram references

_None._

## SI01-REQ-031

Type: req (Requirement)  
Title: Externally testable executable  
Source: docs/41-01-SSD-timing-application-specification-document.md:740

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
Source: docs/41-01-SSD-timing-application-specification-document.md:922

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-033

Type: req (Requirement)  
Title: Compatible IF-03 evolution  
Source: docs/41-01-SSD-timing-application-specification-document.md:931

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
- depends_on <- **SI01-REQ-087**
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
Source: docs/41-01-SSD-timing-application-specification-document.md:203

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
Source: docs/41-01-SSD-timing-application-specification-document.md:229

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
Source: docs/41-01-SSD-timing-application-specification-document.md:727

### Authored outgoing

- specifies -> **UC-009**

### Generated incoming

- verifies <- **VC-ST1-002**

### Diagram references

_None._

## SI01-REQ-044

Type: req (Requirement)  
Title: Reconnect rebuild before live presentation  
Source: docs/41-01-SSD-timing-application-specification-document.md:382

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
Source: docs/41-01-SSD-timing-application-specification-document.md:853

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
- depends_on <- **SI01-REQ-088**

### Diagram references

_None._

## SI01-REQ-046

Type: req (Requirement)  
Title: Write TimingData before commit completion  
Source: docs/41-01-SSD-timing-application-specification-document.md:865

### Authored outgoing

- specifies -> **UC-003**
- specifies -> **UC-012**
- specifies -> **UC-021**

### Generated incoming

- depends_on <- **SI01-REQ-072**
- depends_on <- **SI01-REQ-086**
- depends_on <- **SI01-REQ-087**
- depends_on <- **SI01-REQ-088**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## SI01-REQ-047

Type: req (Requirement)  
Title: Restore committed TimingData after restart  
Source: docs/41-01-SSD-timing-application-specification-document.md:671

### Authored outgoing

- depends_on -> **IF05-REQ-002**
- depends_on -> **IF05-REQ-003**
- depends_on -> **IF05-REQ-007**
- specifies -> **UC-013**

### Generated incoming

- depends_on <- **SI01-REQ-088**
- verifies <- **VC-ST1-002**
- verifies <- **VC-ST1-007**
- verifies <- **VC-ST1-008**

### Diagram references

_None._

## SI01-REQ-048

Type: req (Requirement)  
Title: Reject invalid TimingData recovery input  
Source: docs/41-01-SSD-timing-application-specification-document.md:687

### Authored outgoing

- specifies -> **UC-013**

### Generated incoming

- depends_on <- **SI01-REQ-088**
- verifies <- **VC-ST1-004**

### Diagram references

_None._

## SI01-REQ-049

Type: req (Requirement)  
Title: Contain TimingNode recovery failure  
Source: docs/41-01-SSD-timing-application-specification-document.md:699

### Authored outgoing

- specifies -> **UC-020**

### Generated incoming

- depends_on <- **SI01-REQ-074**

### Diagram references

_None._

## SI01-REQ-050

Type: req (Requirement)  
Title: Use maximum-RSSI tag observation for registration  
Source: docs/41-01-SSD-timing-application-specification-document.md:239

### Authored outgoing

- specifies -> **UC-003**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-051

Type: req (Requirement)  
Title: Keep local registration independent from presentation, logging and upstream delivery  
Source: docs/41-01-SSD-timing-application-specification-document.md:255

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
Source: docs/41-01-SSD-timing-application-specification-document.md:639

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
Source: docs/41-01-SSD-timing-application-specification-document.md:266

### Authored outgoing

- specifies -> **UC-003**

### Generated incoming

- realizes <- **TimingSystemConductor**

### Diagram references

_None._

## SI01-REQ-054

Type: req (Requirement)  
Title: Multiplex mutually exclusive antenna inventory  
Source: docs/41-01-SSD-timing-application-specification-document.md:283

### Authored outgoing

- specifies -> **UC-003**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-055

Type: req (Requirement)  
Title: Allow antenna recovery without process restart  
Source: docs/41-01-SSD-timing-application-specification-document.md:653

### Authored outgoing

- specifies -> **UC-004**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-060

Type: req (Requirement)  
Title: Traceable ready-team registry  
Source: docs/41-01-SSD-timing-application-specification-document.md:395

### Authored outgoing

- specifies -> **UC-005**

### Generated incoming

- depends_on <- **SI01-REQ-061**

### Diagram references

_None._

## SI01-REQ-061

Type: req (Requirement)  
Title: Drive passive CAN display from current application state  
Source: docs/41-01-SSD-timing-application-specification-document.md:408

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
Source: docs/41-01-SSD-timing-application-specification-document.md:420

### Authored outgoing

- specifies -> **UC-007**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-063

Type: req (Requirement)  
Title: Apply TimingNode-scoped RaceData from the Central System  
Source: docs/41-01-SSD-timing-application-specification-document.md:434

### Authored outgoing

- depends_on -> **IF06-REQ-004**
- depends_on -> **IF06-REQ-005**
- specifies -> **UC-010**

### Generated incoming

- depends_on <- **SI01-REQ-077**
- depends_on <- **SI01-REQ-078**
- verifies <- **VC-ST1-011**

### Diagram references

_None._

## SI01-REQ-064

Type: req (Requirement)  
Title: Transport-independent upstream synchronization  
Source: docs/41-01-SSD-timing-application-specification-document.md:448

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
Source: docs/41-01-SSD-timing-application-specification-document.md:462

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
Source: docs/41-01-SSD-timing-application-specification-document.md:750

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
Source: docs/41-01-SSD-timing-application-specification-document.md:762

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
Source: docs/41-01-SSD-timing-application-specification-document.md:774

### Authored outgoing

- depends_on -> **SI01-REQ-064**
- specifies -> **UC-017**

### Generated incoming

- refines <- **IF03-REQ-025**
- refines <- **IF03-REQ-026**
- refines <- **IF03-REQ-027**
- refines <- **IF03-REQ-028**

### Diagram references

_None._

## SI01-REQ-069

Type: req (Requirement)  
Title: Verify production-shaped RabbitMQ connector behaviour  
Source: docs/41-01-SSD-timing-application-specification-document.md:789

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
Source: docs/41-01-SSD-timing-application-specification-document.md:297

### Authored outgoing

- specifies -> **UC-019**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-071

Type: req (Requirement)  
Title: Operator manual registration  
Source: docs/41-01-SSD-timing-application-specification-document.md:215

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
Source: docs/41-01-SSD-timing-application-specification-document.md:99

### Authored outgoing

- depends_on -> **SI01-REQ-024**
- depends_on -> **SI01-REQ-046**
- specifies -> **UC-002**

### Generated incoming

- depends_on <- **SI01-REQ-087**
- refines <- **IF03-REQ-011**
- refines <- **IF04-REQ-004**
- refines <- **IF04-REQ-005**

### Diagram references

_None._

## SI01-REQ-073

Type: req (Requirement)  
Title: Registration lifecycle independent of operator sessions  
Source: docs/41-01-SSD-timing-application-specification-document.md:151

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
Title: Reject opening when a required capability is unavailable  
Source: docs/41-01-SSD-timing-application-specification-document.md:139

### Authored outgoing

- depends_on -> **SI01-REQ-024**
- depends_on -> **SI01-REQ-049**
- depends_on -> **SI01-REQ-052**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-075

Type: req (Requirement)  
Title: Maintain upstream PING request/answer lifecycle  
Source: docs/41-01-SSD-timing-application-specification-document.md:604

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
Source: docs/41-01-SSD-timing-application-specification-document.md:622

### Authored outgoing

- depends_on -> **IF06-REQ-013**

### Generated incoming

- verifies <- **VC-ST1-009**

### Diagram references

_None._

## SI01-REQ-077

Type: req (Requirement)  
Title: Resolve TeamId without rewriting TimingData  
Source: docs/41-01-SSD-timing-application-specification-document.md:542

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
Title: Apply RaceData once and confirm downstream delivery  
Source: docs/41-01-SSD-timing-application-specification-document.md:557

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
- verifies <- **VC-ST1-011**

### Diagram references

_None._

## SI01-REQ-079

Type: req (Requirement)  
Title: Apply RaceData stage-start-time changes  
Source: docs/41-01-SSD-timing-application-specification-document.md:572

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
Source: docs/41-01-SSD-timing-application-specification-document.md:586

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
Title: Exchange TimingData sequence position  
Source: docs/41-01-SSD-timing-application-specification-document.md:476

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
- verifies <- **VC-ST1-012**

### Diagram references

_None._

## SI01-REQ-082

Type: req (Requirement)  
Title: Serve TimingData requests from the retained LogBook  
Source: docs/41-01-SSD-timing-application-specification-document.md:489

### Authored outgoing

- depends_on -> **IF06-REQ-019**
- depends_on -> **IF06-REQ-020**
- depends_on -> **SI01-REQ-081**
- specifies -> **UC-011**
- specifies -> **UC-012**

### Generated incoming

- depends_on <- **SI01-REQ-085**
- verifies <- **VC-ST1-012**

### Diagram references

_None._

## SI01-REQ-083

Type: req (Requirement)  
Title: Rebuild TimingData pending work without a second payload history  
Source: docs/41-01-SSD-timing-application-specification-document.md:501

### Authored outgoing

- depends_on -> **SI01-REQ-042**
- depends_on -> **SI01-REQ-081**
- specifies -> **UC-012**
- specifies -> **UC-013**

### Generated incoming

- verifies <- **VC-ST1-012**

### Diagram references

_None._

## SI01-REQ-084

Type: req (Requirement)  
Title: Expose diagnosable packet and TimingData synchronization state  
Source: docs/41-01-SSD-timing-application-specification-document.md:513

### Authored outgoing

- depends_on -> **IF06-REQ-017**
- depends_on -> **IF06-REQ-018**
- depends_on -> **SI01-REQ-078**
- depends_on -> **SI01-REQ-081**

### Generated incoming

- refines <- **IF03-REQ-027**
- verifies <- **VC-ST1-011**
- verifies <- **VC-ST1-012**

### Diagram references

_None._

## SI01-REQ-085

Type: req (Requirement)  
Title: Re-establish packet delivery and TimingData synchronization on reconnect  
Source: docs/41-01-SSD-timing-application-specification-document.md:524

### Authored outgoing

- depends_on -> **IF06-REQ-021**
- depends_on -> **SI01-REQ-078**
- depends_on -> **SI01-REQ-081**
- depends_on -> **SI01-REQ-082**
- specifies -> **UC-011**
- specifies -> **UC-012**

### Generated incoming

- refines <- **IF03-REQ-027**
- verifies <- **VC-ST1-012**

### Diagram references

_None._

## SI01-REQ-086

Type: req (Requirement)  
Title: Log result-bearing TimingNode operation failures  
Source: docs/41-01-SSD-timing-application-specification-document.md:177

### Authored outgoing

- depends_on -> **SI01-REQ-026**
- depends_on -> **SI01-REQ-046**
- specifies -> **UC-001**
- specifies -> **UC-002**
- specifies -> **UC-009**
- specifies -> **UC-020**
- specifies -> **UC-021**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-087

Type: req (Requirement)  
Title: Record applied lifecycle transitions as TimingData  
Source: docs/41-01-SSD-timing-application-specification-document.md:118

### Authored outgoing

- depends_on -> **SI01-REQ-024**
- depends_on -> **SI01-REQ-040**
- depends_on -> **SI01-REQ-046**
- depends_on -> **SI01-REQ-072**
- specifies -> **UC-001**
- specifies -> **UC-002**
- specifies -> **UC-009**

### Generated incoming

_None._

### Diagram references

_None._

## SI01-REQ-088

Type: req (Requirement)  
Title: Engineering backup and clear of persisted TimingData  
Source: docs/41-01-SSD-timing-application-specification-document.md:879

### Authored outgoing

- depends_on -> **SI01-REQ-045**
- depends_on -> **SI01-REQ-046**
- depends_on -> **SI01-REQ-047**
- depends_on -> **SI01-REQ-048**

### Generated incoming

_None._

### Diagram references

_None._

## SI02-REQ-001

Type: req (Requirement)  
Title: Use only supported public SI-01 boundaries  
Source: docs/41-02-SSD-gui-application-specification-document.md:56

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
Source: docs/41-02-SSD-gui-application-specification-document.md:68

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
Source: docs/41-02-SSD-gui-application-specification-document.md:80

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
Source: docs/41-02-SSD-gui-application-specification-document.md:90

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
Source: docs/41-02-SSD-gui-application-specification-document.md:103

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
Source: docs/41-02-SSD-gui-application-specification-document.md:115

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
Source: docs/41-02-SSD-gui-application-specification-document.md:128

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
Source: docs/41-02-SSD-gui-application-specification-document.md:140

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
Source: docs/41-02-SSD-gui-application-specification-document.md:154

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
Source: docs/41-02-SSD-gui-application-specification-document.md:168

### Authored outgoing

- depends_on -> **IF03-REQ-012**
- depends_on -> **IF03-REQ-024**
- specifies -> **UC-009**

### Generated incoming

_None._

### Diagram references

_None._

## SI02-REQ-011

Type: req (Requirement)  
Title: Simulate the Central System upstream peer through supported transports  
Source: docs/41-02-SSD-gui-application-specification-document.md:181

### Authored outgoing

- specifies -> **UC-009**

### Generated incoming

_None._

### Diagram references

_None._

## SerialLane

Type: arch (Architecture Element)  
Title: SerialLane  
Source: docs/41-01-SSD-timing-application-specification-document.md:2001

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-RuntimeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:405 (diagram=layered-architecture, node=platform-execution)

## SerialTaskRunner

Type: arch (Architecture Element)  
Title: SerialTaskRunner  
Source: docs/41-01-SSD-timing-application-specification-document.md:2009

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-CooperativeExecution**
- elaborates <- **DD-RuntimeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:407 (diagram=layered-architecture, node=platform-execution)

## SharedTerminalHandler

Type: arch (Architecture Element)  
Title: SharedTerminalHandler  
Source: docs/41-01-SSD-timing-application-specification-document.md:1259

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:148 (diagram=layered-architecture, node=shared-terminal)

## SimulatedAntenna

Type: arch (Architecture Element)  
Title: SimulatedAntenna  
Source: docs/41-01-SSD-timing-application-specification-document.md:1862

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:339 (diagram=layered-architecture, node=devices-io)

## SimulatedPowerDevice

Type: arch (Architecture Element)  
Title: SimulatedPowerDevice  
Source: docs/41-01-SSD-timing-application-specification-document.md:1854

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-AntennaRuntime**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:346 (diagram=layered-architecture, node=devices-io)

## SimulationRuntime

Type: arch (Architecture Element)  
Title: SimulationRuntime  
Source: docs/41-01-SSD-timing-application-specification-document.md:1066

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:461 (diagram=layered-architecture, node=simulation-runtime)

## StageStartTimes

Type: arch (Architecture Element)  
Title: StageStartTimes  
Source: docs/41-01-SSD-timing-application-specification-document.md:1548

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:236 (diagram=layered-architecture, node=node-racedata)

## Storage

Type: arch (Architecture Element)  
Title: Storage  
Source: docs/41-01-SSD-timing-application-specification-document.md:1770

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:315 (diagram=layered-architecture, node=storage-io)

## TagProcessor

Type: arch (Architecture Element)  
Title: TagProcessor  
Source: docs/41-01-SSD-timing-application-specification-document.md:1536

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-EventTagProcessing**
- elaborates <- **DD-RuntimeWorkAndMeasurements**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:220 (diagram=layered-architecture, node=node-processing)

## TaskStep

Type: arch (Architecture Element)  
Title: TaskStep  
Source: docs/41-01-SSD-timing-application-specification-document.md:2025

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-CooperativeExecution**

### Diagram references

_None._

## TeamAssignments

Type: arch (Architecture Element)  
Title: TeamAssignments  
Source: docs/41-01-SSD-timing-application-specification-document.md:1559

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:234 (diagram=layered-architecture, node=node-racedata)

## TimeSource

Type: arch (Architecture Element)  
Title: TimeSource  
Source: docs/41-01-SSD-timing-application-specification-document.md:2094

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-TimingTimeComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:445 (diagram=layered-architecture, node=platform-time)

## TimingApplicationRuntime

Type: arch (Architecture Element)  
Title: TimingApplicationRuntime  
Source: docs/41-01-SSD-timing-application-specification-document.md:1056

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-ExecutableComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:453 (diagram=layered-architecture, node=timing-application-runtime)

## TimingData

Type: arch (Architecture Element)  
Title: TimingData  
Source: docs/41-01-SSD-timing-application-specification-document.md:2197

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
Source: docs/41-01-SSD-timing-application-specification-document.md:2177

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
Source: docs/41-01-SSD-timing-application-specification-document.md:1521

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:258 (diagram=layered-architecture, node=node-data)

## TimingNodeDataLane

Type: arch (Architecture Element)  
Title: TimingNode Data Lane  
Source: docs/41-01-SSD-timing-application-specification-document.md:2403

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## TimingNodeProcessing

Type: arch (Architecture Element)  
Title: TimingNode Processing  
Source: docs/41-01-SSD-timing-application-specification-document.md:1504

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:215 (diagram=layered-architecture, node=node-processing)

## TimingNodeProxy

Type: arch (Architecture Element)  
Title: TimingNodeProxy  
Source: docs/41-01-SSD-timing-application-specification-document.md:1336

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-PresentationAccess**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:176 (diagram=layered-architecture, node=timing-node-proxy)

## TimingNodeRaceData

Type: arch (Architecture Element)  
Title: TimingNode RaceData  
Source: docs/41-01-SSD-timing-application-specification-document.md:1513

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:229 (diagram=layered-architecture, node=node-racedata)

## TimingNodeRegistration

Type: arch (Architecture Element)  
Title: TimingNode Registration  
Source: docs/41-01-SSD-timing-application-specification-document.md:1530

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:243 (diagram=layered-architecture, node=node-registration)

## TimingNodeTaskLane

Type: arch (Architecture Element)  
Title: TimingNode Task Lane  
Source: docs/41-01-SSD-timing-application-specification-document.md:2415

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

_None._

## TimingSystem

Type: arch (Architecture Element)  
Title: TimingSystem  
Source: docs/41-01-SSD-timing-application-specification-document.md:2165

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**
- elaborates <- **DD-IOComposition**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:51 (diagram=layered-architecture, node=timing-system-aggregate)

## TimingSystemConductor

Type: arch (Architecture Element)  
Title: TimingSystem Conductor  
Source: docs/41-01-SSD-timing-application-specification-document.md:1409

### Authored outgoing

- realizes -> **SI01-REQ-053**

### Generated incoming

- elaborates <- **DD-CooperativeExecution**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:192 (diagram=layered-architecture, node=system-conductor)

## TimingSystemUpstream

Type: arch (Architecture Element)  
Title: TimingSystem Upstream  
Source: docs/41-01-SSD-timing-application-specification-document.md:1458

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:272 (diagram=layered-architecture, node=upstream-message-port)

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
- specifies <- **SI01-REQ-086**
- specifies <- **SI01-REQ-087**

### Diagram references

_None._

## UC-002

Type: uc (Use Case)  
Title: Close a registration point  
Source: docs/30-UC-system-use-cases.md:172

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
- specifies <- **SI01-REQ-086**
- specifies <- **SI01-REQ-087**

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
- specifies <- **SI01-REQ-086**
- specifies <- **SI01-REQ-087**
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
- specifies <- **SI02-REQ-011**

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

- specifies <- **SI01-REQ-049**
- specifies <- **SI01-REQ-086**

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
- specifies <- **SI01-REQ-086**

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

## UpstreamData

Type: arch (Architecture Element)  
Title: UpstreamData  
Source: docs/41-01-SSD-timing-application-specification-document.md:2207

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:305 (diagram=layered-architecture, node=upstream-data-domain)

## UpstreamGateway

Type: arch (Architecture Element)  
Title: UpstreamGateway  
Source: docs/41-01-SSD-timing-application-specification-document.md:1937

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:384 (diagram=layered-architecture, node=messaging-io)

## UpstreamStream

Type: arch (Architecture Element)  
Title: UpstreamStream  
Source: docs/41-01-SSD-timing-application-specification-document.md:1945

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-DomainIntegration**

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:387 (diagram=layered-architecture, node=messaging-io)

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
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:216

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
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:277

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
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:318

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
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:358

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
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:412

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
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:461

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
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:518

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
Title: Verify default UpstreamData packet envelope and embedded TimingData  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:579

### Authored outgoing

- verifies -> **IF06-REQ-001**
- verifies -> **IF06-REQ-002**
- verifies -> **IF06-REQ-003**
- verifies -> **IF06-REQ-008**
- verifies -> **IF06-REQ-010**
- verifies -> **IF06-REQ-018**

### Generated incoming

_None._

### Diagram references

_None._

## VC-ST1-011

Type: vc (Verification Case)  
Title: Verify downstream stop-and-wait RECV and idempotent RaceData apply  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:624

### Authored outgoing

- verifies -> **IF06-REQ-004**
- verifies -> **IF06-REQ-005**
- verifies -> **IF06-REQ-014**
- verifies -> **IF06-REQ-018**
- verifies -> **SI01-REQ-063**
- verifies -> **SI01-REQ-078**
- verifies -> **SI01-REQ-084**

### Generated incoming

_None._

### Diagram references

_None._

## VC-ST1-012

Type: vc (Verification Case)  
Title: Verify TimingData SEQ and retained LogBook replay  
Source: docs/61-01-VTS-timing-application-verification-test-specification.md:664

### Authored outgoing

- verifies -> **IF06-REQ-017**
- verifies -> **IF06-REQ-019**
- verifies -> **IF06-REQ-020**
- verifies -> **IF06-REQ-021**
- verifies -> **SI01-REQ-081**
- verifies -> **SI01-REQ-082**
- verifies -> **SI01-REQ-083**
- verifies -> **SI01-REQ-084**
- verifies -> **SI01-REQ-085**

### Generated incoming

_None._

### Diagram references

_None._

## VendorAntenna

Type: arch (Architecture Element)  
Title: VendorAntenna  
Source: docs/41-01-SSD-timing-application-specification-document.md:1869

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:341 (diagram=layered-architecture, node=devices-io)

## Web

Type: arch (Architecture Element)  
Title: Web  
Source: docs/41-01-SSD-timing-application-specification-document.md:1227

### Authored outgoing

_None._

### Generated incoming

_None._

### Diagram references

- bld/sphinx-needs/diagrams/layered-architecture.yaml:126 (diagram=layered-architecture, node=web-interface)

## YieldingTask

Type: arch (Architecture Element)  
Title: YieldingTask  
Source: docs/41-01-SSD-timing-application-specification-document.md:2018

### Authored outgoing

_None._

### Generated incoming

- elaborates <- **DD-CooperativeExecution**

### Diagram references

_None._
