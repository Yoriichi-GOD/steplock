from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
root=Path(__file__).resolve().parents[1]
files=sorted((root/'previews').glob('slide-*.png'))
thumb_w,thumb_h=480,270
sheet=Image.new('RGB',(3*thumb_w,((len(files)+2)//3)*304),'#05070B')
draw=ImageDraw.Draw(sheet)
for i,path in enumerate(files):
    image=Image.open(path).convert('RGB');image.thumbnail((thumb_w,thumb_h),Image.Resampling.LANCZOS)
    x=(i%3)*thumb_w;y=(i//3)*304
    sheet.paste(image,(x,y));draw.text((x+12,y+277),f'{i+1:02d} / STEPLOCK',fill='#76C7FF')
sheet.save(root/'previews/contact-sheet.png')
print(f'Contact sheet: {len(files)} native PowerPoint slide renders')
