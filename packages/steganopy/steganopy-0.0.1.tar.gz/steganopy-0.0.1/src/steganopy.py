from blowfish import Blowfish
try:
    from PIL import Image
except:
    raise Exception("Pillow module is not available. Pip install it and try again")


def validate_image(image):
    image = Image.open(image)
    if image.mode not in ('RGB', 'RGBA'):
        raise ValueError('We need RGB, or RGBA image formats only.')
    if image.format == 'JPEG':
        raise ValueError('JPEG is a lossy format and is not suited for use in this tool')
    return image, image.mode.lower()


def encrypt_data_if_needed(data_to_hide, cipher_key):
    if cipher_key:
        cipher = Blowfish(cipher_key)
        return cipher.encryptCTR(data_to_hide)
    else:
        return data_to_hide


def encode_data_in_image(image_data, data_to_hide, pixel_type):
    data_len = check_for_valid_data_length(image_data, data_to_hide)
    image_data = iter(image_data)
    for character_position in xrange(data_len):
        rgba_values, rgb_values = get_rgb_and_rgba_values_for_next_three_pixels(image_data, pixel_type=pixel_type)
        rgb_values = set_least_significant_bit_to_zero(rgb_values)
        rgb_values = encode_character_data_in_rgb_values(data_to_hide, rgb_values, character_position)
        set_flag_byte_if_at_end_of_data(character_position, data_len, rgb_values)
        rgb_values = add_alpha_values_back_into_rgb_values_if_required(rgb_values, rgba_values, pixel_type)
        for pixel in repackage_pixel_values_into_tuples(rgb_values, pixel_type):
            yield pixel


def check_for_valid_data_length(image_data, data_to_hide):
    """
    Check if cover image is significantly large enough to encode all the data

    Since we are using the lsb of the cover image to encode the data it takes three pixels to hide one byte of data.
    That is three bits in the R and G values and two bits plus a flag bit in the B value. So we require an image that
    is three times as large as the data we want to hide.
    """
    data_len = len(data_to_hide)
    if data_len == 0:
        raise ValueError('No data was provided to hide')
    if data_len * 3 > len(image_data):
        raise ValueError('The data provided is too large to fit in the image')
    return data_len


def get_rgb_and_rgba_values_for_next_three_pixels(image_data, pixel_type):
    if pixel_type == "rgb":
        rgba_values = []
        rgb_values = [image_data.next()[:3], image_data.next()[:3], image_data.next()[:3]]
    else:
        rgba_values = [image_data.next()[:4], image_data.next()[:4], image_data.next()[:4]]
        rgb_values = [rgba_values[0][:3], rgba_values[1][:3], rgba_values[2][:3]]
    return [rgba_values, rgb_values]


def set_least_significant_bit_to_zero(rgb_values):
    return [value & ~1 for value in rgb_values[0][:3] + rgb_values[1][:3] + rgb_values[2][:3]]


def encode_character_data_in_rgb_values(data_to_hide, rgb_values, character_position):
    byte = ord(data_to_hide[character_position])
    for bit in xrange(7, -1, -1):
        rgb_values[bit] |= byte & 1
        byte >>= 1
    return rgb_values


def set_flag_byte_if_at_end_of_data(character_position, data_len, rgb_values):
    """
    The lsb of the blue value of a pixel is our flag bit this will always be zero until the end of our data.
    """
    if character_position == data_len - 1:
        rgb_values[-1] |= 1


def add_alpha_values_back_into_rgb_values_if_required(rgb_values, rgba_values, pixel_type):
    if pixel_type == "rgba":
        rgb_values.insert(3, rgba_values[0][-1])
        rgb_values.insert(7, rgba_values[1][-1])
        rgb_values.append(rgba_values[2][-1])
    return rgb_values


def repackage_pixel_values_into_tuples(pixel_values, pixel_type):
    pixel_values = tuple(pixel_values)
    pixel_len = 3
    if pixel_type == "rgba":
        pixel_len = 4
    yield pixel_values[0:pixel_len]
    yield pixel_values[pixel_len:pixel_len * 2]
    yield pixel_values[pixel_len * 2:pixel_len * 3]


def update_pixel_position(column_position, row_number, image_width):
    if column_position == image_width - 1:
        column_position = 0
        row_number += 1
    else:
        column_position += 1
    return column_position, row_number


def extract_next_byte(next_three_pixels):
    extracted_byte = 0
    extracted_byte = shift_lsb_to_make_room_for_eigth_byte(extracted_byte, next_three_pixels)
    extracted_byte |= next_three_pixels[7] & 1
    return chr(extracted_byte)


def shift_lsb_to_make_room_for_eigth_byte(extracted_byte, next_three_pixels):
    for c in xrange(7):
        extracted_byte |= next_three_pixels[c] & 1
        extracted_byte <<= 1
    return extracted_byte


def decrypt_data(decoded_data, cipher_key):
    cipher_decrypt = Blowfish(cipher_key)
    return cipher_decrypt.decryptCTR(decoded_data)


def decrypt_data_if_needed(decoded_data, cipher_key):
        if cipher_key != "":
            decoded_data = decrypt_data(decoded_data, cipher_key)
        return decoded_data
