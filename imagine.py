from PIL import Image
from gooey import Gooey, GooeyParser
from pathlib import Path


@Gooey(program_name="imagine", return_to_config=True, header_height=60)
def parse_args():
    desc = "Skalér og konvertér en eller flere billedfiler til jpg."
    input_files_msg = "Marker en eller flere filer, der skal konverteres"
    output_dir_msg = "Vælg eller opret mappe, hvor jpg-filerne skal gemmes"

    parser = GooeyParser(description=desc)
    parser.add_argument("input_files",
                        metavar="Vælg billedfil(er)",
                        help=input_files_msg,
                        widget="DirChooser")
                        # widget="MultiFileChooser")  # bug - upgrade later
    parser.add_argument("output_dir",
                        metavar="Gem jpg-fil(erne)",
                        help=output_dir_msg,
                        widget="DirChooser")
    parser.add_argument('-mw',
                        '--mwidth',
                        metavar="Maksimal billedbredde i pixels",
                        help="max_width of images in pixels")
    parser.add_argument('-mh',
                        '--mheight',
                        metavar="Maksimal billedhøjde i pixels",
                        help="max_height of images in pixels")
    # parser.add_argument('-f',
    #                     '--format',
    #                     metavar="Output format",
    #                     help="Choose output-format")
    parser.add_argument('-q',
                        '--quality',
                        metavar="JPG-kvalitet",
                        help="Choose quality of output-files. Defaults to 75%")
    return parser.parse_args()


def get_images(dir_object):
    # dir_objectis a Path-object
    files = []
    for obj in dir_object.rglob('*.*'):
        if obj.suffix.lower() in ['.png', '.jpg', '.jp2', '.jpeg', '.tiff', '.tif']:
            files.append(str(obj))
    return files


def read_image(file_path):
    return image.open(file_path)


def resize_image(file_path, max_height=None, max_width=None):
    # http://pillow.readthedocs.io/en/latest/reference/Image.html#PIL.Image.Image
    image = Image.open(file_path)

    # https://pillow.readthedocs.io/en/latest/reference/Image.html#PIL.Image.size
    width, height = image.size
    scaling_factor = 1

    # shrink if max-dimensions are smaller than img-dimensions
    if max_height and max_height/float(height) < scaling_factor:
        scaling_factor = max_height / float(height)

    if max_width and max_width/float(width) < scaling_factor:
        scaling_factor = max_width / float(width)

    # http://pillow.readthedocs.io/en/latest/reference/Image.html#PIL.Image.Image.resize 
    return image.resize((width / scaling_factor, height / scaling_factor))


def save_image(image, filename, quality):
    image.save(filename, quality=quality, optimize=True)


if __name__ == '__main__':
    args = parse_args()
    max_height = args.max_height if args.max_height else None
    max_width = args.max_width if args.max_width else None
    quality = 75 if not args.quality else args.quality

    print("Arguments parsed", flush=True)
    images = get_images(Path(args.input_files))
    print("Image(s) fetched", flush=True)
    print("Working with image(s)...", flush=True)
    for img_path in images:
        if max_height or max_width:
            infile = resize_image(img_path,
                                  max_height=max_height,
                                  max_width=max_width)

        else:
            infile = read_image(img_path)

        if args.output_dir:
            filename = img_path.slice[img_path.rindex('.'):] + ".jpg"
            filepath = '/'.join([args.output_dir, filename])
        else:
            filepath = img_path

        save_image(infile,
                   filename=filepath,
                   jpg_quality=quality)
    print("Done", flush=True)
    print("Click 'edit' to convert additional files.")
