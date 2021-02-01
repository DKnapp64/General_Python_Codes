from PIL import Image, ImageFont, ImageDraw

inlegend = "ssta_colorbar_legend.PNG"
img = Image.open(inlegend)
draw = ImageDraw.Draw(img)

# use a bitmap font
## font = ImageFont.load("arial.pil")
## draw.text((10, 10), "hello", font=font)

draw.text((10, 25), "world", font=font)
draw = ImageDraw.Draw(img)                                                    
font = ImageFont.truetype("/usr/share/fonts/msttcorefonts/arial.ttf", size=28)
draw.text((50,50), datestr, (1,1,1), font=font)
font = ImageFont.truetype("/usr/share/fonts/msttcorefonts/arial.ttf", size=14)
draw.text((50,150), datestr, (1,1,1), font=font)
img.save('out_test_font.tif')                                 
img = None 
