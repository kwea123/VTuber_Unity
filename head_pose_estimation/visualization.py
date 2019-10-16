import cv2

def draw_box(image, boxes, box_color=(255, 255, 255)):
    """Draw square boxes on image"""
    for box in boxes:
        cv2.rectangle(image,
                      (box[0], box[1]),
                      (box[2], box[3]), box_color, 3)

def draw_marks(image, marks, color=(255, 255, 255)):
    """Draw mark points on image"""
    for mark in marks:
        cv2.circle(image, (int(mark[0]), int(
            mark[1])), 1, color, -1, cv2.LINE_AA)

def draw_iris(frame, x, y):
    cv2.line(frame, (x - 5, y), (x + 5, y), (0, 0, 255))
    cv2.line(frame, (x, y - 5), (x, y + 5), (0, 0, 255))


def draw_FPS(frame, FPS):
    cv2.putText(frame, "FPS: %d"%FPS, (40, 40), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)