#!/usr/bin/env python
import graphitesend

g = graphitesend.init('event', graphite_server='localhost', graphite_port='49161')
g.send("event_name", "event_payload", ["hostname", "reboot"])

g.send_list(
    data=[
        {
            'metric': 'my event',
            'tags': 'hostname'
        },
        {
            'metric': 'my event 2',
            'tags': ['hostname2'],
        },
        
    ],
    tags = ['reboot']
)


g.send_dict(
    data={
        'my event': 'payload motherfucker',
        'my event2': 'payload motherfucker2',
        'my event3': {'value': 'payload motherfucker3', 'tags': 'awesometag'},
        'my event4': {'value': 'payload motherfucker4', 'tags': 'awesometag'},
    },
    tags = ['random dict events']
)
