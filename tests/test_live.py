"""Test cửa sổ chơi trực tiếp (chonoi.live). Chỉ dành cho starter Python: nhóm đổi ngôn ngữ thì xóa file này."""

import json
import time
import unittest
import urllib.error
import urllib.request
from decimal import Decimal

from chonoi.contract import load_contract
from chonoi.live import LiveGame, LiveServer


def _get(url):
    with urllib.request.urlopen(url, timeout=5) as r:
        return r.status, r.read()


def _post(url, obj):
    req = urllib.request.Request(url, data=json.dumps(obj).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        e.close()
        return e.code


class LiveServerTest(unittest.TestCase):
    def test_state_input_and_clean_stop(self):
        tuning = load_contract()["tuning"]
        server = LiveServer(LiveGame("gather", tuning, {}, 1), port=0)  # cổng ngẫu nhiên
        server.start()
        try:
            base = f"http://127.0.0.1:{server.port}"
            code, body = _get(base + "/state")
            self.assertEqual(code, 200)
            st = json.loads(body)
            self.assertIn("tick", st)
            self.assertEqual(st["mode"], "gather")
            self.assertEqual(st["player"]["pos"], [2, 0])
            self.assertEqual(_post(base + "/input", {"move": [1, 0], "interact": False, "catch": False}), 200)
            self.assertEqual(_post(base + "/input", {"move": [5, 0]}), 400)
            code, html = _get(base + "/")
            self.assertEqual(code, 200)
            self.assertIn(b"<canvas", html)
            deadline = time.time() + 3
            while time.time() < deadline:
                st2 = json.loads(_get(base + "/state")[1])
                if st2["tick"] > st["tick"] + 3 and st2["player"]["pos"][0] > st["player"]["pos"][0]:
                    break
                time.sleep(0.05)
            self.assertGreater(st2["tick"], st["tick"], "mô phỏng phải chạy nền")
            self.assertGreater(st2["player"]["pos"][0], st["player"]["pos"][0], "input phải tác động tới sim")
        finally:
            server.stop()
        self.assertFalse(server.game._thread.is_alive())
        self.assertFalse(server._thread.is_alive())

    def test_live_day_keeps_exact_spoil_status_when_float_rounds_to_30(self):
        tuning = load_contract()["tuning"]
        scenario = {"gather": {"time_left_ticks": 1, "random_fish": False, "monsters": [],
                               "hold": [
                                   {"id": "I1", "kind": "ca_loc", "fresh": Decimal("30.008333333333333333")},
                                   {"id": "I2", "kind": "bong_sung", "fresh": Decimal("30.00834")},
                               ]}}
        server = LiveServer(LiveGame("day", tuning, scenario, 17, days=1), port=0)
        server.start()
        try:
            base = server.url.rstrip("/")
            self.assertEqual(_post(base + "/restart", {}), 200)
            opening = json.loads(_get(base + "/state")[1], parse_float=Decimal)
            self.assertEqual(opening["meta"]["spoiled_ids"], [])
            self.assertEqual(_post(base + "/input", {"interact": True}), 200)
            self.assertEqual(_post(base + "/input", {"interact": False}), 200)
            evening = opening
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline and evening["ui"]["screen"] != "evening_intro":
                evening = json.loads(_get(base + "/state")[1], parse_float=Decimal)
                time.sleep(0.01)
            self.assertEqual((evening["ui"]["screen"], evening["phase_tick"]), ("evening_intro", 0))
            ended = next(event for event in evening["events"] if event["name"] == "gather_end")
            self.assertEqual(evening["stock"], ended["data"]["inventory"]["items"])
            self.assertLess(evening["stock"][0]["fresh"], Decimal(30))
            self.assertEqual(float(evening["stock"][0]["fresh"]), 30.0)
            self.assertGreater(evening["stock"][1]["fresh"], Decimal(30))
            self.assertEqual(evening["meta"]["spoiled_ids"], ["I1"])
        finally:
            server.stop()


if __name__ == "__main__":
    unittest.main()
