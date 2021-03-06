import os
import time
from tqdm import tqdm

import date_compare
from pic_categorize_tool import copy_to_target
from pic_offload_tool import RawOffloadGroup



class OrganizeFolderError(Exception):
    pass


# Phase 2: Organize files by date into dated directory structure.
# Creates new dated folders where needed.
# Prepends timestamps to img names.

# Instantiate an OrganizedGroup instance with bu_root_path then call its
# run_org() method.

class OrganizedGroup(object):
    """Represents date-organized directory structure. Contains YrDir objects
    which in turn contain MoDir objects."""
    def __init__(self, bu_root_path, buffer_root):
        self.bu_root_path = bu_root_path
        self.date_root_path = self.bu_root_path + "Organized/"
        self.buffer_root_path = buffer_root
        # Double-check Organized folder is there.
        if not os.path.exists(self.date_root_path):
            raise OrganizeFolderError("Organized dir not found at %s! "
                        "Pics not organized. Terminating" % self.date_root_path)
        # Initialize object dictionary.
        self.yr_objs = {}

        # Instantiate year objects.
        yr_list = self.get_yr_list()
        for yr in yr_list:
            self.make_year(yr)

    def get_root_path(self):
        return self.date_root_path

    def get_buffer_root_path(self):
        return self.buffer_root_path

    def get_yr_list(self):
        # Refresh date_root_path every time in case dir changes.
        year_list = os.listdir(self.get_root_path())
        year_list.sort()
        return year_list

    def get_yr_objs(self):
        return self.yr_objs

    def get_latest_yrs(self):
        """Returns most recent year or two years if more than one present."""
        if len(self.get_yr_list()) > 1:
            latest_yr_names = self.get_yr_list()[-2:]
            return [str(self.yr_objs.get(latest_yr_names[0])),
                    str(self.yr_objs.get(latest_yr_names[1]))]
        else:
            latest_yr_name = self.get_yr_list()[-1]
            return [str(self.yr_objs.get(latest_yr_name))]

    def make_year(self, year):
        # check that year doesn't already exist in list
        if year in self.get_yr_objs():
            raise OrganizeFolderError("Tried to make year object for %s, "
                                "but already exists in Organized directory."
                                    % (self.year_name))
        else:
            # put into object dictionary
            self.yr_objs[year] = YearDir(year, self)

    def insert_img(self, img_orig_path, man_img_time=False):
        # Allow a manually-specified img_time to be passed and substituted.
        if man_img_time:
            img_time = man_img_time
            bypass_age_warn = True
        else:
            (img_time, bypass_age_warn) = date_compare.get_img_date_plus(
                                            img_orig_path, skip_unknown=False)

        yr_str = str(img_time.tm_year)
        mo_str = str(img_time.tm_mon)

        # print("DEBUG")
        # print("get_latest_yrs returns:")
        # print(self.get_latest_yrs())
        # print("\nyr_str in self.get_latest_yrs()?")
        # print(yr_str in self.get_latest_yrs())
        #
        # print("\nbypass warning?")
        # print(bypass_age_warn)
        # print("\nyr_str > self.get_latest_yrs()[-1]?")
        # print(yr_str > self.get_latest_yrs()[-1])
        # print("\nman_img_time?")
        # print(man_img_time)



        if yr_str in self.get_latest_yrs():
            # Proceed as normal for this year and last
            self.yr_objs[yr_str].insert_img(img_orig_path, img_time,
                                                                bypass_age_warn)
        elif yr_str > self.get_latest_yrs()[-1]:
            # If the image is from a later year than the existing folders,
            # make new year object.
            self.make_year(yr_str)
            NewYr = self.yr_objs[yr_str]
            NewYr.insert_img(img_orig_path, img_time, bypass_age_warn)
        elif man_img_time:
            # This is the same as a condition above, but the intervening elif
            # should instead run if it evaluates true. A new manually-specified
            # date might not be present in yr_objs dir.
            self.yr_objs[yr_str].insert_img(img_orig_path, img_time,
                                                                bypass_age_warn)
        else:
            print("Attempted to pull image into %s-%s dir, "
                                "but a more recent year dir exists, so "
                                "timestamp may be wrong.\nFallback bypasses "
                                "warning and copies into older dir anyway."
                                                        % (yr_str, mo_str))

            man_img_time_struct = date_compare.spec_manual_time(img_orig_path)
            if man_img_time_struct:
                # If user entered a date:
                self.insert_img(img_orig_path, man_img_time_struct)
                # bypass_age_warn will be set True within function.
            elif yr_str in self.get_yr_list():
                # If user chose fallback but still in valid years, continue
                # with operation anyway
                self.yr_objs[yr_str].insert_img(img_orig_path, img_time,
                                                        bypass_age_warn=True)
            else:
                # year directory doesn't exist yet, so have make it.
                self.make_year(yr_str)
                self.yr_objs[yr_str].insert_img(img_orig_path, img_time,
                                                        bypass_age_warn=True)

    def run_org(self):
        ROG = RawOffloadGroup(self.bu_root_path)

        LastRawOffload = ROG.get_latest_offload_obj()
        src_APPLE_folders = LastRawOffload.list_APPLE_folders()

        for n, folder in enumerate(src_APPLE_folders):
            print("Organizing from raw offload folder %s/%s (%s of %s)" %
            (LastRawOffload.get_dir_name(), folder,
                                str(n+1), len(src_APPLE_folders)))

            for img in tqdm(LastRawOffload.APPLE_contents(folder)):
                full_img_path = LastRawOffload.APPLE_folder_path(folder) + img
                self.insert_img(full_img_path)

        print("\nCategorization buffer populated.")

    def __repr__(self):
        return "OrganizedGroup object with path:\n\t" + self.get_root_path()


class YearDir(object):
    def __init__(self, year_name, OrgGroup):
        """Represents directory w/ year label that exists inside date-organized
        directory structure. Contains MoDir objects."""
        self.year_name = year_name
        self.year_path = OrgGroup.get_root_path() + self.year_name + '/'
        self.OrgGroup = OrgGroup

        if not self.year_name in OrgGroup.get_yr_list():
            os.mkdir(self.year_path)
        # Create dict of months.
        # This will contain all directories transferred to in this job.
        self.mo_objs = {}

        # Create set to hold month directories (names) to copy to without
        # prompt. This is sometimes necessary when image naming puts new photo
        # at beginning of queue and causes older photos to run "older month"
        # prompt repeatedly.
        self.no_prompt_months = set()
        # Run get_latest_mo in case it hasn't been run yet so latest_mo obj
        # is created. Add to to no_prompt_months set.
        self.og_latest_mo = self.get_latest_mo()
        if self.og_latest_mo:
            self.no_prompt_months.add(self.og_latest_mo.get_yrmon_name())

    def get_yr_path(self):
        return self.year_path

    def get_mo_list(self):
        mo_list = os.listdir(self.year_path)
        mo_list.sort()
        return mo_list

    def get_mo_objs(self):
        return self.mo_objs

    def get_latest_mo(self):
        if not self.get_mo_list():
            # If there are no months yet, return None.
            return None
        elif not self.mo_objs:
            # If there are months in the list but not in the dict, make latest
            # month now and return it.
            latest_mo_name = self.get_mo_list()[-1]
            self.make_yrmonth(latest_mo_name)
            return self.mo_objs.get(latest_mo_name)
        else:
            # If there are months in the directory, and the object dictionary
            # is non-empty, then the latest month should be in there.
            latest_mo_name = self.get_mo_list()[-1]
            return self.mo_objs.get(latest_mo_name)

    def make_yrmonth(self, yrmonth):
        # chck that month doesn't already exist in list
        if yrmonth in self.mo_objs:
            raise OrganizeFolderError("Tried to make month object for %s, "
                                        "but already exists in YearDir."
                                        % (yrmonth))
        else:
            self.mo_objs[yrmonth] = MoDir(yrmonth, self)

    def insert_img(self, img_orig_path, img_time, bypass_age_warn=False):
        if ".AAE" in os.path.basename(img_orig_path):
            # Don't copy AAE files into date-organized folders or cat buffer.
            # They will still exist in raw, but it doesn't add any value to copy
            # them elsewhere. They can also have dates that don't match the
            # corresponding img/vid, causing confusion.
            return

        elif os.path.basename(img_orig_path)[:5] == "IMG_E":
            # Look for any original/edited pairs in all org dirs used so far.
            # "IMG_E" files appear later in sorted order than originals, so
            # the originals are transferred first.
            # Can't assume datestamp is the same. Could have edited later.
            target_img_num = os.path.splitext(
                                        os.path.basename(img_orig_path))[0][-4:]

            for month in self.mo_objs.keys():
                mo_obj = self.mo_objs[month]
                for img_name in mo_obj.get_img_list():
                    # If number that follows the "IMG_" or "IMG_E" matches, find
                    # and discard the original (remains in raw_offload folder).
                    if os.path.splitext(img_name)[0][-4:] == target_img_num:
                        # Replace "IMG_E" img_time with original's datestamp.
                        img_time = time.strptime(img_name.split("_")[0],
                                                                    "%Y-%m-%d")
                        print("Keeping edited file %s and removing original "
                           "%s." % (os.path.basename(img_orig_path), img_name))
                        # Remove from both date-org folder and cat buffer.
                        os.remove(os.path.join(mo_obj.get_mo_path(), img_name))
                        os.remove(os.path.join(
                                self.OrgGroup.get_buffer_root_path(), img_name))
                        break
            # Continue to next conditional. Edited ("IMG_E") file is xfered.

        yr_str = str(img_time.tm_year)
        # Have to zero-pad single-digit months pulled from struct_time
        mon_str = str(img_time.tm_mon).zfill(2)
        yrmon = "%s-%s" % (yr_str, mon_str)

        if yrmon in self.no_prompt_months:
            # Pass image path to correct month object for insertion.
            self.mo_objs[yrmon].insert_img(img_orig_path, img_time)
        elif (not self.og_latest_mo) or (yrmon > str(self.og_latest_mo)):
            # If there are no months in year directory initially, or if the
            # image is from a later month than the existing folders, make new
            # month object.
            self.make_yrmonth(yrmon)
            self.no_prompt_months.add(yrmon)
            # Pass image path to new month object for insertion.
            self.mo_objs[yrmon].insert_img(img_orig_path, img_time)
        elif bypass_age_warn:
            # This is the same as a condition above, but the intervening elif
            # should instead run if it evaluates true. A new manually-specified
            # date might not be present in mo_objs.
            self.mo_objs[yrmon].insert_img(img_orig_path, img_time)
        else:
            # If the image is from an earlier month not in no_prompt_months set:
            print("Attempted to pull image into %s dir, but a more recent "
            "month dir exists, so timestamp may be wrong.\nFallback bypasses "
                            "warning and copies into older dir anyway." % yrmon)

            man_img_time_struct = date_compare.spec_manual_time(img_orig_path)
            if man_img_time_struct:
                self.insert_img(img_orig_path, man_img_time_struct,
                                                        bypass_age_warn=True)
            else: # continue with operation anyway
                if yrmon not in self.mo_objs.keys():
                    # year-month directory doesn't exist yet, so have make it.
                    self.make_yrmonth(yrmon)
                self.mo_objs[yrmon].insert_img(img_orig_path, img_time)

                ignore = input("Ignore future warnings for this month? "
                                                                    "[Y/N]\n> ")
                if ignore and ignore.lower() == "y":
                    self.no_prompt_months.add(yrmon)

    def __str__(self):
        return self.year_name

    def __repr__(self):
        return "YearDir object with path:\n\t" + self.get_yr_path()


class MoDir(object):
    """Represents directory w/ month label that exists inside a YrDir object
    within the date-organized directory structure. Contains images."""
    def __init__(self, yrmonth_name, YrDir):
        self.dir_name = yrmonth_name
        self.yrmonth_path = YrDir.get_yr_path() + self.dir_name + '/'
        self.YrDir = YrDir

        if not self.dir_name in YrDir.get_mo_list():
            os.mkdir(self.yrmonth_path)

    def get_mo_path(self):
        return self.yrmonth_path

    def get_img_list(self):
        self.img_list = os.listdir(self.yrmonth_path)
        self.img_list.sort()
        return self.img_list

    def insert_img(self, img_orig_path, img_time):
        # make sure image not already here
        img_name = os.path.basename(img_orig_path)   # no trailing slash
        stamped_name = time.strftime("%Y-%m-%d", img_time) + "_" + img_name

        img_comment = date_compare.get_comment(img_orig_path)
        # Ensure not longer than ext4 fs allows. Ignore URLs too.
        if (img_comment and len(img_comment) < 255-len(stamped_name)-1
                                            and "https://" not in img_comment):
            add_comment = input("Comment found in %s EXIF data:\n\t%s\n"
                    "Append to filename? [Y/N]\n> " % (img_name, img_comment))
            if add_comment:
                # https://stackoverflow.com/questions/1976007/what-characters-are-forbidden-in-windows-and-linux-directory-names
                # Only character not allowed in UNIX filename is the forward slash.
                # But I also don't like spaces.
                formatted_comment = img_comment.replace("/", "_")
                formatted_comment = img_comment.replace(" ", "_")
                stamped_name = (os.path.splitext(stamped_name)[0] + "_"
                        + formatted_comment + os.path.splitext(stamped_name)[1])

        # Copy into the dated directory
        copy_to_target(img_orig_path, self.yrmonth_path,
                                                    new_name=stamped_name)

        # Also copy the img into the cat buffer for next step in prog.
        copy_to_target(img_orig_path,
                            self.YrDir.OrgGroup.get_buffer_root_path(),
                            new_name=stamped_name)

    def get_yrmon_name(self):
        return self.dir_name

    def __str__(self):
        return self.dir_name

    def __repr__(self):
        return "MoDir object with path:\n\t" + self.get_mo_path()


# TEST
# ORG = OrganizedGroup(DEFAULT_BU_ROOT)
# ORG.run_org()
