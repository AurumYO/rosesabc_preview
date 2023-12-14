from PIL import Image, ImageOps
from io import BytesIO
from django.core.files import File
from roses.utils import apply_watermark


def resize_article_photo(photo, section_code):
    """
    Resize an article photo if needed, applying watermark

    Args:
        photo (Image): The original photo as a PIL Image object.
        section_code (int): Code indicating the section to which the photo belongs.

    Returns:
        File: A Django File object containing the resized and optionally watermarked image.

    Raises:
        None.

    The function resizes the input image to a maximum width of 1200 pixels.
    If the image width exceeds 1200 pixels, it is resized proportionally.
    A watermark is applied if the section_code is not 0 (indicating the main image).

    Example:
        resized_file = resize_article_photo(photo, section_code)
    """
    # open photo object
    img = Image.open(photo)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    # get its current size (width, height)
    (w, h) = img.size
    # if the width is is too large
    if w > 1200:
        # define new size scale and size
        scale = w / 1200
        new_size = (int(w // scale), int(h // scale))
        # resize the image
        img = img.resize(new_size, Image.Resampling.LANCZOS)

        im_io = BytesIO()

        # Apply watermark with the user's name if not main image
        if section_code != 0:
            img_with_watermark = apply_watermark(img)
            # convert to file , saving 75% quality and return
            img_with_watermark.save(im_io, "JPEG", quality=75, optimize=True)
        else:
            img.save(im_io, "JPEG", quality=75, optimize=True)
        # convert to file , saving 75% quality and return
        new_image = File(im_io, name=photo.name)
        return new_image
    # if the image width not larger than 1200px return photo only with watermark
    else:
        im_io = BytesIO()
        # Apply watermark with the user's name if not main image
        if section_code != 0:
            img_with_watermark = apply_watermark(img)
            # convert to file , saving 75% quality and return
            img_with_watermark.save(im_io, "JPEG", quality=75, optimize=True)
        else:
            img.save(im_io, "JPEG", quality=75, optimize=True)
        # convert to file , saving 75% quality and return
        new_image = File(im_io, name=photo.name)
        return new_image
