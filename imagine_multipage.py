from PIL import Image, ImageSequence
from gooey import Gooey, GooeyParser
from pathlib import Path


@Gooey(program_name="multipage_images2jpg", return_to_config=True, header_height=60)
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
        if obj.suffix.lower() in ['.png', '.jpg', '.jp2', '.jpeg', '.tiff', '.tif']:
            files.append(obj)
    return files


if __name__ == '__main__':
    args = parse_args()
    max_height = args.mheight if args.mheight else None
    max_width = args.mwidth if args.mwidth else None

    images = get_images(Path(args.input_dir))
    print("Warming up...")
    for path in images:
        image = Image.open(path)
        filename = path.stem + ".jpg"
        output_filename = Path(args.output_dir) / filename

        if image.format.lower() in ['tif', 'tiff'] and image.n_frames > 1:
            for i, page in enumerate(ImageSequence.Iterator(image)):
                pagename = path.stem + "_%d.jpg" % i
                iterated_pagename = Path(args.output_dir) / pagename
                print(page)
                if page.mode in ['P', 'I;16', 'I;16B']:
                    page.convert('RGB').save(iterated_pagename)
                else:
                    page.save(iterated_pagename)

                print("INFO: Converted subpage #" + str(i), flush=True)
        else:
            print(image)
            if image.mode in ['P', 'I;16', 'I;16B']:
                image.convert('RGB').save(output_filename)
            else:
                image.save(output_filename)
                
    print("Done\n", flush=True)
    print("Click 'Edit' to convert additional files", flush=True)
    print("Click 'Restart' to re-run the job", flush=True)