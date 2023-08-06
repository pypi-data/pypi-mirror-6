import forthrast.api as forthrast
import glob

# This takes a list of frames that were meant to be played at 30 fps and then
# creates a new sequence that is meant to be at 60 fps.

if not os.path.isdir("rescaled"):
    os.mkdir("rescaled")

fns = list(sorted(glob.glob("graytest5_moon/snap*.png")))

ff = forthrast.FrameTimeline.from_filenames(fns, fps = 30)
ff.scale_fps(60, template = "rescaled/frame_%(frame)06i.png")
