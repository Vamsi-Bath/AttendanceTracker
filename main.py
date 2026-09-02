import argparse
import os
from attendance_system.camera import AttendanceTracker


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run attendance tracking.")
    parser.add_argument(
        "--camera",
        choices=("laptop", "raspberry-pi"),
        default=os.getenv("CAMERA_TYPE", "laptop"),
        help="Camera to use (default: laptop; can also be set with CAMERA_TYPE).",
    )
    parser.add_argument(
        "--camera-index",
        type=int,
        default=int(os.getenv("CAMERA_INDEX", "0")),
        help="Laptop webcam index (default: 0; ignored for raspberry-pi).",
    )
    args = parser.parse_args()
    room_id = os.getenv("ROOM_ID", "room-101")
    tracker = AttendanceTracker(camera_type=args.camera, camera_index=args.camera_index)
    try:
        tracker.run(room_id=room_id)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        tracker.stop()
