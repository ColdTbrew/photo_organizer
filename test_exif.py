import sys
import exifread

def print_exif(file_path):
    with open(file_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)
        if not tags:
            print("No EXIF data found.")
            return
        for tag in sorted(tags.keys()):
            print(f"{tag}: {tags[tag]}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python exif_dump.py <image_file>")
        sys.exit(1)
    print_exif(sys.argv[1])



#python exif_dump.py /path/to/your/image.jpg