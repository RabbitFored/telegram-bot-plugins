from PIL import Image, ImageOps


def extend_uniform_background(image_path, target_width, target_height, output_path):
    img = Image.open(image_path)

    # Get the background color (assuming the corner pixel is the background)
    background_color = img.getpixel((0, 0))

    # Calculate the size for the border
    original_width, original_height = img.size
    border_width = max((target_width - original_width) // 2, 0)
    border_height = max((target_height - original_height) // 2, 0)

    # Add border to the image with the background color
    extended_image = ImageOps.expand(img, border=(border_width, border_height), fill=background_color)

    # Save the extended image
    extended_image.save(output_path)