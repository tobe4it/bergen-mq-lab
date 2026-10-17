"""Safety regression of the peer-QMgr firewall: no default listener opening."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
ROLE = ROOT / "ansible/roles/mq_lab"

class PeerFirewallContracts(unittest.TestCase):
    def test_closed_by_default_and_exact_source(self):
        defaults = yaml.safe_load((ROLE / "defaults/main.yml").read_text())
        self.assertEqual(defaults["mq_lab_peer_cidrs"], [])
        text = (ROLE / "tasks/firewall.yml").read_text()
        steps = yaml.safe_load(text)
        names = [t.get("name", "") for t in steps]
        self.assertIn("Require canonical exact peer QMgr source addresses", names)
        self.assertIn("Add reviewed peer QMgr sources for MQ listener only", names)
        source = next(x for x in steps if x.get("name","").startswith("Add reviewed peer"))
        self.assertEqual(source["loop"], "{{ mq_lab_peer_cidrs }}")
        self.assertIn("1414", str(source))
        self.assertNotIn('port port=\\"9443\\"', str(source))
        self.assertIn("prefixlen == 32", text)
        self.assertNotIn("192.168.", text)

if __name__ == "__main__":
    unittest.main()
