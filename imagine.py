from PIL import Image
from gooey import Gooey, GooeyParser
from pathlib import Path


@Gooey(program_name="images2jpg", return_to_config=True, header_height=60)
def parse_args():
    desc = "Scale and convert image-files to jpg-files."
    input_dir_msg = "Choose folder with image-files to convert"
    output_dir_msg = "Choose where to save jpg-files"

    parser = GooeyParser(description=desc)
    parser.add_argument("input_dir",
                        metavar="Choose input-folder",
                        help=input_dir_msg,
                        widget="DirChooser")
                        # widget="MultiFileChooser")  # bug - upgrade later
    parser.add_argument("output_dir",
                        metavar="Choose output-folder",
                        help=output_dir_msg,
                        widget="DirChooser")
    parser.add_argument('-mw',
                        '--mwidth',
                        metavar="Max width",
                        help="max_width of output-images (in pixels)")
    parser.add_argument('-mh',
                        '--mheight',
                        metavar="Max height",
                        help="max_height of output-images (in pixels)")
    parser.add_argument('-q',
                        '--quality',
                        metavar="Jpg-quality",
                        help="Choose output-quality (between 10 and 95). Defaults to 75")
    return parser.parse_args()


def get_images(dir_object):
    # dir_object is a Path-object
    files = []
    for obj in dir_object.glob('*.*'):
        if obj.is_file() and obj.suffix.lower() in ['.png', '.jpg', '.jp2', '.jpeg', '.tiff', '.tif']:
            files.append(obj)
    return files


def resize_image(image, max_height=None, max_width=None):
    # https://pillow.readthedocs.io/en/latest/reference/Image.html#PIL.Image.size
    width, height = image.size
    scaling_factor = 1

    # shrink if max-dimensions are smaller than img-dimensions
    if max_height and int(max_height) / height < scaling_factor:
        scaling_factor = int(max_height) / height

    if max_width and int(max_width) / width < scaling_factor:
        scaling_factor = int(max_width) / width

    # http://pillow.readthedocs.io/en/latest/reference/Image.html#PIL.Image.Image.resize 
    return image.resize((int(width * scaling_factor), int(height * scaling_factor)))


def save_image(image, filename, quality):
    image.save(filename, quality=quality, optimize=True)


if __name__ == '__main__':
    args = parse_args()
    max_height = args.mheight if args.mheight else None
    max_width = args.mwidth if args.mwidth else None
    # quality = 75 if not args.quality else args.quality
    quality = args.quality or 75

    images = get_images(Path(args.input_dir))
    print("Fetching images...", flush=True)
    print("Converting...", flush=True)

    for path in images:
        image = Image.open(path)
        if max_height or max_width:
            image = resize_image(image,
                                 max_height=max_height,
                                 max_width=max_width)

        filename = path.stem + ".jpg"
        save_image(image,
                   filename=Path(args.output_dir) / filename,
                   quality=int(quality))
        print("INFO: Converted " + str(path.name), flush=True)

    print("Done\n", flush=True)
    print("Click 'Edit' to convert additional files", flush=True)
    print("Click 'Restart' to re-run the job", flush=True)