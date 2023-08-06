#!/usr/bin/env python
try:
    import apt
except ImportError:
    pass

from powerline.lib.threaded import ThreadedSegment, with_docstring


class AptUpgradesSegment(ThreadedSegment):
    interval = 300

    def update(self, oldthing):
        upgrades = 0
        for pkg in apt.Cache():
            if pkg.is_upgradable:
                upgrades += 1
        return upgrades
    def render(self, upgrades, **kwargs):
        if upgrades > 0:
            return [{
                "contents": "%i packages can be upgraded" % upgrades,
                "highlight_groups": ["packages:upgrades", "packages"]
                }]
        else:
            return None

AptUpgrades = with_docstring(AptUpgradesSegment(),
        """Displays the number of upgradable packages""")
