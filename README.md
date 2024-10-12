
# Rocket Lab Production Automation Coding Test

Produce GUI for testing team to visualise the behivour of multiple devices
simultaneously, using only the Python standard library and PyQt5.


## Tasks

Planned actions to complete project.

### Networking

Handle stream of multiplexed output from multiple, concurrent devices performing
test runs and reporting back results.

- [*] Experiment with UDP client/server
- [*] Experiment with UDP broadcasting
- [*] Send discovery messages to DUT simulator with UDP multicasting
- [*] Receive discovery messages from DUT simulator
- [ ] Build list of devices on network via multicasting discovery messages
- [ ] Send and recieve simple command to DUT via standard UDP networking
- [ ] Brainstorm approaches for collecting and demultiplexing device test data


### GUI

Check list for tasks producing graphic user interface.

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
    - Min/Max peaks
    - Averages (median and mean)?
    - Stddev
    - Maybe a nice box-and-whisker to visualise & compare above values?


## Notes

My working notes. Internal use only.

### Promiscuous UDP client

There are two modes of operation for UDP client code. Promiscuous and not. The
former will accept an UDP datagram to the client port from anywhere, the latter
rejects messages not from the server previously connected to.

    # Careful
    s.connect() -> s.send() -> s.recv()

    # Promiscuous
    sock.sendto() -> sock.recvfrom()


I've implemented both approaches in the echo server as `careful_client()` and
`promiscuous_client()`, as I'm not yet sure which will prove the most useful
for the final program.
