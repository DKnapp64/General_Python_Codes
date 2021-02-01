import os, sys
import ffmpeg

(
    ffmpeg
    .input('/Carnegie/DGE/caodata/Scratch/dknapp/Planet_Spec_Prep/Cubes/cicra_vswir_???.jpg', pattern_type='glob', framerate=3)
    .output('cicra_vswir_pca_movie.mp4')
    .run()
)
