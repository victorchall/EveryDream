import argparse
from pathlib import Path
import cv2

def get_parser(**parser_kwargs):
    parser = argparse.ArgumentParser(**parser_kwargs)
    parser.add_argument(
        "--vid_dir",
        required=True,
        type=str,
        nargs="?",
        const=True,
        help="directory with videos to extract frames",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        nargs="?",
        const=True,
        help="directory to put extracted images",
    )
    parser.add_argument(
        "--format",
        type=str,
        nargs="?",
        const=True,
        default="png",
        choices=["png", "jpg"],
        help="image file format of the extracted frames",
    )
    parser.add_argument(
        "--interval",
        type=int,
        nargs="?",
        const=True,
        default=10,
        help="number of seconds between frame captures",
    )
    return parser
    
def get_videos(input_dir):
    for f in input_dir.iterdir():
        file_path = Path(f)
        if file_path.suffix in [".mp4", ".avi", ".mov", ".mpeg", ".mpg", ".mkv"]:
            yield file_path

def capture_frames(input_dir, output_dir):
    print (f'Capturing video frames in {opt.interval} second intervals.\n')

    for video_path in get_videos(input_dir):
        print(f'Extracting {video_path}')
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f'Could not open video')
            continue

        output = output_dir / video_path.stem
        output.mkdir(exist_ok=True, parents=True)

        current_frame = 0
        count = 0
        fps = cap.get(cv2.CAP_PROP_FPS)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                count_str = str(count).zfill(4)
                cv2.imwrite(str(output / f'frame_{count_str}.{opt.format}'), frame)
                current_frame += fps * opt.interval
                cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
                count += 1
            else:
                cap.release()
                break

    print(f'\nFinished extracting frames to {output_dir}\n')

if __name__ == "__main__":
    parser = get_parser()
    opt = parser.parse_args()

    if (not Path(opt.vid_dir).exists):
        print("Video directory does not exist.")
        exit(1)

    if (opt.out_dir is None):
        output = Path(opt.vid_dir) / "output"
        print(f"No output directory specified, using default: {output}")
    else:
        output = Path(opt.out_dir)
    capture_frames(Path(opt.vid_dir), output)
