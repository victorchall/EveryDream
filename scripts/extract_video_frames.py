# extract frames from videos every n seconds

import cv2
import os
from pathlib import Path

video_base_path = Path('../movies')
frames_root_path = Path('../frames')

interval = 30 #seconds

if not video_base_path.exists():
    print('Video base path does not exist')
    exit(1)

if not frames_root_path.exists():
    os.mkdir(frames_root_path)

# loop over all files in the base path
for video_path in video_base_path.iterdir():
    frames_folder = frames_root_path / f'frames-{video_path.stem}'
    if not frames_folder.exists():
        os.mkdir(frames_folder)

    print(f'Loading video {video_path}')
    print(f'Saving frames to {frames_folder}')

    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    count = 0

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(str(frames_folder / f'frame{count}.jpg'), frame)
            count += fps * interval
            cap.set(cv2.CAP_PROP_POS_FRAMES, count)
        else:
            cap.release()
            break

print('done')