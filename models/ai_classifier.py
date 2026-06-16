import logging
import os

from ultralytics import YOLO

logger = logging.getLogger(__name__)

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "best.pt")

_model = None
_load_error = None

try:
    _model = YOLO(_MODEL_PATH)
except Exception as exc:
    _load_error = exc
    logger.warning("Failed to load YOLO model from %s: %s", _MODEL_PATH, exc)


def detect_issue(image_path: str) -> dict:
    """
    Detect the civic issue category from an uploaded image.

    Runs YOLO inference on the image. If at least one pothole is detected,
    routes the issue to the Road Department; otherwise to Waste Management.
    """
    default_result = {"category": "garbage", "dept_id": 2}

    if _model is None:
        logger.warning(
            "YOLO model unavailable; defaulting to garbage classification."
        )
        return default_result

    try:
        results = _model(image_path, verbose=False)

        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue

            class_names = result.names
            for box in result.boxes:
                class_id = int(box.cls.item())
                class_name = class_names.get(class_id, "")
                if class_name.lower() == "pothole":
                    return {"category": "pothole", "dept_id": 1}

    except Exception as exc:
        logger.warning("Issue detection failed for %s: %s", image_path, exc)

    return default_result
