import src.steganopy as stegano


def create_stegano_image(original_image, data_to_hide, cipher_key=""):
    """
    # PARAMETERS:
    original_image - A string representing the full path to an RGB or RGBA format PNG Image file.
    data_to_hide   - A string representing the full path to a file that will be encoded into the original_image.
    cipher_key     - An optional string that will be used as the cipher key to encrypt the data prior to encoding
                     in the original image. Must be between 8 and 56 characters in length.

    # RETURNS:
    An image object
    """
    original_image, pixel_type = stegano.validate_image(original_image)
    data_to_hide = stegano.encrypt_data_if_needed(open(data_to_hide, 'rb').read(), cipher_key)
    image_encoded_with_data = original_image.copy()
    image_width, column_position, row_number = image_encoded_with_data.size[0], 0, 0
    for pixel in stegano.encode_data_in_image(image_encoded_with_data.getdata(), data_to_hide, pixel_type):
        image_encoded_with_data.putpixel((column_position, row_number), pixel)
        column_position, row_number = stegano.update_pixel_position(column_position, row_number, image_width)
    return image_encoded_with_data


def extract_data_from_stegano_image(image, cipher_key=""):
    """
    # PARAMETERS
    image      - A string representing the full path to a previously created steganographic image.
    cipher_key - An optional string that will be used as the cipher key to decode the extracted data.
                 This will be required if the data was encrypted prior to creating the original
                 steganographic image.

    # RETURNS:
    A string that can be written to the appropriate file type
    """
    decoded_data = ""
    image, _ = stegano.validate_image(image)
    image_data = iter(image.getdata())
    while True:
        next_three_pixels = list(image_data.next()[:3] + image_data.next()[:3] + image_data.next()[:3])
        decoded_data += stegano.extract_next_byte(next_three_pixels)
        if next_three_pixels[-1] & 1:
            return stegano.decrypt_data_if_needed(decoded_data, cipher_key)
