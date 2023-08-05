from django.contrib.contenttypes.models import ContentType

import PIL.Image

from cropduster.models import Image, Thumb
from cropduster.resizing import Size, Box

from wire.articles.models import WireArticle


wire_article_ct = ContentType.objects.get_for_model(WireArticle)


IMAGE_SIZES = [
    Size('lead_large', label="Lead Image", w=675, min_h=250, auto=[
        Size('lead_medium', w=480),
        Size('lead_massive', w=1040),
    ]),
    Size('horizontal', label="Horizontal", w=650, h=403, auto=[
        Size('horizontal_short_large', w=675, h=371),
        Size('horizontal_medium', w=320, h=198),
        Size('horizontal_small', w=185, h=112),
    ]),
    Size('small_square', label="Square Thumbnail", w=150, h=150, auto=[
        Size('short_large_square', w=350, h=280),
    ]),
]


def import_images(wire_article, v2_crop, v2_attribution):
    pil_img = PIL.Image.open(wire_article.lead_image.path)
    w, h = pil_img.size

    crop_box = get_crop_box(v2_crop) or Box(0, 0, w, h)

    new_img = Image(width=w, height=h,
            image=wire_article.lead_image.name,
            attribution=v2_attribution)
    new_img.content_type = wire_article_ct
    new_img.object_id = wire_article.pk
    new_img.save()

    for size in IMAGE_SIZES:
        best_fit = size.fit_to_crop(crop_box, original_image=pil_img)
        fit_box = best_fit.box
        crop_thumb = Thumb(**{
            "name": "Crop",
            "width": fit_box.w,
            "height": fit_box.h,
            "crop_x": fit_box.x1,
            "crop_y": fit_box.y1,
            "crop_w": fit_box.w,
            "crop_h": fit_box.h,
        })
        new_thumbs = new_img.save_size(size, crop_thumb)
        for name, thumb in new_thumbs.iteritems():
            new_img.thumbs.add(thumb)


def get_crop_box(v2_crop):
    if any([getattr(v2_crop, 'crop_%s' % a) is None for a in ['x', 'y', 'w', 'h']]):
        return None
    x1, y1 = v2_crop.crop_x, v2_crop.crop_y
    x2, y2 = x1 + v2_crop.crop_w, y1 + v2_crop.crop_h
    return Box(x1, y1, x2, y2)
