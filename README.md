
# Rocket Lab Production Automation Coding Test

Produce GUI for testing team to visualise the behivour of multiple devices
simultaneously, using only the Python standard library and PyQt5.

My nervousness and eagerness to impress has driven a few too many cycles of
refactoring, and hence the app has become rather over-engineered! That said,
I'm quite happy about how the networking and data conversion system, and the
optional-extra command-line worked out.


## Requirements

PyQt5 and at least Python 3.11, as it makes heavy use of static typing and
dataclasses.


## Graphical Interface

The application is both a command-line and a GUI. If called with no arguments
the GUI will start, eg.

    $ cd ~/Projects/rocket-test/
    $ ./leon
    ...GUI will start...


## Unit tests

    $ ./run_tests.sh


## Command-line

If any command-line arguments are given, an alternative text-only interface
will be used. The command-line was built to ensure a rapid testing cycle.

### Help

    $ ./leon --help
    usage: rocket_lab [-h] [--multicast ADDRESS:PORT] [-t TIMEOUT] [-v] COMMAND ...

    Rocket Lab Production Automation Coding Test

    positional arguments:
      COMMAND
        discover            Find devices on network via UDP multicast
        test                Run test on the selected device
        gui                 Start PyQT graphical user interface (default)

    options:
      -h, --help            show this help message and exit
      --multicast ADDRESS:PORT
                            Multicast IP address and port (default 224.3.11.15:31115)
      -t TIMEOUT, --timeout TIMEOUT
                            Seconds to wait for response
      -v, --verbose         Enable debug logging output

    The default action is to start the GUI

### Discover

    $ ./leon discover
    2 devices responded to discovery:
    M001   SN0123457    192.168.0.10:6062
    M001   SN0123456    192.168.0.10:6061

### Test Device

    $ ./leon test 192.168.0.64:37370
    Start test on 192.168.0.64:37370 for 2s, status every 100ms
    INFO    Received 'test started' from device
       100 milliseconds:      50.60mA   4,477.30mV
       200 milliseconds:      13.60mA   4,460.30mV
       300 milliseconds:     -11.10mA   4,448.90mV
       400 milliseconds:     -23.40mA   4,443.20mV
       500 milliseconds:     -23.40mA   4,443.20mV
       600 milliseconds:     -11.00mA   4,448.90mV
       700 milliseconds:      13.70mA   4,460.30mV
       800 milliseconds:      50.70mA   4,477.30mV
       900 milliseconds:     100.10mA   4,500.00mV
     1,000 milliseconds:      38.40mA   4,471.70mV
     1,100 milliseconds:     -11.00mA   4,449.00mV
     1,200 milliseconds:     -48.00mA   4,431.90mV
     1,300 milliseconds:     -72.70mA   4,420.60mV
     1,400 milliseconds:     -85.00mA   4,414.90mV
     1,500 milliseconds:     -85.00mA   4,414.90mV
     1,600 milliseconds:     -72.70mA   4,420.60mV
     1,700 milliseconds:     -47.90mA   4,431.90mV
     1,800 milliseconds:     -10.90mA   4,449.00mV
     1,900 milliseconds:      38.50mA   4,471.70mV
     2,000 milliseconds:     -23.20mA   4,443.30mV
    INFO    Received 'test completed' from device
    Current mean -10.99mA, max 100.10mA, min -85.00mA
    Voltage mean  4,448.94mV, max 4,500.00mV, min 4,414.90mV


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


### Command-Line

- [x] Build minimal command-line interface for rapid prototyping
- [x] Implement 'discover' subcommand
- [x] Implement 'test' subcommand
- [x] Implement 'gui' default subcommand


### GUI

Check list for tasks producing graphic user interface.

- [x] Produce paper sketch of GUI elements
- [x] Produce prototype of GUI layout
- [x] List devices in navigation
- [x] Allow user to update list of devices
- [x] Allow user to select a device
- [ ] Add icons to navigation showing test state
- [ ] Add live plot of time against mV & mA
- [ ] Stretch goal: add useful aggregates over collected test data
    - Min/Max peaks
    - Averages (median and mean)?
    - Stddev
    - Maybe a nice box-and-whisker to visualise & compare above values?
