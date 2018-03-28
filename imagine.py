from PIL import image
from gooey import Gooey, GooeyParser
from pathlib import Path


@Gooey(program_name="convert2jpg",
       return_to_config=True,
       header_height=60)
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
    parser.add_argument('-q',
                        '--quality',
                        metavar="JPG-kvalitet",
                        help="Choose quality of output-files. Defaults to 95%")
    return parser.parse_args()


def get_images(dir_object):
    # dir_objectis a Path-object
    files = []
    for obj in dir_object.rglob('*.*'):
        if obj.suffix in ['.png', '.jpg', '.jp2', '.jpeg', '.tiff', '.tif']:
            files.append(str(obj))
    return files


def read_image(file_path):
    return image.read(file_path)


def resize_image(file_path, max_height=None, max_width=None):
    # https://docs.opencv.org/3.0-last-rst/modules/imgcodecs/doc/reading_and_writing_images.html?highlight=imread#cv2.imread
    cv_image = image.read(file_path)

    height, width = cv_image.shape[:2]
    scaling_factor = 1

    # shrink if img-dimentions are bigger than required
    if max_height and max_height/float(height) < scaling_factor:
        scaling_factor = max_height / float(height)

    if max_width and max_width/float(width) < scaling_factor:
        scaling_factor = max_width / float(width)

    # https://docs.opencv.org/3.0-last-rst/modules/imgproc/doc/geometric_transformations.html?highlight=resize#cv2.resize
    resized = cv2.resize(cv_image,
                         None,  # TODO: What is this param?
                         fx=scaling_factor,
                         fy=scaling_factor,
                         interpolation=cv2.INTER_AREA)

    return resized


def save_as_jpg(cv_image, filename, jpg_quality=95):
    # https://docs.opencv.org/3.0-last-rst/modules/imgcodecs/doc/reading_and_writing_images.html?highlight=imwrite#cv2.imwrite
    cv2.imwrite(filename,
                cv_image,
                [cv2.IMWRITE_JPEG_QUALITY, jpg_quality])


if __name__ == '__main__':
    args = parse_args()
    print("Arguments parsed")
    images = get_images(Path(args.input_files))
    print("Image(s) fetched")
    print("Working with image(s)...")
    for img_path in images:
        if args.get('max_height') or args.get('max_width'):
            infile = resize_image(img_path,
                                  max_height=args.get('max_height'),
                                  max_width=args.get('max_width'))

        else:
            infile = read_image(img_path)

        if args.get('output_dir'):
            filename = img_path.slice[img_path.rindex('.'):] + ".jpg"
            filepath = '/'.join([args.output_dir, filename])
        else:
            filepath = img_path
        save_as_jpg(infile,
                    filename=filepath,
                    jpg_quality=args.get('quality', 95))
