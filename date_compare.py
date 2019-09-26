import PIL.Image
from PIL.ExifTags import TAGS
from os import listdir, rename
from os.path import getmtime, isdir
from time import localtime, struct_time, strftime, strptime
import exiftool


class ImgTypeError(Exception):
    pass

class TimeStampError(Exception):
    pass

def list_all_img_dates(path, add_datestamp=False):
    """Function that takes either a directory or single image path and prints
    all available timestamps for each JPG, PNG, AAE, or MOV file for comparison.
    Optional argument allows the creation timestamp to be prepended to image(s)
    as they are processed (with confirmation prompt)."""
    # add functionality to rename files if desired.
    if isdir(path):
        if path[-1] != '/':
            path += '/'
        image_list = listdir(path)
        image_list.sort()
    else:
        # If path is only a single image instead of a directory, separate out
        # the image name from the path to conform to path + img convention in
        # rest of code. Create a length-one list with that image name to
        # loop through.
        single_image = path.split('/')[-1]
        path = path.split(single_image)[0]
        image_list = [single_image]

    for img in image_list:
        # print(img)
        img_ext = img.upper()[-4:]
        file_mod_time = strftime('%Y-%m-%dT%H%M%S', localtime(getmtime(path + img)))

        if img_ext == ".JPG" or img_ext == "JPEG":
            img_obj = PIL.Image.open(path + img)

            encoded_exif = img_obj._getexif()
            pil_metadata = {}
            for tag, value in encoded_exif.items():
                 decoded_key = TAGS.get(tag, tag)
                 if "DateTime" in decoded_key:
                     pil_metadata[decoded_key] = value

            with exiftool.ExifTool() as et:
                exiftool_metadata = et.get_metadata(path + img)

            # "*" indicates metadata most likely to represent actual creation time.
            print((img + ":\n"
                        "        file_mod_time:\t\t%s\n"
                        "        PIL-getexif DateTimeOriginal:\t%s\n"
                        "        PIL-getexif DateTimeDigitized:\t%s\n"
                        "        PIL-getexif DateTime:\t%s\n"
                        "        Exiftool EXIF:ModifyDate:\t%s\n"
                        "        Exiftool EXIF:DateTimeOriginal*:\t%s\n"
                        "        Exiftool EXIF:CreateDate:\t%s\n"
                        "        Exiftool Composite:SubSecCreateDate:\t%s\n"
                        "        Exiftool Composite:SubSecDateTimeOriginal:\t%s\n"
                        % (file_mod_time, pil_metadata.get('DateTimeOriginal'),
                            pil_metadata.get('DateTimeDigitized'),
                            pil_metadata.get('DateTime'),
                            exiftool_metadata.get('EXIF:ModifyDate'),
                            exiftool_metadata.get('EXIF:DateTimeOriginal'),
                            exiftool_metadata.get('EXIF:CreateDate'),
                            exiftool_metadata.get('Composite:SubSecCreateDate'),
                            exiftool_metadata.get('Composite:SubSecDateTimeOriginal')
                            )).expandtabs(28))



        elif img_ext == ".MOV":
            with exiftool.ExifTool() as et:
                metadata = et.get_metadata(path + img)
                qt_create_date = metadata.get("QuickTime:CreateDate")
                qt_mod_date = metadata.get("QuickTime:ModifyDate")
                qt_trk_create_date = metadata.get("QuickTime:TrackCreateDate")
                qt_trk_mod_date = metadata.get("QuickTime:TrackModifyDate")
                qt_med_create_date = metadata.get("QuickTime:MediaCreateDate")
                qt_med_mod_date = metadata.get("QuickTime:MediaModifyDate")
                qt_creation_date = metadata.get("QuickTime:CreationDate")


            # "*" indicates metadata most likely to represent actual creation time.
            print((img + ":\n"
                        "        file_mod_time:\t\t%s\n"
                        "        EXIFtool QuickTime:CreateDate:\t%s\n"
                        "        EXIFtool QuickTime:ModifyDate:\t%s\n"
                        "        EXIFtool QuickTime:TrackCreateDate:\t%s\n"
                        "        EXIFtool QuickTime:TrackModifyDate:\t%s\n"
                        "        EXIFtool QuickTime:MediaCreateDate:\t%s\n"
                        "        EXIFtool QuickTime:MediaModifyDate:\t%s\n"
                        "        EXIFtool QuickTime:CreationDate*:\t%s\n"
                        % (file_mod_time,
                        qt_create_date, qt_mod_date,
                        qt_trk_create_date, qt_trk_mod_date,
                        qt_med_create_date, qt_med_mod_date,
                        qt_creation_date)).expandtabs(28))

        elif img_ext == ".MP4":
            with exiftool.ExifTool() as et:
                metadata = et.get_metadata(path + img)
                qt_create_date = metadata.get("QuickTime:CreateDate")
                qt_mod_date = metadata.get("QuickTime:ModifyDate")
                qt_trk_create_date = metadata.get("QuickTime:TrackCreateDate")
                qt_trk_mod_date = metadata.get("QuickTime:TrackModifyDate")
                qt_med_create_date = metadata.get("QuickTime:MediaCreateDate")
                qt_med_mod_date = metadata.get("QuickTime:MediaModifyDate")


            # "*" indicates metadata most likely to represent actual creation time.
            print((img + ":\n"
                        "        file_mod_time:\t\t%s\n"
                        "        EXIFtool QuickTime:CreateDate*:\t%s\n"
                        "        EXIFtool QuickTime:ModifyDate:\t%s\n"
                        "        EXIFtool QuickTime:TrackCreateDate:\t%s\n"
                        "        EXIFtool QuickTime:TrackModifyDate:\t%s\n"
                        "        EXIFtool QuickTime:MediaCreateDate:\t%s\n"
                        "        EXIFtool QuickTime:MediaModifyDate:\t%s\n"
                        "Dates 4 hrs ahead because no time zone adjustment."
                        % (file_mod_time,
                        qt_create_date, qt_mod_date,
                        qt_trk_create_date, qt_trk_mod_date,
                        qt_med_create_date, qt_med_mod_date)).expandtabs(28))


        elif img_ext == ".PNG":
            img_obj = PIL.Image.open(path + img)

            # encoded_exif = getattr(img_obj, '_getexif', lambda: None)()
            date_created = img_obj.info.get('XML:com.adobe.xmp')
            if date_created:
                date_created = date_created.split("<photoshop:DateCreated>")[1].split("</photoshop:DateCreated>")[0]

            with exiftool.ExifTool() as et:
                metadata = et.get_metadata(path + img)
                xmp_date_created = metadata.get("XMP:DateCreated")

            # "*" indicates metadata most likely to represent actual creation time.
            print((img + ":\n"
                        "        file_mod_time:\t\t%s\n"
                        "        PIL-info date_created:\t%s\n"
                        "        EXIFtool XMP:DateCreated*:\t%s\n"
                        % (file_mod_time, date_created, xmp_date_created)).expandtabs(28))

        elif img_ext == ".AAE":
            img_obj = open(path + img, 'r')

            # encoded_exif = getattr(img_obj, '_getexif', lambda: None)()
            for line in img_obj:
                if '<date>' in line:
                    adjustmentTimestamp = line.split("<date>")[1].split("Z</date>")[0]

            with exiftool.ExifTool() as et:
                metadata = et.get_metadata(path + img)
                adj_time = metadata.get("PLIST:AdjustmentTimestamp")

            # "*" indicates metadata most likely to represent actual creation time.
            print((img + "\n"
                        "        file_mod_time:\t\t%s\n"
                        "        AAEparse adjustmentTimestamp:\t%s\n"
                        "        EXIFtool PLIST:AdjustmentTimestamp*:\t%s\n"
                        % (file_mod_time, adjustmentTimestamp, adj_time)).expandtabs(28))
        else:
            raise ImgTypeError("Invalid image type encountered: %s" % img)

        # Add datestamp to image name if desired.
        if add_datestamp:
            # test rename operation to see if mtime changes
            # need a variable name that stores images best guess-time. look at
            # get_img_date end code.
            img_path = path + img
            # This requires redundant use of exiftool, but not a big deal
            # if runtime isn't bad.
            datestamp = strftime('%Y-%m-%d', get_img_date(img_path))
            datestamp_long = strftime('%Y-%m-%dT%H%M%S', get_img_date(img_path))

            if datestamp_long in img:
                # rename previously-generated longer-stamped names
                img_shortened = img.replace(datestamp_long, datestamp)
                rename(img_path, path + img_shortened)
            elif datestamp in img:
                # Don't prepend redundant datestamp.
                print("%s already has correct datestamp." % img)
                continue
            elif img[:4] != 'IMG_':
                # Detect presence of non-standard naming (could be pre-existing alternate datestamp)
                # print("%s has non-standard naming. Skipping." % img)
                rename_choice = input("%s has non-standard naming. "
                        "Add %s datestamp anyway? [y/n]\n>" % (img, datestamp))
                if rename_choice.lower() == 'y':
                    rename(img_path, path + datestamp + '_' + img)
                else:
                    print("Skipped %s" % img)
            else:
                rename(img_path, path + datestamp + '_' + img)


def get_img_date(img_path):
    """Function that prints best available timestamp for any single JPG, PNG,
    AAE, or MOV file located at img_path."""
    # modify to look for each metadata type and fall back on mtime if needed.
    with exiftool.ExifTool() as et:
        img_ext = img_path.upper()[-4:]
        metadata = et.get_metadata(img_path)

        # Different files have different names for the creation date in the metadata.
        if img_ext == ".JPG" or img_ext == "JPEG":
            create_time = metadata.get("EXIF:DateTimeOriginal")
            format = "%Y:%m:%d %H:%M:%S"
            # ex. 2019:08:26 09:11:21
        elif img_ext == ".MOV":
            create_time = metadata.get("QuickTime:CreationDate")
            # non-standard format - adjust manually before passing to strftime
            # ex. 2019:08:26 19:22:27-04:00
            create_time = create_time[0:22] + create_time[23:]
            # Now formatted this way: 2019:08:26 19:22:27-0400
            format = "%Y:%m:%d %H:%M:%S%z"
        elif img_ext == ".MP4":
            create_time = metadata.get("QuickTime:CreateDate")
            format = "%Y:%m:%d %H:%M:%S"
            # MP4 metadata isn't in correct time zone.
            create_time = tz_adjust(create_time, format, 4)
            # ex. 2019:08:26 03:51:19
        elif img_ext == ".PNG":
            create_time = metadata.get("XMP:DateCreated")
            format = "%Y:%m:%d %H:%M:%S"
            # ex. 2019:08:26 03:51:19
        elif img_ext == ".AAE":
            create_time = metadata.get("PLIST:AdjustmentTimestamp")
            format = "%Y:%m:%d %H:%M:%SZ"
            # ex. 2019:07:05 12:46:46Z
        else:
            raise ImgTypeError("Unexpected extension encountered at " + img_path)


        if create_time:
            create_time_obj = strptime(create_time, format)
            # print(create_time_obj)
            return create_time_obj
        else:
            # Fall back on fs mod time if more precise metadata unavailable.
            file_mod_time_obj = localtime(getmtime(img_path))
            # print(file_mod_time_obj)
            return file_mod_time_obj

def tz_adjust(time_str, format, shift):
    """Function to adjust timezone of a datestamp."""
    time_obj = strptime(time_str, format)

    ts_list = list(time_obj)
    if ts_list[3] <= shift:
        "Function doesn't handle date adjustments resulting from hr change."
        raise TimeStampError("Changing time stamp would require date change.")
    else:
        ts_list[3] -= shift         # EST
        time_obj_adjusted = struct_time(tuple(ts_list))
        time_str_adjusted = strftime(format, time_obj_adjusted)
        return time_str_adjusted


def meta_dump(img_path):
    """Display all available exiftool data."""
    with exiftool.ExifTool() as et:
        metadata = et.get_metadata(img_path)
        for key in metadata:
             print(str(key) + ": " + str(metadata[key]))

# References:
# https://www.blog.pythonlibrary.org/2010/03/28/getting-photo-metadata-exif-using-python/
# https://stackoverflow.com/questions/4764932/in-python-how-do-i-read-the-exif-data-for-an-image#4765242
# https://gist.github.com/erans/983821#comment-377080
# https://stackoverflow.com/questions/48631908/python-extract-metadata-from-png#51249611
# https://www.vice.com/en_us/article/aekn58/hack-this-extra-image-metadata-using-python

# https://stackoverflow.com/questions/21355316/getting-metadata-for-mov-video#21395803
# https://github.com/smarnach/pyexiftool
# https://smarnach.github.io/pyexiftool/
# https://sno.phy.queensu.ca/~phil/exiftool/



###########################
###### Example output:

# AAE
# >>> with exiftool.ExifTool() as et:
# ...     metadata = et.get_metadata([filepath])
# ...
# >>> for key in metadata:
# ...     print(str(key) + ": " + str(metadata[key]))
# ...
# SourceFile: [filepath]
# ExifTool:ExifToolVersion: 11.65
# File:FileName: IMG_7611.AAE
# File:Directory: [folder path]
# File:FileSize: 829
# File:FileModifyDate: 2019:07:05 10:32:50-04:00
# File:FileAccessDate: 2019:09:08 21:45:01-04:00
# File:FileInodeChangeDate: 2019:09:08 21:45:01-04:00
# File:FilePermissions: 700
# File:FileType: AAE
# File:FileTypeExtension: AAE
# File:MIMEType: application/vnd.apple.photos
# PLIST:AdjustmentBaseVersion: 0
# PLIST:AdjustmentData: (Binary data 150 bytes, use -b option to extract)
# PLIST:AdjustmentEditorBundleID: com.apple.mobileslideshow
# PLIST:AdjustmentFormatIdentifier: com.apple.photo
# PLIST:AdjustmentFormatVersion: 1.4
# PLIST:AdjustmentRenderTypes: 0
# PLIST:AdjustmentTimestamp: 2019:07:05 12:46:46Z



# PNG
# >>> with exiftool.ExifTool() as et:
# ...     metadata = et.get_metadata("[filepath])
# ...
# >>> for key in metadata:
# ...     print(str(key) + ": " + str(metadata[key]))
# ...
# SourceFile: [filepath]
# ExifTool:ExifToolVersion: 11.65
# File:FileName: IMG_8552.PNG
# File:Directory: [folder path]
# File:FileSize: 85705
# File:FileModifyDate: 2019:09:02 00:06:12-04:00
# File:FileAccessDate: 2019:09:15 09:16:32-04:00
# File:FileInodeChangeDate: 2019:09:15 08:40:01-04:00
# File:FilePermissions: 700
# File:FileType: PNG
# File:FileTypeExtension: PNG
# File:MIMEType: image/png
# PNG:ImageWidth: 750
# PNG:ImageHeight: 1334
# PNG:BitDepth: 8
# PNG:ColorType: 2
# PNG:Compression: 0
# PNG:Filter: 0
# PNG:Interlace: 0
# PNG:SRGBRendering: 0
# XMP:XMPToolkit: XMP Core 5.4.0
# XMP:DateCreated: 2019:08:26 03:51:19
# XMP:UserComment: Screenshot
# Composite:ImageSize: 750 1334
# Composite:Megapixels: 1.0005




# MOV
# >>> with exiftool.ExifTool() as et:
# ...     metadata = et.get_metadata("[filepath])
# ...
# >>> for key in metadata:
# ...     print(str(key) + ": " + str(metadata[key]))
# ...
# SourceFile: [filepath]
# ExifTool:ExifToolVersion: 11.65
# ExifTool:Warning: [minor] The ExtractEmbedded option may find more tags in the movie data
# File:FileName: IMG_8621.MOV
# File:Directory: [folder path]
# File:FileSize: 77769964
# File:FileModifyDate: 2019:08:26 23:26:42-04:00
# File:FileAccessDate: 2019:09:15 09:16:34-04:00
# File:FileInodeChangeDate: 2019:09:15 08:40:01-04:00
# File:FilePermissions: 700
# File:FileType: MOV
# File:FileTypeExtension: MOV
# File:MIMEType: video/quicktime
# QuickTime:MajorBrand: qt
# QuickTime:MinorVersion: 0.0.0
# QuickTime:CompatibleBrands: ['qt  ']
# QuickTime:MovieDataSize: 77750760
# QuickTime:MovieDataOffset: 36
# QuickTime:MovieHeaderVersion: 0
# QuickTime:CreateDate: 2019:08:26 23:24:43
# QuickTime:ModifyDate: 2019:08:26 23:24:43
# QuickTime:TimeScale: 600
# QuickTime:Duration: 39.5466666666667
# QuickTime:PreferredRate: 1
# QuickTime:PreferredVolume: 1
# QuickTime:PreviewTime: 0
# QuickTime:PreviewDuration: 0
# QuickTime:PosterTime: 0
# QuickTime:SelectionTime: 0
# QuickTime:SelectionDuration: 0
# QuickTime:CurrentTime: 0
# QuickTime:NextTrackID: 5
# QuickTime:TrackHeaderVersion: 0
# QuickTime:TrackCreateDate: 2019:08:26 23:24:43
# QuickTime:TrackModifyDate: 2019:08:26 23:24:43
# QuickTime:TrackID: 1
# QuickTime:TrackDuration: 39.5466666666667
# QuickTime:TrackLayer: 0
# QuickTime:TrackVolume: 1
# QuickTime:ImageWidth: 1920
# QuickTime:ImageHeight: 1080
# QuickTime:CleanApertureDimensions: 1920 1080
# QuickTime:ProductionApertureDimensions: 1920 1080
# QuickTime:EncodedPixelsDimensions: 1920 1080
# QuickTime:GraphicsMode: 64
# QuickTime:OpColor: 32768 32768 32768
# QuickTime:CompressorID: avc1
# QuickTime:SourceImageWidth: 1920
# QuickTime:SourceImageHeight: 1080
# QuickTime:XResolution: 72
# QuickTime:YResolution: 72
# QuickTime:CompressorName: H.264
# QuickTime:BitDepth: 24
# QuickTime:VideoFrameRate: 29.9787827099888
# QuickTime:Balance: 0
# QuickTime:AudioFormat: mp4a
# QuickTime:AudioBitsPerSample: 16
# QuickTime:AudioSampleRate: 44100
# QuickTime:LayoutFlags: 100
# QuickTime:AudioChannels: 1
# QuickTime:PurchaseFileFormat: mp4a
# QuickTime:MatrixStructure: 1 0 0 0 1 0 0 0 1
# QuickTime:ContentDescribes: 1
# QuickTime:MediaHeaderVersion: 0
# QuickTime:MediaCreateDate: 2019:08:26 23:24:43
# QuickTime:MediaModifyDate: 2019:08:26 23:24:43
# QuickTime:MediaTimeScale: 600
# QuickTime:MediaDuration: 91.065
# QuickTime:MediaLanguageCode: und
# QuickTime:GenMediaVersion: 0
# QuickTime:GenFlags: 0 0 0
# QuickTime:GenGraphicsMode: 64
# QuickTime:GenOpColor: 32768 32768 32768
# QuickTime:GenBalance: 0
# QuickTime:HandlerClass: dhlr
# QuickTime:HandlerVendorID: appl
# QuickTime:HandlerDescription: Core Media Data Handler
# QuickTime:MetaFormat: mebx
# QuickTime:HandlerType: mdta
# QuickTime:Make: Apple
# QuickTime:Model: iPhone 6s
# QuickTime:Software: 12.4
# QuickTime:CreationDate: 2019:08:26 19:22:27-04:00
# Composite:ImageSize: 1920 1080
# Composite:Megapixels: 2.0736
# Composite:AvgBitrate: 15728407
# Composite:Rotation: 90




# JPG
# >>> with exiftool.ExifTool() as et:
# ...     metadata = et.get_metadata([filepath])
#
# >>> for key in metadata:
# ...     print(str(key) + ": " + str(metadata[key]))
# ...
# SourceFile: [filepath]
# ExifTool:ExifToolVersion: 11.65
# File:FileName: IMG_8563.JPG
# File:Directory: [folder path]
# File:FileSize: 2340281
# File:FileModifyDate: 2019:08:26 09:11:21-04:00
# File:FileAccessDate: 2019:09:15 09:16:33-04:00
# File:FileInodeChangeDate: 2019:09:15 08:40:01-04:00
# File:FilePermissions: 700
# File:FileType: JPEG
# File:FileTypeExtension: JPG
# File:MIMEType: image/jpeg
# File:ExifByteOrder: MM
# File:ImageWidth: 4032
# File:ImageHeight: 3024
# File:EncodingProcess: 0
# File:BitsPerSample: 8
# File:ColorComponents: 3
# File:YCbCrSubSampling: 2 2
# EXIF:Make: Apple
# EXIF:Model: iPhone 6s
# EXIF:Orientation: 1
# EXIF:XResolution: 72
# EXIF:YResolution: 72
# EXIF:ResolutionUnit: 2
# EXIF:Software: 12.4
# EXIF:ModifyDate: 2019:08:26 09:11:21
# EXIF:YCbCrPositioning: 1
# EXIF:ExposureTime: 0.01666666667
# EXIF:FNumber: 2.2
# EXIF:ExposureProgram: 2
# EXIF:ISO: 32
# EXIF:ExifVersion: 0221
# EXIF:DateTimeOriginal: 2019:08:26 09:11:21
# EXIF:CreateDate: 2019:08:26 09:11:21
# EXIF:ComponentsConfiguration: 1 2 3 0
# EXIF:ShutterSpeedValue: 0.0166649999460157
# EXIF:ApertureValue: 2.20000000038133
# EXIF:BrightnessValue: 4.780345489
# EXIF:ExposureCompensation: 0
# EXIF:MeteringMode: 5
# EXIF:Flash: 24
# EXIF:FocalLength: 4.15
# EXIF:SubjectArea: 2015 1511 2217 1330
# EXIF:SubSecTimeOriginal: 184
# EXIF:SubSecTimeDigitized: 184
# EXIF:FlashpixVersion: 0100
# EXIF:ColorSpace: 1
# EXIF:ExifImageWidth: 4032
# EXIF:ExifImageHeight: 3024
# EXIF:SensingMethod: 2
# EXIF:SceneType: 1
# EXIF:ExposureMode: 0
# EXIF:WhiteBalance: 0
# EXIF:FocalLengthIn35mmFormat: 29
# EXIF:SceneCaptureType: 0
# EXIF:LensInfo: 4.15 4.15 2.2 2.2
# EXIF:LensMake: Apple
# EXIF:LensModel: iPhone 6s back camera 4.15mm f/2.2
# EXIF:Compression: 6
# EXIF:ThumbnailOffset: 1772
# EXIF:ThumbnailLength: 10680
# EXIF:ThumbnailImage: (Binary data 10680 bytes, use -b option to extract)
# MakerNotes:RunTimeFlags: 1
# MakerNotes:RunTimeValue: 34717646045291
# MakerNotes:RunTimeScale: 1000000000
# MakerNotes:RunTimeEpoch: 0
# MakerNotes:AccelerationVector: -0.9088873265 -0.01614983752 -0.4305499197
# Composite:RunTimeSincePowerUp: 34717.646045291
# Composite:Aperture: 2.2
# Composite:ImageSize: 4032 3024
# Composite:Megapixels: 12.192768
# Composite:ScaleFactor35efl: 6.98795180722891
# Composite:ShutterSpeed: 0.01666666667
# Composite:SubSecCreateDate: 2019:08:26 09:11:21.184
# Composite:SubSecDateTimeOriginal: 2019:08:26 09:11:21.184
# Composite:CircleOfConfusion: 0.00429972350378608
# Composite:FOV: 63.6549469203797
# Composite:FocalLength35efl: 29
# Composite:HyperfocalDistance: 1.8206773258829
# Composite:LightValue: 9.82575383259457



# MP4
# ExifTool:ExifToolVersion: 11.65
# File:FileName: IMG_9088.MP4
# File:Directory: /media/veracrypt11/BU_Data/iPhone_Pictures/TEST/special_cases
# File:FileSize: 612230
# File:FileModifyDate: 2019:09:19 23:18:17-04:00
# File:FileAccessDate: 2019:09:23 22:38:25-04:00
# File:FileInodeChangeDate: 2019:09:23 22:38:24-04:00
# File:FilePermissions: 600
# File:FileType: MP4
# File:FileTypeExtension: MP4
# File:MIMEType: video/mp4
# QuickTime:MajorBrand: mp42
# QuickTime:MinorVersion: 0.0.1
# QuickTime:CompatibleBrands: ['mp41', 'mp42', 'isom']
# QuickTime:MovieDataSize: 608775
# QuickTime:MovieDataOffset: 44
# QuickTime:MovieHeaderVersion: 0
# QuickTime:CreateDate: 2019:09:18 18:05:52
# QuickTime:ModifyDate: 2019:09:18 18:05:53
# QuickTime:TimeScale: 600
# QuickTime:Duration: 6.60666666666667
# QuickTime:PreferredRate: 1
# QuickTime:PreferredVolume: 1
# QuickTime:PreviewTime: 0
# QuickTime:PreviewDuration: 0
# QuickTime:PosterTime: 0
# QuickTime:SelectionTime: 0
# QuickTime:SelectionDuration: 0
# QuickTime:CurrentTime: 0
# QuickTime:NextTrackID: 2
# QuickTime:TrackHeaderVersion: 0
# QuickTime:TrackCreateDate: 2019:09:18 18:05:52
# QuickTime:TrackModifyDate: 2019:09:18 18:05:53
# QuickTime:TrackID: 1
# QuickTime:TrackDuration: 6.60666666666667
# QuickTime:TrackLayer: 0
# QuickTime:TrackVolume: 1
# QuickTime:MatrixStructure: 1 0 0 0 1 0 0 0 1
# QuickTime:ImageWidth: 272
# QuickTime:ImageHeight: 480
# QuickTime:MediaHeaderVersion: 0
# QuickTime:MediaCreateDate: 2019:09:18 18:05:52
# QuickTime:MediaModifyDate: 2019:09:18 18:05:53
# QuickTime:MediaTimeScale: 600
# QuickTime:MediaDuration: 6.60666666666667
# QuickTime:MediaLanguageCode: und
# QuickTime:HandlerType: vide
# QuickTime:HandlerDescription: Core Media Video
# QuickTime:GraphicsMode: 0
# QuickTime:OpColor: 0 0 0
# QuickTime:CompressorID: avc1
# QuickTime:SourceImageWidth: 272
# QuickTime:SourceImageHeight: 480
# QuickTime:XResolution: 72
# QuickTime:YResolution: 72
# QuickTime:BitDepth: 24
# QuickTime:ColorRepresentation: nclx 6 1 6
# QuickTime:VideoFrameRate: 29.6670030272452
# Composite:ImageSize: 272 480
# Composite:Megapixels: 0.13056
# Composite:AvgBitrate: 737164
# Composite:Rotation: 0









#
# from PIL import Image
# from PIL.ExifTags import TAGS
# ret = {}
# i = Image.open('IMG_8559.JPG')
# info = i._getexif()
#
# for tag, value in info.items():
#      decoded = TAGS.get(tag, tag)
#      ret[decoded] = value
#      print(decoded)
#      print(value)
