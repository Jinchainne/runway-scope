import importlib.util
import json
import pathlib
import sys
import types
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "runway_scope.py"


class _Decorator:
    def __call__(self, value):
        return value


class _GenericList(list):
    @classmethod
    def __class_getitem__(cls, _item):
        return cls


class _GenericMap(dict):
    @classmethod
    def __class_getitem__(cls, _item):
        return cls


def _load_contract():
    gl = types.SimpleNamespace(
        Contract=object,
        public=types.SimpleNamespace(write=_Decorator(), view=_Decorator()),
        nondet=types.SimpleNamespace(
            web=types.SimpleNamespace(render=lambda _url, mode="text": "Official evidence " * 20),
            exec_prompt=lambda _prompt, response_format="json": {},
        ),
        vm=types.SimpleNamespace(
            UserError=RuntimeError,
            Result=object,
            Return=type("Return", (), {}),
            run_nondet_unsafe=lambda leader, _validator: leader(),
        ),
        message=types.SimpleNamespace(sender_address="0x" + "1" * 40),
    )
    stub = types.ModuleType("genlayer")
    stub.gl = gl
    stub.u256 = int
    stub.Address = str
    stub.DynArray = _GenericList
    stub.TreeMap = _GenericMap
    previous = sys.modules.get("genlayer")
    sys.modules["genlayer"] = stub
    try:
        spec = importlib.util.spec_from_file_location("runway_scope_behavior", CONTRACT_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if previous is None:
            del sys.modules["genlayer"]
        else:
            sys.modules["genlayer"] = previous


class RunwayScopeBehaviorTest(unittest.TestCase):
    def setUp(self):
        self.module = _load_contract()
        self.contract = object.__new__(self.module.RunwayScope)
        self.contract.windows = {}
        self.contract.window_ids = []

    def register(self, **overrides):
        values = {
            "window_id": "ATL-09L-001",
            "airport": "ATL",
            "runway": "09L",
            "operation": "ARRIVAL",
            "aircraft_category": "HEAVY",
            "window_start_utc": "2026-09-01T10:00Z",
            "window_end_utc": "2026-09-01T14:00Z",
            "notam_url": "https://notams.aim.faa.gov/notamSearch/nsapp.html",
            "nas_url": "https://nasstatus.faa.gov/list",
            "weather_url": "https://api.weather.gov/alerts/active",
        }
        values.update(overrides)
        self.contract.register_window(*values.values())

    def record(self):
        self.register()
        return json.loads(self.contract.windows["ATL-09L-001"])

    def test_registration_freezes_identity_and_official_sources(self):
        record = self.record()
        self.assertEqual(record["airport"], "ATL")
        self.assertEqual(record["runway"], "09L")
        self.assertEqual(record["state"], "REGISTERED")
        self.assertEqual(self.contract.list_window_ids(), ["ATL-09L-001"])

    def test_deceptive_or_wrong_source_hosts_are_rejected_without_mutation(self):
        for url in (
            "https://notams.aim.faa.gov.evil.example/notam",
            "https://user@notams.aim.faa.gov/notam",
            "http://notams.aim.faa.gov/notam",
        ):
            with self.assertRaisesRegex(RuntimeError, "allowlisted official HTTPS host"):
                self.register(notam_url=url)
            self.assertEqual(self.contract.windows, {})

        with self.assertRaisesRegex(RuntimeError, "malformed"):
            self.register(notam_url="https://notams.aim.faa.gov:invalid/notam")
        self.assertEqual(self.contract.windows, {})

    def test_window_is_bounded_and_calendar_valid(self):
        with self.assertRaisesRegex(RuntimeError, "no longer than 24 hours"):
            self.register(window_end_utc="2026-09-02T11:00Z")
        with self.assertRaisesRegex(RuntimeError, "invalid calendar"):
            self.register(window_start_utc="2026-13-01T10:00Z")

    def test_runway_designator_rejects_impossible_values(self):
        for runway in ("00", "37", "9L", "09X"):
            with self.assertRaisesRegex(RuntimeError, "valid designator"):
                self.register(runway=runway)

    def test_primary_notam_failure_is_unresolved(self):
        record = self.record()
        self.contract._render = lambda url: ("", False) if "notams" in url else ("Evidence " * 20, True)
        result = self.contract._assess(record)
        self.assertEqual(result["result"], "UNRESOLVED")
        self.assertEqual(result["source_bindings"]["notam"], "UNAVAILABLE")
        self.assertEqual(result["restriction_codes"], [])

    def test_bound_excerpt_must_be_literal_source_text(self):
        record = self.record()
        self.module.gl.nondet.exec_prompt = lambda *_args, **_kwargs: {
            "result": "APPLICABLE_RESTRICTION",
            "restriction_codes": ["RUNWAY_CLOSED"],
            "conditions": "",
            "reasoning": "The bound notice explicitly closes the registered runway window.",
            "source_bindings": {"notam": "BOUND", "nas": "UNBOUND", "weather": "UNBOUND"},
            "grounded_excerpts": {"notam": "invented excerpt", "nas": "", "weather": ""},
        }
        with self.assertRaisesRegex(RuntimeError, "literal source substring"):
            self.contract._assess(record)

    def test_no_restriction_requires_bound_primary_notam(self):
        record = self.record()
        self.module.gl.nondet.exec_prompt = lambda *_args, **_kwargs: {
            "result": "NO_APPLICABLE_RESTRICTION",
            "restriction_codes": [],
            "conditions": "",
            "reasoning": "No notice in the supplied evidence applies to this operation.",
            "source_bindings": {"notam": "UNBOUND", "nas": "UNBOUND", "weather": "UNBOUND"},
            "grounded_excerpts": {"notam": "", "nas": "", "weather": ""},
        }
        with self.assertRaisesRegex(RuntimeError, "requires a bound NOTAM"):
            self.contract._assess(record)

    def test_conditional_result_requires_conditions(self):
        record = self.record()
        excerpt = "Official evidence"
        self.module.gl.nondet.exec_prompt = lambda *_args, **_kwargs: {
            "result": "CONDITIONAL_OPERATION",
            "restriction_codes": ["AIRCRAFT_LIMIT"],
            "conditions": "",
            "reasoning": "The notice imposes an aircraft-category operational condition.",
            "source_bindings": {"notam": "BOUND", "nas": "UNBOUND", "weather": "UNBOUND"},
            "grounded_excerpts": {"notam": excerpt, "nas": "", "weather": ""},
        }
        with self.assertRaisesRegex(RuntimeError, "requires concrete conditions"):
            self.contract._assess(record)

    def test_consensus_result_materially_updates_state_and_provenance(self):
        record = self.record()
        result = {
            "result": "APPLICABLE_RESTRICTION",
            "restriction_codes": ["RUNWAY_CLOSED"],
            "conditions": "",
            "reasoning": "The bound FAA notice closes the requested runway during the frozen window.",
            "source_bindings": {"notam": "BOUND", "nas": "UNBOUND", "weather": "UNBOUND"},
            "snapshot_digests": {"notam": "a" * 64, "nas": "b" * 64, "weather": "c" * 64},
            "grounded_excerpts": {"notam": "Runway 09L closed", "nas": "", "weather": ""},
        }
        self.contract._assess = lambda _record: result
        self.assertEqual(self.contract.assess_window("ATL-09L-001"), "APPLICABLE_RESTRICTION")
        stored = json.loads(self.contract.windows["ATL-09L-001"])
        self.assertEqual(stored["state"], "APPLICABLE_RESTRICTION")
        self.assertEqual(stored["restriction_codes"], ["RUNWAY_CLOSED"])
        self.assertEqual(stored["snapshot_digests"]["notam"], "a" * 64)
        with self.assertRaisesRegex(RuntimeError, "not eligible"):
            self.contract.assess_window("ATL-09L-001")


if __name__ == "__main__":
    unittest.main()
