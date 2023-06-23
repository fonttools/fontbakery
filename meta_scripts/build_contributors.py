import argparse
import codecs
import os
import re
import sys

import git  # pip install GitPython

CONTRIBUTORS_HEAD = """
# This is the list of people who have contributed to this project,
# and includes those not listed in AUTHORS.txt because they are not
# copyright authors. For example, company employees may be listed
# here because their company holds the copyright and is listed there.
#
# When adding J Random Contributor's name to this file, either J's
# name or J's organization's name should be added to AUTHORS.txt
#
# Names should be added to this file as:
# Name <email address>

"""

description = "Generate a CONTRIBUTORS.txt file from a repository's git history."
parser = argparse.ArgumentParser(description=description)
parser.add_argument("folder", nargs=1, help="source folder which contains git commits")


def main():
    args = parser.parse_args()
    folder = args.folder[0]
    log = git.Git(folder).log()
    commit_list = re.findall(r"(?<=Author: ).*", log)
    contributors = []
    # Add contributors in reverse. Should mean project creator is first
    for contributor in commit_list[::-1]:
        if contributor not in contributors:
            contributors.append(contributor)

    contrib_file = os.path.join(folder, "CONTRIBUTORS.txt")
    if os.path.isfile(contrib_file):
        print("CONTRIBUTORS.txt file already exists, adding '_copy' suffix.")
        contrib_file = os.path.join(folder, "CONTRIBUTORS_copy.txt")

    with codecs.open(os.path.join(folder, contrib_file), "w", encoding="utf-8") as doc:
        doc.write(CONTRIBUTORS_HEAD)
        doc.write("\n".join(contributors))
    print(f"Finished generating CONTRIBUTORS.txt. File saved at {folder}")


if __name__ == "__main__":
    sys.exit(main())
