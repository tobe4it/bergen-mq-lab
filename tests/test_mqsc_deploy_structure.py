"""Offline structural checks for the independent MQSC deployment adapter."""
from pathlib import Path
import unittest

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(yaml is None, "PyYAML unavailable")
class MqscDeployStructureTests(unittest.TestCase):
    def load(self, path):
        with (ROOT / path).open(encoding="utf-8") as stream:
            documents = list(yaml.safe_load_all(stream))
        self.assertEqual(len(documents), 1, path)
        return documents[0]

    def test_all_yaml_is_single_document(self):
        paths = [
            "ansible/playbooks/mqsc-deploy.yml",
            "ansible/roles/mqsc_deploy/defaults/main.yml",
            "ansible/roles/mqsc_deploy/tasks/main.yml",
            "ansible/roles/mqsc_deploy/tasks/posix.yml",
            "ansible/roles/mqsc_deploy/tasks/windows.yml",
            "ansible/examples/mqsc-inventory.yml",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.load(path)

    def test_apply_requires_explicit_confirmation(self):
        tasks = self.load("ansible/roles/mqsc_deploy/tasks/main.yml")
        gate = next(t for t in tasks if "ansible.builtin.assert" in t)
        conditions = gate["ansible.builtin.assert"]["that"]
        self.assertTrue(any("mqsc_confirm_apply" in c for c in conditions))
        self.assertTrue(any("ansible_check_mode" in c for c in conditions))

    def test_both_platforms_validate_before_apply(self):
        for platform in ("posix", "windows"):
            tasks = self.load(f"ansible/roles/mqsc_deploy/tasks/{platform}.yml")
            block = next(t["block"] for t in tasks if "block" in t)
            validate_index = next(i for i, t in enumerate(block) if "Validate MQSC syntax" in t["name"])
            apply_index = next(i for i, t in enumerate(block) if "Apply MQSC" in t["name"])
            self.assertLess(validate_index, apply_index)
            self.assertIn("mqsc_validation_ok | bool", block[apply_index]["when"])

    def test_audit_is_default(self):
        defaults = self.load("ansible/roles/mqsc_deploy/defaults/main.yml")
        self.assertEqual(defaults["mqsc_mode"], "audit")
        self.assertFalse(defaults["mqsc_confirm_apply"])


if __name__ == "__main__":
    unittest.main()
