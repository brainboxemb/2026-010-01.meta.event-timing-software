
## Timing-system detail views

### TimingSystem internals — ordered ingress, services and persistence

![TimingSystem internals — ordered ingress, services and persistence](./timing-system-internals.svg)

- [Editable draw.io file](./timing-system-internals.drawio)

### RFID pipeline — raw encrypted reads to accepted registration

![RFID pipeline — raw encrypted reads to accepted registration](./rfid-pipeline.svg)

- [Editable draw.io file](./rfid-pipeline.drawio)


## Data, traceability and display views

### In-memory data, backup and V1/V2 display behaviour

![In-memory data, backup and V1/V2 display behaviour](./data-display-flow.svg)

- [Editable draw.io file](./data-display-flow.drawio)

### Registration traceability — monotonic sequence per registration source

![Registration traceability — monotonic sequence per registration source](./registration-stream-identity.svg)

- [Editable draw.io file](./registration-stream-identity.drawio)


## System software-item, topology and state-model views

### Software items and principal system interfaces

![Software items and principal system interfaces](./software-item-system-overview.svg)

- [Editable draw.io file](./software-item-system-overview.drawio)

### Configurable runtime topology — instances, assets, sources and antennas

![Configurable runtime topology — instances, assets, sources and antennas](./runtime-registration-topology.svg)

- [Editable draw.io file](./runtime-registration-topology.drawio)

### RabbitMQ — shared connection with per-source consumers and controlled publishing

![RabbitMQ — shared connection with per-source consumers and controlled publishing](./rabbitmq-source-topology.svg)

- [Editable draw.io file](./rabbitmq-source-topology.drawio)

### TimingSystemInstance lifecycle — operational lifecycle and health are separate

![TimingSystemInstance lifecycle — operational lifecycle and health are separate](./timing-system-lifecycle.svg)

- [Editable draw.io file](./timing-system-lifecycle.drawio)

### RFID reader lifecycle and recovery direction

![RFID reader lifecycle and recovery direction](./rfid-lifecycle.svg)

- [Editable draw.io file](./rfid-lifecycle.drawio)

### Connectivity status is layered; local timing is not a RabbitMQ connection state

![Connectivity status is layered; local timing is not a RabbitMQ connection state](./connectivity-layers.svg)

- [Editable draw.io file](./connectivity-layers.drawio)

