"""Compute a motion score from images"""

import numpy as np
import cv2
import math
import sys

def motion_score(frame_buffer, detection="bgs2", kernel_size=4):
  """
  Assign a score to the amount of motion detected 
  frame_buffer is a list of opencv images (at least 2) 
  detection is one of {"bgs" (BackgroundSubtractorMOG), 
  "bgs2" (BackgroundSubtractorMOG2), or "flow" (optical flow)}
  Returns fraction of pixels moving
  """
  score, _ = run_motion_detection(frame_buffer, detection, kernel_size)

def run_motion_detection(frame_buffer, detection="bgs2", kernel_size=4):
  """
  Assign a score to the amount of motion detected and generate a foreground mask
  frame_buffer is a list of opencv images (at least 2) 
  detection is one of {"bgs" (BackgroundSubtractorMOG), 
  "bgs2" (BackgroundSubtractorMOG2), or "flow" (optical flow)}
  Returns score (fraction of pixels moving), foreground mask 
  """
  if len(frame_buffer) < 2:
    print "frame_buffer must have a length of at least 2!!"
    return None, None

  if detection == "bgs":
    fgmask = background_subtract(frame_buffer, "bgs")
  elif detection == "bgs2":
    fgmask = background_subtract(frame_buffer, "bgs2")
  elif detection == "flow":
    fgmask = optical_flow(frame_buffer)
  else:
    print "detection type not recognized!"
    return None, None
  if fgmask == None:
    return None, None

  #dilate and erode to remove noise
  kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
  fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

  nonzero_pixels = cv2.countNonZero(fgmask)
  score = float(nonzero_pixels) / np.size(fgmask)

  return score, fgmask

def optical_flow(frame_buffer):
  """
  Create a greyscale mask showing where the motion is using optical flow
  frame_buffer is a list of opencv images (at least 2)
  Returns a greyscale mask with moving pixels
  """
  if len(frame_buffer) < 2:
    print "frame_buffer must have a length of at least 2!!"
    return None
  new_frame = cv2.cvtColor(frame_buffer[-1],cv2.COLOR_BGR2GRAY)
  prev_frame = cv2.cvtColor(frame_buffer[-2],cv2.COLOR_BGR2GRAY)
  flow = cv2.calcOpticalFlowFarneback(prev_frame, new_frame, 0.5, 3, 15, 3, 5, 1.2, 0)
  mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
  _, thres = cv2.threshold(mag, 4.0, 255, cv2.THRESH_BINARY)
  fgmask = cv2.convertScaleAbs(thres)
  return fgmask

def background_subtract(frame_buffer, detection="bgs2"):
  """cv2.imshow('color frame', draw)
  Create a greyscale mask showing where the motion is using background subtraction
  frame_buffer is a list of opencv images (at least 2)
  detection is one of {"bgs" (BackgroundSubtractorMOG) or 
    "bgs2" (BackgroundSubtractorMOG2)}
  Returns a greyscale mask with moving pixels
  """
  if len(frame_buffer) < 2:
    print "frame_buffer must have a length of at least 2!!"
    return None

  if detection == "bgs2":
    bgs = cv2.BackgroundSubtractorMOG2(len(frame_buffer)-1, 25)
  elif detection == "bgs":
    bgs = cv2.BackgroundSubtractorMOG(len(frame_buffer)-1, 4, 0.8)
  else:
    print "detection type was not recognized!"
    return None
  for frame in frame_buffer:
    fgmask = bgs.apply(frame)
  return fgmask


def create_color_img(frame_buffer, detection="bgs2", kernel_size=4):
  """
  Create a color image showing where the motion is
  frame_buffer is a list of opencv images (at least 2)
  Returns a color image with moving pixels having colors from the original image
  """

  score, fgmask = run_motion_detection(frame_buffer, detection, kernel_size)
  print "{0:.3f}".format(score)

  #return colors from the original image beneath the mask
  mask_rgb = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)

  #pdb.set_trace()
  draw = frame & mask_rgb

  return draw

if __name__ == "__main__":
  detection = "bgs2"
  if len(sys.argv) >= 2:
    if sys.argv[1] in {"bgs2", "bgs", "flow"}:
      detection = sys.argv[1]
    else:
      print "usage: motion_score.py detection_type"

  capture = cv2.VideoCapture(0)
  frame_buffer = []
  history = 2

  while capture.isOpened():
    _, frame = capture.read()  
    frame_buffer.append(frame)
    if len(frame_buffer) > history+1:
      frame_buffer.pop(0)
    if len(frame_buffer) < history:
      continue

    #score = motion_score(frame_buffer, detection)
    #print "{0:.3f}".format(score)

    draw = create_color_img(frame_buffer, detection)
    if draw == None:
      print "draw was None"
      continue
    cv2.imshow('color frame', draw)

    # quit if Esc is pressed
    c = cv2.waitKey(30) & 0xff
    if c == 27:
      break

  capture.release()
  cv2.destroyAllWindows()
