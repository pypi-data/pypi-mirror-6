Steganopy
=========

|Build Status|

Steganography is the art and science of writing hidden messages in such
a way that no one, apart from the sender and intended recipient,
suspects the existence of the message. The word steganography is of
Greek origin and means "concealed writing".

Steganopy is a steganographic tool written in Python. It comes with a
handy gui and an easy to use api so that it can be integrated into your
Python projects. Steganopy allows you to encode data into any PNG image
with an RGB or RGBA format.

Files are encoded into PNG images using the least significant bit
modification method. As long as your original image is sufficiently
large enough to hold the data to be encode any type of file could be
concealed within an image (Text files, other images, etc). A password
can optionally be supplied to encrypt data prior to encoding for a truly
unbreakable level of protection.

Installation
============

``pip install steganopy``

Usage
=====

You have two ways to use steganopy

GUI
---

Use the gui by simply issuing the command ``steganopy`` will now be able to use
the gui to encode data into PNG images as well as extract data from
steganographic images

In a Python program
-------------------

The api offers two functions to call from within your python programs.
*NOTE* The cipher key is optional but if you use one to encode your data
you will have to use the same one again to extract that data.

Encode data
~~~~~~~~~~~

.. code:: python

    from os.path import sep, expanduser

    from steganopy.api import create_stegano_image

    output_dir = sep.join([expanduser('~'), "Downloads"])
    stegano_image = create_stegano_image(
        original_image=sep.join([expanduser('~'), "Downloads", "cover_image.png"]),
        data_to_hide=sep.join([expanduser('~'), "doc_to_hide.txt"]),
        cipher_key="JarrodCTaylor"
    )

    stegano_image.save(sep.join([expanduser('~'), "Downloads", "stegano_image.png"]))

Extract data
~~~~~~~~~~~~

.. code:: python

    from os.path import sep, expanduser

    from steganopy.api import extract_data_from_stegano_image

    extracted_data = extract_data_from_stegano_image(
        image=sep.join([expanduser('~'), "Downloads", "stegano_image.png"]),
        cipher_key="JarrodCTaylor"
    )

    with open(sep.join([expanduser('~'), "Downloads", "extracted_content.txt"]), "w") as f:
        f.write(extracted_data)

.. |BUILD Status| image:: https://travis-ci.org/JarrodCTaylor/steganopy.png?branch=master
   :target: https://travis-ci.org/JarrodCTaylor/steganopy
