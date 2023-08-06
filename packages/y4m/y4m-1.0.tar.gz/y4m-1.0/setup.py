#!/usr/bin/env python

from distutils.core import setup

description = """YUV4MPEG2 (.y4m) Reader/Writer

```python
import sys
import y4m


def process_frame(frame):
    # do something with the frame
    pass


if __name__ == '__main__':

    parser = y4m.Reader(process_frame, verbose=True)
    # simulate chunk of data
    infd = sys.stdin
    if sys.hexversion >= 0x03000000: # Python >= 3
        infd = sys.stdin.buffer

    with infd as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            parser.decode(data)
```
"""

setup(name='y4m',
      version='1.0',
      description='YUV4MPEG2 (.y4m) Reader/Writer',
      author='Pierre Gronlier',
      author_email='ticapix@gmail.com',
      url='http://gronlier.fr/blog',
      packages=['y4m'],
      long_description=description
     )
