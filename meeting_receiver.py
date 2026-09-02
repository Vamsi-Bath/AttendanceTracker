import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from cv2 import error

WORKSPACE_ROOT = Path(__file__).resolve().parent
MEETINGS_PATH = WORKSPACE_ROOT / "mock_meetings.json"
HOST = "0.0.0.0"
PORT = 5000

class MeetingReceiverHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send_json({"status": "ok"})
            return
        if parsed.path == "/meetings":
            payload = {key: values[0] if len(values) == 1 else values for key, values in parse_qs(parsed.query).items()}
            if not payload:
                self._send_json({"error": "no query parameters supplied"}, status=400)
                return
            self._store_meeting(payload)
            return
        self._send_json({"error": "not found"}, status=404) 

    def _store_meeting(self, payload: dict) -> None:
        if not isinstance(payload, dict):
            self._send_json({"error": "expected a JSON object"}, status=400)
            return

        required_fields = {"meetingId", "roomId", "startTime", "endTime"}
        missing = sorted(required_fields - set(payload.keys()))
        if missing:
            self._send_json({"error": f"missing fields: {', '.join(missing)}"}, status=400)
            return
        
        existing = []
        if MEETINGS_PATH.exists():
            try:
                existing = json.loads(MEETINGS_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = []

        if not isinstance(existing, list):
            existing = []

        existing = [item for item in existing if isinstance(item, dict)]
        if not any(item.get("meetingId") == payload.get("meetingId") for item in existing):
            existing.append(payload)
            MEETINGS_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")

        self._send_json({"status": "received", "meetingId": payload.get("meetingId")})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/meetings":
            self._send_json({"error": "not found"}, status=404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length else b"{}"

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json({"error": "invalid json"}, status=400)
            return

        if not isinstance(payload, dict):
            self._send_json({"error": "expected a JSON object"}, status=400)
            return

        self._store_meeting(payload)


def run() -> None:
    server = ThreadingHTTPServer((HOST, PORT), MeetingReceiverHandler)
    print(f"Listening on http://{HOST}:{PORT}/meetings")
    server.serve_forever()


if __name__ == "__main__":
    run()
