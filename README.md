
# Rocket Lab Production Automation Coding Test

Produce GUI for testing team to visualise the behivour of multiple devices
simultaneously, using only the Python standard library and PyQt5.

My nervousness and eagerness to impress has driven a few too many cycles of
refactoring, and hence the app has become rather over-engineered! That said,
I'm quite happy about how the networking and data conversion system, and the
optional-extra command-line worked out.


## Requirements

PyQt5 and at least Python 3.11, as it makes heavy use of optional static typing.


## Graphical Interface

The application is both a command-line and a GUI. If called with no arguments
the GUI will start, eg.

    $ cd ~/Projects/rocket-test/
    $ python3 -m rocket_lab
    ...GUI will start...


## Command-line

If any command-line arguments are given, an alternative text-only interface
will be used. The command-line was built to ensure a rapid testing cycle.

### Help

    $ cd ~/Projects/rocket-test/
    $ python3 -m rocket_lab --help
    usage: rocket_lab [-h] [-v] COMMAND ...

    Rocket Lab Production Automation Coding Test

    positional arguments:
      COMMAND
        discover     Find devices on network via UDP multicast
        test         Run test on the selected device

    options:
      -h, --help     show this help message and exit
      -v, --verbose  Enable debug logging output

    Run with zero aguments to start GUI

### Discover

    $ python3 -m rocket_lab discover
    2 devices responded to discovery:
    M001   SN0123457    192.168.0.10:6062
    M001   SN0123456    192.168.0.10:6061

### Test

    $ python3 -m rocket_lab test 192.168.0.10:6062 -s 30
    # TODO

## Tasks

Planned actions to complete project.

### Networking

Handle stream of multiplexed output from multiple, concurrent devices performing
test runs and reporting back results.

- [x] Experiment with UDP client/server
- [x] Experiment with UDP broadcasting
- [x] Send discovery messages to DUT simulator with UDP multicasting
- [x] Receive discovery messages from DUT simulator
- [x] Build list of devices on network via multicasting discovery messages
- [x] Send and recieve simple command to DUT via standard UDP networking
- [x] Start test and recieve test data, sending back to caller via generators
- [ ] Brainstorm approaches for collecting and demultiplexing device test data


### Command-Line

- [x] Build minimal command-line interface for rapid prototyping
- [x] Implement 'discover' subcommand
- [x] Implement 'test' subcommand


### GUI

Check list for tasks producing graphic user interface.

- [x] Produce paper sketch of GUI elements
- [x] Produce prototype of GUI layout
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
