import cv2
import os
import numpy as np
from matplotlib import pyplot as plot_img


# source_image is the captured fingerprint to be tested, test_against_image is the fingerprint to test the source_image against
source_image = "Fingerprints\\1_1.png"
test_against_image = "Database\\1_1.png"
#test_against_image = "Database\\1_3.png"

# read in the fingerprint captured and show the original image:
img = cv2.imread(source_image) # user fingerprint image
database_image = cv2.imread(test_against_image) # image read from database folder
height, width, channels = img.shape # grab size of read iamges


# ======================== Applying Contrast to remove Noise ============
# Apply contrast to expose darker parts of fingerprint.
def apply_Contrast(img):
    alpha = 0.5 # assigned weight to the first image
    beta = 0.5 # assigned weight to the second image
    img_second = np.zeros(img.shape, img.dtype) # second image, copy of first one
    contrast = cv2.addWeighted(img, alpha, img_second, 0, beta) # applying contrast
    return contrast



# ======================== Applying Contrast to remove Noise ============


# ======================== Applying Binarization to remove Noise ============
# Binarization is applied to the contrasted image to remove any unwanted pixels.
# Binary colors of black and white allows the matching to be more accurate as the
# pattern of the fingerprint is more exposed.
def apply_Binarization(img):
    # if pixel value is greater then the threshold value it is assigned a singular color of either black or white
    _, mask = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY_INV)
    return mask



# ======================== Applying Binarization to remove Noise ============

# ======================== Applying Thinning through Erosion to remove Noise ============
# The fingerprint is thinned out incase there are ridges on the print that overlap
def apply_Erosion(img):
    kernal = np.ones((3,3), np.uint8) # shape applied to image, 3x3 square shape is applied to contrast image
    erosion = cv2.erode(img, kernal, iterations=1) # erosion mask applied to the contrast image to thin fingerprint ridges
    return erosion


# ======================== Applying Thinning through Erosion to remove Noise ============

# ======================== Show Feature Points ========================================
# distinguish fingerprint as blue by replacing all white pixels with blue pixels
def apply_highlighting(img):
    feature_points = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    Image_blue = np.array(feature_points, copy=True)

    white_px = np.asarray([255, 255, 255])
    blue_px = np.asarray([0  , 255  , 255  ])

    (row, col, _) = feature_points.shape

    for r in range(row):
        for c in range(col):
            px = feature_points[r][c]
            if all(px == white_px):
                Image_blue[r][c] = blue_px
    
    return Image_blue

# ======================== Show Feature Points ===========================================     

# ======================== Show Feature Points ========================================
# distinguish fingerprint as blue by replacing all white pixels with blue pixels
def show_featurepoints(img):
    
    #show feature points found in fingerprint using orb detector
    orb  = cv2.ORB_create(nfeatures=1200)
    keypoints, descriptors = orb.detectAndCompute(img, None)
    featurepoint_img = img
    featurepoint_img = cv2.drawKeypoints(featurepoint_img, keypoints, None, color=(255, 0 ,0))

    return featurepoint_img


# ======================== Show Feature Points ===========================================     


# ======================== Applying each process to fingerprint for analysis ===========================================

# applying image processing to user fingerprints
analyzed_image = img
contrast = apply_Contrast(img)
analyzed_image = contrast
mask = apply_Binarization(contrast)
analyzed_image = mask
erosion = apply_Erosion(mask)
analyzed_image = erosion
Image_blue = apply_highlighting(erosion)
featurepoint_img = show_featurepoints(Image_blue)

# applying image processing to tested fingerprint in database
Image_blue2 = apply_highlighting(database_image)


process_done = ["Original", "Contrast","Binarization","Thinning", "Highlighting", "Feature Points"]
images = [img, contrast, mask, erosion, Image_blue, featurepoint_img]

# plot all transformations done to the fingerprint
for i in range(6):
    plot_img.subplot(2, 3, i+1), plot_img.imshow(images[i], 'gray')
    plot_img.title(process_done[i])
    plot_img.xticks([]),plot_img.yticks([])


# ======================== Applying each process to fingerprint for analysis ===========================================


# ======================== Feature Matching using ORB Detection ===========================================
orb  = cv2.ORB_create(nfeatures=150)

match_results_img = cv2.cvtColor(Image_blue, cv2.COLOR_RGB2BGR) #convert image back
match_results_img2 = cv2.cvtColor(Image_blue2, cv2.COLOR_RGB2BGR) #convert image back

# Feature Matching using ORB Detection
keypoints_img1, des1 = orb.detectAndCompute(analyzed_image, None) # Determine all keypoints in image 1
keypoints_img2, des2 = orb.detectAndCompute(database_image, None) # Determine all keypoints in image 2

# Brute Force Matching
brute_f = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matchesOriginal = brute_f.match(des1, des1)  # Match image 1 with it self to find out how many keypoints there are for image matching
matchesNew = brute_f.match(des1, des2)   # Match image 1 with image 2 to find out how many related keypoints there are between the two images

# The match rate is determined by getting the total matches between image 1 and itself, and then dividing it by the number of matches for image 1 and 2.
# The reason for this calculation is because image 1 matching with itself is essentially a 100% match rate, this gives us the number of keypoints for a 
# a perfect match. We can then get the match rate by dividing the match ratio of image 1 and 2, by the ideal match rate by comparing how many keypoints
# are found and dividing the total keypoints.
match_rate = (len(matchesNew)/len(matchesOriginal))*100     


# Draw all matches in new window
matching_result = cv2.drawMatches(match_results_img, keypoints_img1, match_results_img2, keypoints_img2, matchesNew, None, matchColor=(0, 0 ,255))


# Output for results of matching
# Show text for Match Rate of Two Images
match_height, match_width, match_channels = img.shape # grab size of match results image
b,g,r,a = 255,255,255,0
repeat_draw = 10 # used to redraw the text drawn, the lower the value the lower the opacity the text will be
for x in range(repeat_draw):
    cv2.putText(matching_result,"Match Rate: " + str(match_rate) + "%", ( int(match_width/2),int(match_height-10)), cv2.FONT_HERSHEY_SIMPLEX , 0.7, (b,g,r), 1, cv2.LINE_AA) #here


# If the match rate is greater then 90% we have a match on the fingerprint
b,g,r,a = 0,255,0,0
if match_rate > 90:
    for x in range(repeat_draw):
        cv2.putText(matching_result,"FINGERPRINT MATCH FOUND.", ( int(match_width/2)-30,int(match_height-30)), cv2.FONT_HERSHEY_SIMPLEX , 0.7, (b,g,r), 1, cv2.LINE_AA) #here
else:
    for x in range(repeat_draw):
        cv2.putText(matching_result,"NO MATCH FOUND.", ( int(match_width/2),int(match_height-30)), cv2.FONT_HERSHEY_SIMPLEX , 0.7, (b,g,r), 1, cv2.LINE_AA) #here
    

# output matching results
cv2.imshow("Matching Fingerprint Results:", cv2.resize(matching_result, (512, 348)))


# ======================== Feature Matching using ORB Detection ===========================================



# setting sizes and title for window
fig = plot_img.gcf()
fig.set_size_inches(8.5, 6, forward=True)
fig.canvas.set_window_title(' Fingerprint Identification System')
plot_img.show()




cv2.waitKey(0)
cv2.destroyAllWindows()
