import numpy as np

envi_class_colors = np.array([0,   0,   0, 255,   0,   0,   0, 255,   0,   0,   0, 255, 255, 255,   0,
   0, 255, 255, 255,   0, 255, 176,  48,  96,  46, 139,  87, 160,  32, 240,
 255, 127,  80, 127, 255, 212, 218, 112, 214, 160,  82,  45, 127, 255,   0,
 216, 191, 216, 238,   0,   0, 205,   0,   0, 139,   0,   0,   0, 238,   0,
   0, 205,   0,   0, 139,   0,   0,   0, 238,   0,   0, 205,   0,   0, 139,
 238, 238,   0, 205, 205,   0, 139, 139,   0,   0, 238, 238,   0, 205, 205,
   0, 139, 139, 238,   0, 238, 205,   0, 205, 139,   0, 139, 238,  48, 167,
 205,  41, 144, 139,  28,  98, 145,  44, 238, 125,  38, 205,  85,  26, 139,
 255, 165,   0, 238, 154,   0, 205, 133,   0, 139,  90,   0, 238, 121,  66,
 205, 104,  57, 139,  71,  38, 238, 210, 238, 205, 181, 205, 255,   0,   0,
   0, 255,   0,   0,   0, 255, 255, 255,   0,   0, 255, 255, 255,   0, 255,
 176,  48,  96,  46, 139,  87, 160,  32, 240, 255, 127,  80, 127, 255, 212,
 218, 112, 214, 160,  82,  45, 127, 255,   0, 216, 191, 216, 238,   0,   0,
 205,   0,   0, 139,   0,   0,   0, 238,   0,   0, 205,   0,   0, 139,   0,
   0,   0, 238,   0,   0, 205,   0,   0, 139, 238, 238,   0, 205, 205,   0,
 139, 139,   0,   0, 238, 238,   0, 205, 205,   0, 139, 139, 238,   0, 238,
 205,   0, 205, 139,   0, 139, 238,  48, 167, 205,  41, 144, 139,  28,  98,
 145,  44, 238, 125,  38, 205,  85,  26, 139, 255, 165,   0, 238, 154,   0,
 205, 133,   0, 139,  90,   0, 238, 121,  66, 205, 104,  57, 139,  71,  38,
 238, 210, 238, 205, 181, 205, 255,   0,   0,   0, 255,   0,   0,   0, 255,
 255, 255,   0,   0, 255, 255, 255,   0, 255, 176,  48,  96,  46, 139,  87,
 160,  32, 240, 255, 127,  80, 127, 255, 212, 218, 112, 214, 160,  82,  45,
 127, 255,   0, 216, 191, 216, 238,   0,   0, 205,   0,   0, 139,   0,   0,
   0, 238,   0,   0, 205,   0,   0, 139,   0,   0,   0, 238,   0,   0, 205,
   0,   0, 139, 238, 238,   0, 205, 205,   0, 139, 139,   0,   0, 238, 238,
   0, 205, 205,   0, 139, 139, 238,   0, 238, 205,   0, 205, 139,   0, 139,
 238,  48, 167, 205,  41, 144, 139,  28,  98, 145,  44, 238, 125,  38, 205,
  85,  26, 139, 255, 165,   0, 238, 154,   0, 205, 133,   0, 139,  90,   0,
 238, 121,  66, 205, 104,  57, 139,  71,  38, 238, 210, 238, 205, 181, 205,
 255,   0,   0,   0, 255,   0,   0,   0, 255, 255, 255,   0,   0, 255, 255,
 255,   0, 255, 176,  48,  96,  46, 139,  87, 160,  32, 240, 255, 127,  80,
 127, 255, 212, 218, 112, 214, 160,  82,  45, 127, 255,   0, 216, 191, 216,
 238,   0,   0, 205,   0,   0, 139,   0,   0,   0, 238,   0,   0, 205,   0,
   0, 139,   0,   0,   0, 238,   0,   0, 205,   0,   0, 139, 238, 238,   0,
 205, 205,   0, 139, 139,   0,   0, 238, 238,   0, 205, 205,   0, 139, 139,
 238,   0, 238, 205,   0, 205, 139,   0, 139, 238,  48, 167, 205,  41, 144,
 139,  28,  98, 145,  44, 238, 125,  38, 205,  85,  26, 139, 255, 165,   0,
 238, 154,   0, 205, 133,   0, 139,  90,   0, 238, 121,  66, 205, 104,  57,
 139,  71,  38, 238, 210, 238, 205, 181, 205, 255,   0,   0,   0, 255,   0,
   0,   0, 255, 255, 255,   0,   0, 255, 255, 255,   0, 255, 176,  48,  96,
  46, 139,  87, 160,  32, 240, 255, 127,  80, 127, 255, 212, 218, 112, 214,
 160,  82,  45, 127, 255,   0, 216, 191, 216, 238,   0,   0, 205,   0,   0,
 139,   0,   0,   0, 238,   0,   0, 205,   0,   0, 139,   0,   0,   0, 238,
   0,   0, 205,   0,   0, 139, 238, 238,   0, 205, 205,   0, 139, 139,   0,
   0, 238, 238,   0, 205, 205,   0, 139, 139, 238,   0, 238, 205,   0, 205,
 139,   0, 139, 238,  48, 167, 205,  41, 144, 139,  28,  98, 145,  44, 238,
 125,  38, 205,  85,  26, 139, 255, 165,   0, 238, 154,   0, 205, 133,   0,
 139,  90,   0, 238, 121,  66, 205, 104,  57, 139,  71,  38, 238, 210, 238,
 205, 181, 205, 255,   0,   0,   0, 255,   0,   0,   0, 255, 255, 255,   0,
   0, 255, 255, 255,   0, 255, 176,  48,  96,  46, 139,  87, 160,  32, 240,
 255, 127,  80, 127, 255, 212, 218, 112, 214, 160,  82,  45, 127, 255,   0,
 216, 191, 216], dtype=np.uint8)

print(len(envi_class_colors))
print(256*3)

np.save("envi_class_colors.npy", envi_class_colors)