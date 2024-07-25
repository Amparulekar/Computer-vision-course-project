This readme explains how to run the code and is of some value.
All our code has been placed in separate folder folders numberd m1, m2 and m3.
All our code requires the following folder to be downloaded: (https://drive.google.com/drive/folders/1V46ejEvwPg0D5aw-9BDSaPDnh_rgfZI_)
This must be saved in root directory of the repository and named `cv`.
## m1 (Linear Programming)
This has the linear programming method's implementation (https://arxiv.org/pdf/1511.04472.pdf)
The scripts here are (Note all programs are run from the root directory of the repository):

 - edgeblanker.py: script to set the pixel values of the boundaries of shuffled jigsaw pieces to zero.


    Syntax: `python3 m1/edgeblanker.py --path <path to dir with image segments> --pad <number of rows and columns to pad>`


    Example: `python3 m1/edgeblanker.py --path segmented/general/0/ --pad 3`

 - jigsaw.py: script to create indiviual pieces from an image.


    Syntax: `python3 m1/jigsaw.py --ss <sample size from each category> --ns <number of segments to split each col/row into> [--resize]`


    Example: `python3 m1/jigsaw.py --ss 2 --ns 3`


    This produces two folders in each category in a folder called segmented, with 3*3 = 9 images each.
    If --resize is passed, each whole image is first resized to 600x600, and then split into segments.
    Also, run `python3 m1/jigsaw.py --clean` to clear the `segmented` folder.

 - main.py: script to put together a list of image parts 


    Syntax: `python3 m1/main.py --path <path to dir with segments> --ns <number of rows/cols> --mdm <margin of similarity at boundaries>`
    
    
    Example: `python3 m1/main.py --path segmented/general/0/ --ns 3 --mdm 1`
    
    
    Note: for good solutions, mdm must be greater than the padding supplied to edgeblanker.py, but also not too large.

 - renamer.py: script to rename files in the cv folder to a numeric system.
    
    
    Syntax: `python3 m1/renamer.py`


 - solver.py: contains a class used in the main.py file.


## m2 (Greedy Approach)
Files added `main.py`

TO RUN : `python3 m2/main.py --image <imagePath>`  
Example: `python3 m2/main.py --image convincingDirectory/m2/original.jpg`  
To make the algorithm go to the next step press `q`

Libraries needed:
- scikit-image
- opencv-python
- numpy




## m3 (DL Models)
This folder presents jupyter notebooks for training two models and their corresponding versions for Google colab.
The files themselves are pretty self-explanatory to follow to train a model keras.
Model designs and metrics are present in convincingDirectory/m3.