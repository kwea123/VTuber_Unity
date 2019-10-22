from argparse import ArgumentParser
from multiprocessing import Process, Queue

import cv2
import numpy as np
import time
import socket
from collections import deque

from head_pose_estimation.pose_estimator import PoseEstimator
from head_pose_estimation.stabilizer import Stabilizer
from head_pose_estimation.visualization import *
from head_pose_estimation.misc import *

import numpy as np

def get_face(detector, img_queue, box_queue, cpu=False):
    if cpu:
        while True:
            image = img_queue.get()
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            try:
                box = detector(image)[0]
                x1 = box.left()
                y1 = box.top()
                x2 = box.right()
                y2 = box.bottom()
                box_queue.put([x1, y1, x2, y2])
            except:
                box_queue.put(None)
    else:
        while True:
            image = img_queue.get()
            box = detector.extract_cnn_facebox(image)
            box_queue.put(box)

def main():
    # Setup face detection models
    if args.cpu: # use dlib to do face detection and facial landmark detection
        import dlib 
        face_detector = dlib.get_frontal_face_detector()
        dlib_model_path = 'head_pose_estimation/assets/shape_predictor_68_face_landmarks.dat'
        predictor = dlib.shape_predictor(dlib_model_path)
    else: # use better models on GPU
        import face_alignment, dlib
        fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, use_onnx=True, 
                                          flip_input=False)

    cap = cv2.VideoCapture(args.cam+cv2.CAP_DSHOW) # CAP_DSHOW is required on my PC to get 30 FPS
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    _, sample_frame = cap.read()

    # Setup process and queues for multiprocessing.
    # img_queue = Queue()
    # box_queue = Queue()
    # img_queue.put(sample_frame)
    # box_process = Process(target=get_face, args=(
    #     face_detector, img_queue, box_queue, True,))
    # box_process.start()

    # Introduce pose estimator to solve pose. Get one frame to setup the
    # estimator according to the image size.
    pose_estimator = PoseEstimator(img_size=sample_frame.shape[:2])

    # Introduce scalar stabilizers for pose.
    pose_stabilizers = [Stabilizer(
                        state_num=2,
                        measure_num=1,
                        cov_process=0.01,
                        cov_measure=0.1) for _ in range(8)]

    if args.connect:
        address = ('127.0.0.1', 5066)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(address)

    ts = []
    frame_count = 0
    prev_boxes = deque(maxlen=5)
    prev_marks = deque(maxlen=5)

    while True:
        _, frame = cap.read()
        frame = cv2.flip(frame, 2)
        frame_count += 1
        if args.connect and frame_count > 60: # send information to unity
            msg = '%.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f'% \
                  (roll, pitch, yaw, min_ear, mar, mdst, steady_pose[6], steady_pose[7])
            s.send(bytes(msg, "utf-8"))

        t = time.time()

        # Pose estimation by 3 steps:
        # 1. detect face;
        # 2. detect landmarks;
        # 3. estimate pose

        # img_queue.put(frame)
        # facebox = box_queue.get()
        if frame_count % 2 == 1: # do face detection every odd frame
            frame_ = cv2.resize(frame, None, fx=0.5, fy=0.5)
            facebox = fa.face_detector.detect_from_image(frame_)[0]
            if facebox is not None:
                facebox = (2*facebox[:4]).astype(int)
        elif len(prev_boxes) > 1: # use a linear movement assumption
            facebox = prev_boxes[-1] + np.mean(np.diff(np.array(prev_boxes), axis=0), axis=0)[0]
            facebox = facebox.astype(int)
        prev_boxes.append(facebox)

        if facebox is not None:
            # Do face detection, facial landmark detection and iris detection.
            if args.cpu:
                face = dlib.rectangle(left=facebox[0], top=facebox[1], 
                                      right=facebox[2], bottom=facebox[3])
                marks = shape_to_np(predictor(frame, face))
            else:
                if frame_count == 1 or frame_count % 2 == 0: # do landmark detection on first frame
                                                             # or every even frame
                    face_img = frame[facebox[1]: facebox[3], facebox[0]: facebox[2]]
                    marks = fa.get_landmarks(face_img[:,:,::-1], 
                            detected_faces=[(0, 0, facebox[2]-facebox[0], facebox[3]-facebox[1])])
                    marks = marks[-1]
                    marks[:, 0] += facebox[0]
                    marks[:, 1] += facebox[1]
                elif len(prev_marks) > 1: # use a linear movement assumption
                    marks = prev_marks[-1] + np.mean(np.diff(np.array(prev_marks), axis=0), axis=0)
                prev_marks.append(marks)

            x_l, y_l, ll, lu = detect_iris(frame, marks, "left")
            x_r, y_r, rl, ru = detect_iris(frame, marks, "right")

            # Try pose estimation with 68 points.
            R, T = pose_estimator.solve_pose_by_68_points(marks)
            pose = list(R) + list(T)
            # Add iris positions to stabilize.
            pose+= [(ll+rl)/2.0, (lu+ru)/2.0]

            # Stabilize the pose.
            steady_pose = []
            pose_np = np.array(pose).flatten()
            for value, ps_stb in zip(pose_np, pose_stabilizers):
                ps_stb.update([value])
                steady_pose.append(ps_stb.state[0])

            if args.debug:

                # show iris.
                if x_l > 0 and y_l > 0:
                    draw_iris(frame, x_l, y_l)
                if x_r > 0 and y_r > 0:
                    draw_iris(frame, x_r, y_r)

                # show face landmarks.
                draw_marks(frame, marks, color=(0, 255, 0))

                # show facebox.
                draw_box(frame, [facebox])

                # draw stable pose annotation on frame.
                pose_estimator.draw_annotation_box(
                    frame, np.expand_dims(steady_pose[:3],0), np.expand_dims(steady_pose[3:6],0), 
                    color=(128, 255, 128))

                # draw head axes on frame.
                pose_estimator.draw_axes(frame, np.expand_dims(steady_pose[:3],0), 
                                         np.expand_dims(steady_pose[3:6],0))

            roll = np.clip(-(180+np.degrees(steady_pose[2])), -50, 50)
            pitch = np.clip(-(np.degrees(steady_pose[1]))-15, -40, 40)
            yaw = np.clip(-(np.degrees(steady_pose[0])), -50, 50)
            min_ear = min(eye_aspect_ratio(marks[36:42]), eye_aspect_ratio(marks[42:48]))
            mar = mouth_aspect_ration(marks[60:68])
            mdst = mouth_distance(marks[60:68])/(facebox[2]-facebox[0])
            

        dt = time.time()-t
        ts += [dt]
        FPS = int(1/(np.mean(ts[-10:])+1e-6))
        print('\r', '%.3f'%dt, end=' ')

        if args.debug:
            draw_FPS(frame, FPS)
            cv2.imshow("face", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): # press q to exit.
                break

    # Clean up the multiprocessing process.
    # box_process.terminate()
    # box_process.join()
    cap.release()
    if args.connect:
        s.close()
    if args.debug:
        cv2.destroyAllWindows()
    print('%.3f'%np.mean(ts))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--cam", type=int, 
                        help="specify the camera number if you have multiple cameras",
                        default=0)
    parser.add_argument("--cpu", action="store_true", 
                        help="use cpu to do face detection and facial landmark detection",
                        default=False)
    parser.add_argument("--debug", action="store_true", 
                        help="show camera image to debug (need to uncomment to show results)",
                        default=False)
    parser.add_argument("--connect", action="store_true", 
                        help="connect to unity character",
                        default=False)
    args = parser.parse_args()
    main()