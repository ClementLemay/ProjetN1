#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from enocean.consolelogger import init_logging
import enocean.utils
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import RadioPacket
from enocean.protocol.constants import PACKET, RORG
import sys
import traceback
from parsingLog import *

try:
    import queue
except ImportError:
    import Queue as queue


def assemble_radio_packet(transmitter_id):
    return RadioPacket.create(rorg=RORG.BS4, rorg_func=0x20, rorg_type=0x01,
                              sender=transmitter_id,
                              CV=50,
                              TMP=21.5,
                              ES='true')


init_logging()
communicator = SerialCommunicator()
communicator.start()
print('The Base ID of your module is %s.' % enocean.utils.to_hex_string(communicator.base_id))

if communicator.base_id is not None:
    print('Sending example package.')
    communicator.send(assemble_radio_packet(communicator.base_id))

# endless loop receiving radio packets
while communicator.is_alive():
    try:
        # Loop to empty the queue...
        packet = communicator.receive.get(block=True, timeout=1)
	vreturn = packet
	if packet.packet_type == PACKET.RADIO and packet.rorg == RORG.BS4:
            # parse packet with given FUNC and TYPE
            for k in packet.parse_eep(0x02, 0x05):
                print('%s: %s' % (k, packet.parsed[k]))
		string = ('%s: %s' % (k, packet.parsed[k]))
		parserTemp(string,vreturn)
        if packet.packet_type == PACKET.RADIO and packet.rorg == RORG.BS1:
            # alternatively you can select FUNC and TYPE explicitely
            packet.select_eep(0x00, 0x01)
            # parse it
            packet.parse_eep()
            for k in packet.parsed:
                print('%s: %s' % (k, packet.parsed[k]))
		string=('%s: %s' % (k, packet.parsed[k]))
		parserDoor(string, vreturn)
        if packet.packet_type == PACKET.RADIO and packet.rorg == RORG.RPS:
	    string = ' '
	    for k in packet.parse_eep(0x02, 0x02):
		print('%s: %s' % (k, packet.parsed[k]))
		char = ('%s: %s' % (k, packet.parsed[k]))
		string = string + char
	    parserButton(string, vreturn)
	    del string
    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if communicator.is_alive():
    communicator.stop()
