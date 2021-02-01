import numpy as np

def get_overlap_info(focal_bounds, focal_res, img_bounds, img_res):             
    """This function tests for the intersection of 2 spaces defined by a focal (mosaic) 
     area and an image area.  It takes the input bounds of a focal area         
     (e.g., a map tile in UTM to mosaic), the resolution, the image bounds      
     (also in UTM) and its resolution.  It returns two tuples with the upper left
     (i.e., NorthWest) corner pixel and line (column and row), and the number   
     of columns and rows for the image area and a tuple of the same format,     
     but for the coinciding mosaic area.  If there is no intersection of the 2  
     spaces, it returns a tuple of four -1s.                                    
    """                                                                         
                                                                                
    ## focal and image bounds are in the order (Xmin, Xmax, Ymin, Ymax)         
    r1 = [focal_bounds[0], focal_bounds[3], focal_bounds[1], focal_bounds[2]]   
    r2 = [img_bounds[0], img_bounds[3], img_bounds[1], img_bounds[2]]           
                                                                                
    ## find intersection                                                        
    intersection = [max(r1[0], r2[0]), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]
                                                                                
    ## Test for non-overlap.  if not overlapping, return -1s.                   
    if ((intersection[0] > intersection[2]) or (intersection[3] > intersection[1])):
      return((-1.0,-1.0,-1.0,-1.0), (-1.0,-1.0,-1.0,-1.0))                      
                                                                                
    # check for any overlap                                                     
    left1flt = (intersection[0]-r1[0])/focal_res # difference divided by pixel dimension
    left1 = int(np.abs(round((intersection[0]-r1[0])/focal_res))) # difference divided by pixel dimension
    top1flt = round((intersection[1]-r1[1])/focal_res)                          
    top1 = int(np.abs(round(((intersection[1]-r1[1])/focal_res))))              
    col1 = int(np.abs(round(((intersection[2]-r1[0])/focal_res) - left1flt))) # difference minus offset left
    row1 = int(np.abs(round(((intersection[3]-r1[1])/focal_res) - top1flt)))    
                                                                                
    left2flt = (intersection[0]-r2[0])/img_res # difference divided by pixel dimension
    left2 = int(np.abs(round(((intersection[0]-r2[0])/img_res)))) # difference divided by pixel dimension
    top2flt = (intersection[1]-r2[1])/img_res                                   
    top2 = int(np.abs(round(((intersection[1]-r2[1])/img_res))))                
    col2 = int(np.abs(round(((intersection[2]-r2[0])/img_res) - left2flt))) # difference minus new left offset
    row2 = int(np.abs(round(((intersection[3]-r2[1])/img_res) - top2flt)))      
                                                                                
    ## print("%d   %d    %d   %d" % (left1,top1,col1,row1))                     
    ## print("%d   %d    %d   %d" % (left2,top2,col2,row2))                     
                                                                                
    return([left1,top1,col1,row1], [left2,top2,col2,row2])
