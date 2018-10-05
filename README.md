# A Python Client for the NoLimits 2 Telemetry Server
A simple implementation of a telemetry client for communication with the telemetry server of [NoLimits 2 - Roller Coaster Simulation](http://www.nolimitscoaster.com/).

## Usage
### A Minimal Example

Launch NoLimits with the --telemetry option and execute on the same machine:

```Python
from pprint import pprint

from nl2telemetry import NoLimits2
from nl2telemetry.message import get_telemetry, Answer

with NoLimits2() as nl2:
    nl2.send(get_telemetry)
    data = Answer.get_data(nl2.receive())
    pprint(data.__dict__)
```

## Requirements
* NoLimits 2 - Roller Coaster Simulation (tested with 2.5.6.0)
* Python 3 (developed in 3.7, confirmed to work with at least 3.5.2)

## Features 
* All messages available in NoLimits 2.5.6.0 __Standard and Professional__ are
implemented as IDE friendly classes.
* Simple demonstration applications. 
    * The Minimal example.
    * Live plotting of G-Forces (uses [matplotlib](https://matplotlib.org/)).
    
        ![](docs/liveplot.png?raw=True
    "matplotlib interface for live g force logging")
    * Logging of G-Forces as CSV data.
    * A Station Control Panel.
    
        ![](docs/dispatch_control.png?raw=True
    "telemetry based control panel")

## Limitations
* No messages that require the __Attraction License__ message of NoLimits 2
are implemented.
* No efforts have been made to ensure or even test parallel execution
capability or stability.
