#!/usr/bin/env python
#
#  Copyright 2017 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Support for adding/removing information about config db link from /etc/rc.local.d/local.sh
Any config stuff we need and configure in /etc/... will be removed on ESX reboot.
Anything we need to persist between the reboots, needs to be confugured here.
"""

import fileinput
import sys

END_OF_CONTENT = "exit 0" # we will reach it one time, the first time only

# this is what we use to identify the text section
config_db_tag = "# -- vSphere Docker Volume Service configuration location"

# this is the text section tempate. '{}' will be replace by datastore name
config_db_section = config_db_tag + \
"""
#
# Please do not edit this section manually. It is managed by vmdkops_admin.py config command
#
datastore={}
slink=/etc/vmware/vmdkops/auth-db
shared_dbn=/vmfs/volumes/$datastore/dockvols/vmdkops_config.db
if [ -d $(basename $slink) ] && [ ! -e $slink  ]
then
    ln -s $shared_db $slink
fi
""" + config_db_tag + "\n"


# open file and scan it.
#
# if we reached "exit 0" add the text section, add the rest of the file and be done
# if we find the tag,  skip to the end of the section (same tag, add the rest of the file and be done)


def update_content(src_file, add, section, tag):
    """
    Updates (adds or removes) a section limited with tag to a file
    TBD: a better description
    """
    skip_to_tag = no_more_checks = False
    for line in iter(fileinput.input([src_file])):
        if no_more_checks:
            sys.stdout.write(line)
            continue
        if skip_to_tag:
            if line.startswith(tag):
                # found the second tag, done with the section
                no_more_checks = True
                if add:
                    print(section)
            continue
        if line.startswith(tag):
            # Found the first tag - skip till the next one
            skip_to_tag = True
            continue
        if line.startswith(END_OF_CONTENT):
            if add:
                print(section)
            no_more_checks = True
        sys.stdout.write(line)

name = "test1"
ds_name = "MYSharedXXXXXXXXE"

update_content(src_file=name, add=False, section=config_db_section.format(ds_name), tag=config_db_tag)