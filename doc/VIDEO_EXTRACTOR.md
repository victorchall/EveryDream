# Video frame extractor

## Usage

Place video files into the top level of a directory.

Execute `python scripts/extract_video_frames.py --vid_dir path/to/videos` to iterate over all files, extract frames at regular intervals, and save full resolution frame images to disk.

This tool supports a wide variety of input video containers and codecs (via OpenCV), and exports jpg or png files.

## Arguments

### --vid_dir

Required directory path for input video files.

### --out_dir

Optional directory path in which to store extracted frame images. Defaults to a directory named 'output' that will be created inside the specified videos directory.

### --format

The format for image files saved to disk. Defaults to `png`, or optionally `jpg`.

### --interval

The number of seconds between frame captures. Defaults to 10 seconds.
