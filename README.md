
# Rocket Lab Production Automation Coding Test

Produce GUI for testing team to visualise the behivour of multiple devices
simultaneously.


## Tasks

### Networking

Handle stream of multiplexed output from multiple, concurrent devices performing
test runs and reporting back results.

- [ ] Experiment with UDP client/server
- [ ] Experiment with UDP broadcasting
- [ ] Experiment with UDP multicasting with own server
- [ ] UDP multicasting experiment with DUT
- [ ] Collect list of devices on network via multicasting discovery messages
- [ ] Send and recieve simple command to DUT via standard UDP networking
- [ ] Brainstorm approaches for collecting and demultiplexing device test data


### GUI

- [ ] Produce paper sketch of GUI elements
- [ ] List devices in navigation
- [ ] Show current state of tests in navigation
- [ ] Detail view for devices and its collected test data
- [ ] Show current state of tests in detail area
- [ ] Add buttons to start & stop test in detail area
- [ ] Collect test duration (drop-down for standard values? Provide default?)
- [ ] Start with scrolling text area for logging messages
- [ ] Add live plot of time against mV & mA
- [ ] Stretch goal: add useful aggregates over colleted test data
    * Min/Max peaks
    * Averages (median and mean)?
    * Stddev
    * Maybe a nice box-and-whisker to visualise & compare above values?
