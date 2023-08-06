import numpy as np
import numbers
from PIL import Image
from itertools import izip

class Frame:
    def __init__(self, filename, frame_time):
        self.filename = filename
        self.frame_time = frame_time

    @property
    def image(self):
        return Image.open(self.filename)

class FrameTimeline:
    def __init__(self, frame_list):
        self.frame_list = list(sorted(frame_list,
                key = lambda a: a.frame_time))
        # Now we set up our frame times
        self.times = np.fromiter(
            (f.frame_time for f in self.frame_list),
            dtype="float64")
        # Index into self.times is index into frame_list
        self.start_time = self.times[0]
        self.stop_time = self.times[-1]
        # Cache this
        self.frame_ind = np.arange(len(self.frame_list), dtype="float64")

    @classmethod
    def from_filenames(cls, filenames, times = None, fps = None):
        # Note that to get the end-times and number of elements correct, we
        # typically use mgrid with nframes + 1.
        nframes = len(filenames)
        if isinstance(times, tuple):
            start, stop = times
            times = np.mgrid[start:stop:1j*(1+nframes)]
        elif isinstance(times, (np.number, numbers.Number)):
            start, stop = 0.0, float(times)
            times = np.mgrid[start:stop:1j*(1+nframes)]
        elif fps is not None:
            if times is not None: raise NotImplementedError
            start = 0.0
            stop = nframes / float(fps)
            times = np.mgrid[start:stop:1j*(1+nframes)]
        elif times is None:
            times = np.arange(nframes, dtype="float64")
        frame_list = [Frame(fn, t) for
            (fn, t) in izip(filenames, times)]
        return cls(frame_list)

    def __getitem__(self, key):
        # We only support list-type indexing.
        return FrameTimeline(self.frame_list[key])

    def compute_frame_mixing(self, times):
        # Figure out which frames we want
        rel_frames = np.interp(times, self.times, self.frame_ind)
        # The rel_frames array is a floating point array of frame indices.  So
        # by looking at the ceiling, the floor, and the remainder, we can get
        # the relative mixing between the two.
        left_frames = np.floor(rel_frames).astype("int64")
        right_frames = np.ceil(rel_frames).astype("int64")
        frame_mix = np.mod(rel_frames, 1.0)
        return left_frames, right_frames, frame_mix

    def scale_fps(self, output_fps, template = None):
        dt = self.stop_time - self.start_time
        nframes = dt * float(output_fps)
        times = np.mgrid[self.start_time:self.stop_time:1j*(1+nframes)]
        mix = self.compute_frame_mixing(times)
        if template is None:
            return mix
        for i, t, i3 in self.mix_frames(*mix):
            fn = template % {'frame': i, 'time:': t}
            print "Saving %s (% 6i / % 6i)" % (
                fn, i+1, nframes)
            i3.save(fn)

    def mix_frames(self, left_frames, right_frames, mix):
        for i, (l, r, f) in enumerate(izip(left_frames, right_frames, mix)):
            dt = self.frame_list[r].frame_time - self.frame_list[l].frame_time
            t = self.frame_list[l].frame_time + dt*f
            i1 = self.frame_list[l].image
            i2 = self.frame_list[r].image
            i3 = Image.blend(i1, i2, f)
            yield i, t, i3
