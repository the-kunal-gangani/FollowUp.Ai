import math
import cv2
import numpy as np

GESTURE_SHAPES = {
    (0, 0, 0, 0, 0): "box",
    (1, 1, 1, 1, 1): "star",
    (1, 0, 0, 0, 1): "heart",
    (0, 1, 0, 0, 1): "lightning",
    (0, 1, 1, 1, 0): "batman",
}


def match_gesture(fingers):
    if not fingers or len(fingers) != 5:
        return None
    return GESTURE_SHAPES.get(tuple(fingers))


def draw_cartoon_shape(frame, shape_name, center, size):
    if shape_name == "box":
        _draw_box(frame, center, size)
    elif shape_name == "star":
        _draw_star(frame, center, size)
    elif shape_name == "heart":
        _draw_heart(frame, center, size)
    elif shape_name == "lightning":
        _draw_lightning(frame, center, size)


def _draw_box(frame, center, size):
    cx, cy = center
    half = size // 2

    top_left = (cx - half, cy - half)
    bottom_right = (cx + half, cy + half)

    cv2.rectangle(frame, top_left, bottom_right, (60, 180, 255), -1, cv2.LINE_AA)
    cv2.rectangle(frame, top_left, bottom_right, (20, 90, 160), 4, cv2.LINE_AA)

    eye_offset_x = half // 3
    eye_y = cy - half // 4
    eye_radius = max(size // 14, 3)

    cv2.circle(frame, (cx - eye_offset_x, eye_y), eye_radius, (20, 20, 20), -1, cv2.LINE_AA)
    cv2.circle(frame, (cx + eye_offset_x, eye_y), eye_radius, (20, 20, 20), -1, cv2.LINE_AA)

    mouth_y = cy + half // 3
    cv2.ellipse(
        frame, (cx, mouth_y), (half // 3, half // 5), 0, 0, 180, (20, 20, 20), 3, cv2.LINE_AA
    )


def _draw_star(frame, center, size):
    cx, cy = center
    outer_r = size // 2
    inner_r = outer_r // 2
    points = []

    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        radius = outer_r if i % 2 == 0 else inner_r
        x = int(cx + radius * math.cos(angle))
        y = int(cy - radius * math.sin(angle))
        points.append([x, y])

    star_points = np.array(points, dtype=np.int32)
    cv2.fillPoly(frame, [star_points], (0, 220, 255), lineType=cv2.LINE_AA)
    cv2.polylines(frame, [star_points], True, (0, 160, 200), 3, cv2.LINE_AA)


def _draw_heart(frame, center, size):
    cx, cy = center
    scale = size / 200.0

    t = np.linspace(0, 2 * math.pi, 100)
    x = 16 * (np.sin(t) ** 3)
    y = -(13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))

    x = (x * scale * 6 + cx).astype(int)
    y = (y * scale * 6 + cy).astype(int)

    pts = np.stack([x, y], axis=1)
    cv2.fillPoly(frame, [pts], (100, 60, 255), lineType=cv2.LINE_AA)
    cv2.polylines(frame, [pts], True, (60, 20, 200), 3, cv2.LINE_AA)


def _draw_lightning(frame, center, size):
    cx, cy = center
    s = size / 100.0

    raw_points = [
        (20, -50), (-6, 6), (12, 6), (-20, 50), (10, -2), (-8, -2),
    ]

    points = np.array(
        [[int(cx + px * s), int(cy + py * s)] for px, py in raw_points],
        dtype=np.int32
    )

    cv2.fillPoly(frame, [points], (0, 230, 255), lineType=cv2.LINE_AA)
    cv2.polylines(frame, [points], True, (0, 150, 200), 3, cv2.LINE_AA)