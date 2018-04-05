from PIL import Image, ImageSequence
from gooey import Gooey, GooeyParser
from pathlib import Path


@Gooey(program_name="images2jpg", return_to_config=True, header_height=60)
def parse_args():
    desc = "Convert png, jpeg, bmp, jpeg 2000-files and more to (scaled) jpg-files."
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
    quality = args.quality or 75
    all_pages = True

    images = get_images(Path(args.input_dir))
    print("WARMING UP...", flush=True)

    errors = 0
    for path in images:
        image = Image.open(path)
        filename = path.stem + ".jpg"
        output_filename = Path(args.output_dir) / filename

        if max_height or max_width:
            image = resize_image(image, max_height=max_height, max_width=max_width)

        try:
            save_image(image, filename=output_filename, quality=int(quality))
        except KeyError:
            print("ERROR: Conversion skipped. Unable to determine output-format from filename: " + filename, flush=True)
            errors += 1
        except IOError:
            print("ERROR: Unable to convert file: " + path.name + ". Partial filedata may have been written to disc.", flush=True)
            errors += 1

    print("", flush=True)
    print("DONE", flush=True)
    print("Converted " + str(len(images) - errors) + " files", flush=True)
    if errors > 0:
        print("Unable to convert " + str(errors) + " files", flush=True)

    print("")
    print("ACTIONS")
    print("Click 'Edit' to convert additional files", flush=True)
    print("Click 'Restart' to re-run the job", flush=True)
    print("\n", flush=True)
