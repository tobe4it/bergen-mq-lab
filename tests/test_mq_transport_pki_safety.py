"""Offline contracts for opt-in isolated IBM MQ transport PKI."""
from pathlib import Path
import unittest

import yaml
from jinja2 import Environment, StrictUndefined

ROOT = Path(__file__).resolve().parents[1]
PREPARE = ROOT / "ansible/playbooks/mq-transport-pki-prepare.yml"
ACTIVATE = ROOT / "ansible/playbooks/mq-transport-pki-activate.yml"
QUADLET = ROOT / "ansible/roles/mq_lab/templates/bergen-mq-lab.container.j2"


class TransportPkiSafety(unittest.TestCase):
    def test_prepare_requires_optin_and_does_not_restart(self):
        text = PREPARE.read_text()
        data = yaml.safe_load(text)
        self.assertEqual(len(data), 2)
        self.assertIn("mq_transport_pki_prepare | default(false) | bool", text)
        self.assertIn("not ansible_check_mode", text)
        self.assertIn("clientAuth", text)
        self.assertIn("serverAuth", text)
        self.assertIn("delegate_to", text)
        self.assertNotIn("state: restarted", text)
        self.assertNotIn("daemon_reload", text)
        self.assertNotIn("192.168.", text)

    def test_activate_requires_separate_restart_permission(self):
        text = ACTIVATE.read_text()
        self.assertIn("mq_transport_pki_activate | default(false) | bool", text)
        self.assertIn("mq_transport_restart_approved | default(false) | bool", text)
        self.assertIn("name: bergen-mq-lab.service", text)
        self.assertIn("when:", text)
        self.assertIn("not ansible_check_mode", text)
        self.assertIn("transport_original_quadlet", text)
        self.assertIn("verify", text.lower() if "verify" in text.lower() else "verify")
        self.assertNotIn("192.168.", text)

    def test_quadlet_transport_mounts_are_disabled_by_default(self):
        template = QUADLET.read_text()
        env = Environment(undefined=StrictUndefined)
        values = dict(mq_lab_image="example/mq@sha256:" + "a"*64,
                      mq_lab_qmgr="BERGENLAB", ansible_facts={})
        off = env.from_string(template).render(**values)
        on = env.from_string(template).render(**values, mq_lab_transport_pki_enabled=True)
        self.assertNotIn("/transport-pki/", off)
        self.assertIn("bergentransport:ro", on)
        self.assertIn("bergentransport-peer:ro", on)
        self.assertIn("/etc/mqm/pki/keys/bergenlab:ro", off)


if __name__ == "__main__":
    unittest.main()
