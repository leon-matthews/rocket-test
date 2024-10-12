
# Rocket Lab Production Automation Coding Test

Produce GUI for testing team to visualise the behivour of multiple devices
simultaneously, using only the Python standard library and PyQt5.

I have allowed myself the weekend to complete the task. Despite the short
timeframe, I have done my best to produce the sort of work I would produce
if I were to paid to build this sort of progam - with an eye on testability
and extensibility.


## Requirements

PyQt5 and at least Python 3.11, as it makes heavy use of optional static typing.


## Usage

The application is both a command-line and a GUI. If called with no arguments
the GUI will start, eg.

### GUI

    $ cd ~/Projects/rocket-test/
    $ python3 -m rocket_lab
    ...GUI will start...

### Command-line

    $ cd ~/Projects/rocket-test/
    $ python3 -m rocket_lab --help
    usage: rocket_lab [-h] {discover} ...

    Rocket Lab Production Automation Coding Test

    positional arguments:
      {discover}
        discover  Find DUT simulators using UDP multicast

    options:
      -h, --help  show this help message and exit

    Run with zero aguments to start GUI


## Tasks

Planned actions to complete project.

### Networking

Handle stream of multiplexed output from multiple, concurrent devices performing
test runs and reporting back results.

- [x] Experiment with UDP client/server
- [x] Experiment with UDP broadcasting
- [x] Send discovery messages to DUT simulator with UDP multicasting
- [x] Receive discovery messages from DUT simulator
- [ ] Build list of devices on network via multicasting discovery messages
- [ ] Send and recieve simple command to DUT via standard UDP networking
- [ ] Brainstorm approaches for collecting and demultiplexing device test data


### Command-Line

- [x] Build minimal command-line interface for rapid prototyping
- [x] Implement 'discover' subcommand


### GUI

Check list for tasks producing graphic user interface.

- [x] Produce paper sketch of GUI elements
- [ ] List devices in navigation
- [ ] Show current state of tests in navigation
- [ ] Detail view for devices and its collected test data
- [ ] Show current state of tests in detail area
- [ ] Add buttons to start & stop test in detail area
- [ ] Collect test duration (drop-down for standard values? Provide default?)
- [ ] Start with scrolling text area for logging messages
- [ ] Add live plot of time against mV & mA
- [ ] Stretch goal: add useful aggregates over colleted test data
    - Min/Max peaks
    - Averages (median and mean)?
    - Stddev
    - Maybe a nice box-and-whisker to visualise & compare above values?
