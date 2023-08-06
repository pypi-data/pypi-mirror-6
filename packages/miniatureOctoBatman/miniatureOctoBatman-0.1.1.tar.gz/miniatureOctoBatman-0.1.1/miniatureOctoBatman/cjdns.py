#!/usr/bin/env python
from powerline.lib.threaded import ThreadedSegment, with_docstring
import cjdnsadmin

def peers(pl):
    """Returns the current number of peers connected"""
    try:
        cjdns = cjdnsadmin.connectWithAdminInfo()
    except:
        return None
    peercount = 0
    localpeers = 0
    page = 0
    more = True
    while more:
        table = cjdns.InterfaceController_peerStats(page)
        more = "more" in table
        page += 1
        for peer in table['peers']:
            if peer['state'] != "UNRESPONSIVE":
                if "user" in peer:
                    if peer['user'] == "Local Peers":
                        localpeers += 1
                    else:
                        peercount += 1
                else:
                    peercount += 1
    out = [
            {
                "contents": str(peercount),
                "highlight_group": ["cjdns:peers"]
            }
        ]
    if localpeers > 0:
        out.append({
            "contents": str(localpeers),
            "highlight_group": ["cjdns:localpeers"]
            })
    return out

class NodesSegment(ThreadedSegment):
    interval = 5

    def update(self, oldnodes):
        try:
            cjdns = cjdnsadmin.connectWithAdminInfo()
        except:
            return None

        more = True
        page = 0
        routes = 0
        nodes = []
        while more:
            table = cjdns.NodeStore_dumpTable(page)
            more = "more" in table
            routes += len(table['routingTable'])
            for route in table['routingTable']:
                if not route['ip'] in nodes:
                    nodes.append(route['ip'])
            page += 1
        return nodes

    def render(self, nodes, **kwags):
        return [{
            "contents": str(len(nodes)),
            "highlight_group": ["cjdns:nodes"]
            }]
nodes = with_docstring(NodesSegment(),
        """Displays the number of nodes in the cjdns routing table""")

if __name__ == "__main__":
    print("Hint: If you see this message and you don't know why, try reading the included README.md file")
    print(peers(None))
    print(nodes(None))
