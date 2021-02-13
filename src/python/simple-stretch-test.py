## Image Processing libraries
from skimage import exposure
import rawpy
import imageio

# Reference https://www.kaggle.com/tsilveira/raw-image-processing

raw_filename=r'_MG_6188.CR2'
jpg_filename=r'output.jpg'

# I tried a few things out and found gamma adjust then histogram is best.  
# And gamma=1, gain=1 is best contrast for my test image, Flame Nebula 5s exposure.
# The goal is just to have a small reference image to send to Discord for checking drift over time without going outside..

rawImg = rawpy.imread(raw_filename)
rgbImg = rawImg.raw_image_visible
gImg = exposure.adjust_gamma(rgbImg, gamma=1, gain=1)
ghImg = exposure.equalize_hist(gImg)

imageio.imwrite(jpg_filename, ghImg)
