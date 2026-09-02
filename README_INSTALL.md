# Meeting-room attendance tracker

This application uses a laptop webcam or Raspberry Pi camera to detect people in a meeting room. It does **not** identify people. While a booked meeting is active, it counts the visible people, saves periodic local observations, and sends one attendance report to Power Automate when that meeting ends.

## How it works

```text
Camera -> Python person detection -> local meeting observations
                 ^                         |
                 |                         v
        Power Automate meeting list   final attendance report
```

- Every camera frame: detects and tracks visible people.
- Every 15 seconds during an active meeting: saves an occupancy observation locally in `meeting_data`.
- Every 60 seconds: fetches the latest meeting bookings from Power Automate and updates `mock_meetings.json`.
- When the active meeting ends: sends a final attendance report to Power Automate.

The camera continues counting throughout. The 60-second interval only refreshes the meeting schedule.

## Files needed to run

- `main.py` - the application entry point.
- `attendance_system` - application code.
- `yolo11n.onnx` - AI model used by `main.py`.
- `Scripts`, `Lib`, `Include`, and `pyvenv.cfg` - the included Python environment and installed packages.
- `mock_meetings.json` and `meeting_data` - local meeting cache and recorded observations.

## What the Power Automate owner must create

Create **two separate Power Automate HTTP-trigger flows**, with different URLs.

### 1. Meeting Bookings flow - GET

This flow supplies the current and upcoming meeting schedule.

1. Use **When an HTTP request is received** as the trigger and configure it to accept **GET**.
2. Read the meeting data produced by the PDF-processing worker (for example from SharePoint, Excel, Dataverse, or a stored JSON file).
3. Return a **Response** with status code `200` and `Content-Type: application/json`.
4. Return the full list of current and upcoming meetings, not just one new meeting.

The response body must be a JSON array like this:

```json
[
  {
    "meetingId": "meeting-003",
    "roomId": "room-101",
    "startTime": "2026-08-13T10:00:00+01:00",
    "endTime": "2026-08-13T11:00:00+01:00",
    "roomCapacity": 12
  }
]
```

Required fields are `meetingId`, `roomId`, `startTime`, and `endTime`. Times must be ISO-8601 values with a time zone, such as `2026-08-13T10:00:00+01:00` or `2026-08-13T09:00:00Z`.

Python removes ended meetings from the local cache. If a locally stored meeting is still active, it keeps that meeting and adds/updates the current and upcoming meetings returned by the flow.

### 2. Attendance Report flow - POST

This flow receives a final report after each meeting.

1. Use **When an HTTP request is received** as the trigger and configure it to accept **POST**.
2. Accept a JSON request body.
3. Store, email, or process the report as needed.
4. Return status `200`, `201`, or `202` to acknowledge receipt.

The report contains fields including:

```text
meetingId, roomId, meanOccupancy, peakOccupancy, medianOccupancy,
observationCount, durationMinutes, roomCapacity, capacityUtilisation,
chartData, chartImageBase64
```

`chartImageBase64` is a base64-encoded PNG chart of occupancy over the meeting.

Keep both flow URLs private. Their `sig` query value is an access secret; regenerate the URL in Power Automate if it is exposed.

## Run on a laptop

Open PowerShell in this project folder and set the two URLs for the current PowerShell window:

```powershell
$env:MEETING_BOOKINGS_API_URL = "PASTE_THE_GET_MEETING_BOOKINGS_FLOW_URL_HERE"
$env:ATTENDANCE_REPORT_API_URL = "PASTE_THE_POST_ATTENDANCE_REPORT_FLOW_URL_HERE"
.\Scripts\python.exe main.py --camera laptop
```

For another webcam, change the index:

```powershell
.\Scripts\python.exe main.py --camera laptop --camera-index 1
```

Press `Q` or `Esc` in the camera window to stop the tracker.

If the Power Automate URLs are not set or are temporarily unavailable, the camera app still runs and uses the last saved `mock_meetings.json`; it cannot retrieve new bookings or upload the final report until the connection is available.

## Run on Raspberry Pi

Create a Linux Python environment on the Pi, install the dependencies and Picamera2, set the same two environment variables, then run:

```bash
export MEETING_BOOKINGS_API_URL="PASTE_THE_GET_MEETING_BOOKINGS_FLOW_URL_HERE"
export ATTENDANCE_REPORT_API_URL="PASTE_THE_POST_ATTENDANCE_REPORT_FLOW_URL_HERE"
python main.py --camera raspberry-pi
```

The Raspberry Pi needs a compatible Python environment and the `picamera2` package; this Windows virtual environment cannot simply be copied to the Pi.

## Install/reinstall dependencies

The project includes a ready-to-use Windows Python environment. If it must be rebuilt, install Python 3.10, create a new virtual environment, activate it, and run:

```powershell
python -m pip install -r requirements.txt
```
