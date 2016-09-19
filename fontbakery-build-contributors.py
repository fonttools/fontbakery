'''Generate a CONTRIBUTORS.txt document from a repository's git history.'''
import git
import sys
import os
import re


CONTRIBUTORS_HEAD = \
'''# This is the list of people who have contributed to this project,
# and includes those not listed in AUTHORS.txt because they are not
# copyright authors. For example, company employees may be listed
# here because their company holds the copyright and is listed there.
#
# When adding J Random Contributor's name to this file, either J's
# name or J's organization's name should be added to AUTHORS.txt
#
# Names should be added to this file as:
# Name <email address>

'''


def main(folder):
    log = git.Git(folder).log()
    commit_list = re.findall(r'(?<=Author: ).*', log)
    contributors = []
    # Add contributors in reverse. Should mean project creator is first
    for contributor in commit_list[::-1]:
        if contributor not in contributors:
            contributors.append(contributor)

    contrib_file = os.path.join(folder, 'CONTRIBUTORS.txt')
    if os.path.isfile(contrib_file):
        print "CONTRIBUTORS.txt already exists, adding '_copy' suffix\n"
        contrib_file = os.path.join(folder, 'CONTRIBUTORS_copy.txt')

    with open(os.path.join(folder, contrib_file), 'w') as doc:
        doc.write(CONTRIBUTORS_HEAD)
        doc.write('\n'.join(contributors))
    print 'Finished generating CONTRIBUTORS.txts. File saved at %s' % (folder)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'ERROR: please add one source folder which contains git commits'
    else:
        folder = sys.argv[-1]
        main(folder)
