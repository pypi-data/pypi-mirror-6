Rambo
=======
A command line sprite tool for smashing your images into sprites.

Includes `pypacker <http://jwezorek.com/2013/01/sprite-packing-in-python/>`_, written by Joe Wezorek.



Features
--------
* Automatic support for multiple sprite resolutions (based on folder names)
* pngcrush for a low-fat diet
* Produces an HTML test page so can preview your sprites
* Python, so it's blazing fast


Set up your images
------------------
You'll need to drop your sprite images in a sub-folder for each pixel aspect ratio.

::

  Eg, sprites/
        foo/           (the 1x has no prefix. Your sprite will be called this.)
        foo-0.75x/     (smaller than 1x for poxy androids. Use the same base-name `foo`)
        foo-1.5x/      (android pseudo-retina)
        foo-2x/        (true retina)
        bar/
        bar-2x/

Usage
-----
.. code::

    pip install rambo

Then run rambo from the command line:

.. code::

    rambo --input "images/sprites" --output "images" --csspath "css" --cssfile "_sprites.scss" --sasspath "sass/sprites" --testpage_dir "site" --testpage_name "test_page.html"

Arguments
~~~~~~~~~

.. code::

  -h, --help                show this help message and exit
  --input INPUT             Input directory, images/sprites
  --output OUTPUT           Output directory, images/
  --cssfile CSSFILE         CSS filename, _sprites.scss
  --csspath CSSPATH         CSS output path, css
  --sasspath SASSPATH       SaSS output path,  sass/sprites
  --testpage_dir TEST_DIR   Cheat sheet dir, site/
  --testpage_name TESTPAGE  Cheat sheet, cheat_sheet.html
