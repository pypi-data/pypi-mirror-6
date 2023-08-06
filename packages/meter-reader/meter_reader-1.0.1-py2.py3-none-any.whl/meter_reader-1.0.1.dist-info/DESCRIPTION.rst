Meter Reader
===============================================================================

Meter Reader is a client library and command line client for retrieving
nearly realtime energy usage data from a smart meter via the Eagle Energy
Gateway. See
`Rainforest Automation_ <http://www.rainforestautomation.com>`_ for more
about the Eagle Gateway.

Meter Reader is not affiliated with the Eagle Energy Gateway or
Rainforest Automation.

Installation
-------------------------------------------------------------------------------
::

    $ pip install meter-reader

Usage
-------------------------------------------------------------------------------
Meter Reader is intended to be used as a library for other applications
but it does contain a command line application called mr::

    $ mr < ip address >

This will run the ``LIST_DEVICES`` devices command on the gateway and display
a formatted response. Other commands, such as ``GET_DEVICE_DATA``, will first
run the ``LIST_DEVICES`` command to determine the MAC address of the gateway.

Commands can be specified with the '-c' option. For example::

    $ mr -c GET_DEVICE_DATA < ip address >

    MessageCluster
        DeviceMacId          xx:xx:xx:xx:xx:xx:xx:xx
        MeterMacId           xx:xx:xx:xx:xx:xx:xx
        TimeStamp            0
        Id                   0
        Priority             None
        Text                 None
        ConfirmationRequired N
        Confirmed            N
        Read                 Y
        Queue                active
    CurrentSummation
        DeviceMacId          xx:xx:xx:xx:xx:xx:xx:xx
        MeterMacId           xx:xx:xx:xx:xx:xx:xx
        TimeStamp            2014-04-19 16:01:22+00:00
        SummationDelivered   12949746
        SummationReceived    0
        Multiplier           1
        Divisor              1000
        DigitsRight          3
        DigitsLeft           15
        SuppressLeadingZero  Y
    NetworkInfo
    ...

::

    $ mr -c GET_SUMMATION_VALUES < ip address >

    2014-04-18 16:30:00+00:00, Summation, 0.350
    2014-04-18 17:30:00+00:00, Summation, 0.322
    2014-04-18 18:30:00+00:00, Summation, 0.193
    2014-04-18 19:30:00+00:00, Summation, 0.285
    2014-04-18 20:30:00+00:00, Summation, 0.286
    2014-04-18 21:30:00+00:00, Summation, 0.351
    ...

There are two ways to retrieve instantaneous demand:

1. Send the ``GET_INSTANTANEOUS_DEMAND`` command directly to the gateway. This
   will return a nearly raw response from the gateway (formatting is applied).

::

    $ mr -c GET_INSTANTANEOUS_DEMAND < ip address >

        InstantaneousDemand
        DeviceMacId         xx:xx:xx:xx:xx:xx:xx:xx
        MeterMacId          xx:xx:xx:xx:xx:xx:xx
        TimeStamp           2014-04-19 15:35:27+00:00
        Demand              297
        Multiplier          1
        Divisor             1000
        DigitsRight         3
        DigitsLeft          15
        SuppressLeadingZero Y

2. Supply the ``--get-instant-demand`` argument. This will post-process the
response before displaying it.::

    $ mr --get-instant-demand < ip address >

    2014-04-19 15:58:39+00:00, 0.292kW

Raw and unformatted data returned by the gatway, can be viewed by using the
'-r' option::

    $ mr -r -c GET_DEVICE_DATA < ip address >

Including meter_reader in an application
-------------------------------------------------------------------------------
::

    from meter_reader import Gateway

    GATEWAY_ADDRESS = '192.168.1.10'

    gw = Gateway(GATEWAY_ADDRESS)
    response = gw.run_command('GET_DEVICE_DATA')
    print('Network Info')
    print(response['NetworkInfo'])

    timestamp, demand = gw.get_instantaneous_demand()
    print('Demand {0} at {1}'.format(demand, timestamp))


Copyright (c) 2014, Emmanuel Levijarvi
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


