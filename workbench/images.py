"""Optional Pillow image helpers. No AI detection, OCR or screen capture."""
from __future__ import annotations
import warnings
from pathlib import Path
from .core import checked_file, file_hash, write_new, json_text


def open_image(path: str | Path):
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise ValueError('Image utilities require Pillow; core tools do not.') from exc
    p = checked_file(path)
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        with Image.open(p) as original:
            if original.width * original.height > 40_000_000:
                raise ValueError('Image exceeds the 40-megapixel tool limit.')
            if getattr(original, 'n_frames', 1) != 1:
                raise ValueError('Animated/multipage image: select an explicit frame first.')
            original.load()
            image = ImageOps.exif_transpose(original)
            if 'A' in image.getbands() or 'transparency' in image.info:
                if image.convert('RGBA').getchannel('A').getextrema() != (255, 255):
                    raise ValueError('Transparent images require an explicit background/composite before RGB processing.')
            image = image.convert('RGB')
    return image


def save_new_image(image, path: str | Path) -> None:
    p = Path(path)
    if p.suffix.lower() != '.png': raise ValueError('Output must be .png.')
    if p.is_symlink() or any(x.is_symlink() for x in p.parents): raise ValueError('Symlink outputs refused.')
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('xb') as f: image.save(f, format='PNG')


def contact_sheet(paths: list[str], output: str, columns: int = 4, cell: int = 240) -> dict:
    from PIL import Image, ImageDraw
    if not paths or len(paths) > 80: raise ValueError('Provide 1..80 explicit images per sheet.')
    if not 1 <= columns <= 8 or not 96 <= cell <= 400: raise ValueError('Invalid contact-sheet dimensions.')
    # Validate all files before constructing an output, so no input is silently omitted.
    records = []; thumbs = []
    for number, path in enumerate(paths, 1):
        image = open_image(path)
        ident = f'I{number:03d}'
        records.append({'id': ident, 'file': str(path), 'display_width': image.width,
                        'display_height': image.height, 'sha256': file_hash(checked_file(path))})
        image.thumbnail((cell-12, cell-38)); thumbs.append(image)
    rows = (len(paths)+columns-1)//columns
    sheet = Image.new('RGB',(cell*columns,cell*rows),'white'); draw = ImageDraw.Draw(sheet)
    for i, image in enumerate(thumbs):
        x,y=(i%columns)*cell,(i//columns)*cell
        sheet.paste(image,(x+(cell-image.width)//2,y+8))
        draw.text((x+8,y+cell-26),records[i]['id'],fill='black')
    save_new_image(sheet,output)
    return {'sheet': output, 'mapping': records, 'coordinate_convention': 'Coordinates after EXIF orientation normalization.',
            'warning': 'Thumbnails are overview only. Inspect original-resolution crops before defect decisions.'}


def crop_image(path: str, box: list[int], output: str) -> dict:
    image=open_image(path)
    validate_box(box,image.width,image.height)
    save_new_image(image.crop(tuple(box)),output)
    return {'source':path,'source_sha256':file_hash(checked_file(path)), 'crop':output,
            'box_xyxy_half_open':box, 'source_display_size':[image.width,image.height],
            'coordinate_convention':'EXIF-normalized display pixels; x increases right, y down. Crop-to-source: add x0/y0.'}


def validate_box(box: list[int], width: int, height: int) -> None:
    if len(box)!=4 or any(isinstance(n,bool) or not isinstance(n,int) for n in box): raise ValueError('Box requires four integer coordinates.')
    x0,y0,x1,y1=box
    if not (0<=x0<x1<=width and 0<=y0<y1<=height): raise ValueError('Box outside image or empty; no silent clipping.')


def annotate(path: str, regions: list[dict], output: str) -> dict:
    from PIL import ImageDraw
    image=open_image(path); draw=ImageDraw.Draw(image)
    for i,r in enumerate(regions,1):
        box=r['box']; validate_box(box,image.width,image.height)
        x0,y0,x1,y1=box
        draw.rectangle((x0,y0,x1-1,y1-1),outline='red',width=2)
        draw.text((x0+2,y0+2),f'R{i:03d}',fill='red')
    save_new_image(image,output)
    return {'image':output,'regions':regions,'labels':'R001, R002 ... in input order',
            'warning':'Regions are user/model-supplied observations, not independently verified defect labels.'}


def difference(reference: str, target: str, output: str, threshold: int = 30) -> dict:
    from PIL import ImageChops, ImageStat
    if isinstance(threshold,bool) or not 1<=threshold<=255: raise ValueError('threshold must be 1..255.')
    a,b=open_image(reference),open_image(target)
    if a.size != b.size: raise ValueError('Image sizes differ. Alignment/resampling must be explicitly decided first.')
    delta=ImageChops.difference(a,b).convert('L')
    luminance_delta=ImageChops.difference(a.convert('L'),b.convert('L'))
    mask=delta.point(lambda x:255 if x>=threshold else 0)
    hist=mask.histogram(); n=a.width*a.height
    save_new_image(mask,output)
    return {'reference':reference,'target':target,'threshold':threshold,
            'mean_absolute_luminance_difference':ImageStat.Stat(luminance_delta).mean[0],
            'mask_measure':'Luma-weighted absolute RGB channel differences; threshold in 0..255.',
            'changed_pixel_count':hist[255],'total_pixels':n,'changed_fraction':hist[255]/n,
            'candidate_extent_xyxy':mask.getbbox(),
            'warning':'No registration/lighting correction. Difference mask is NOT defect detection or an accuracy estimate.'}
