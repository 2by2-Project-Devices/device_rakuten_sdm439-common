#!/usr/bin/env python
#
# Copyright (C) 2016 The CyanogenMod Project
# Copyright (C) 2017-2022 The LineageOS Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from hashlib import sha1
from pathlib import Path
import sys

device = 'sdm439-common'
vendor = 'rakuten'

vendor_path = '../../../vendor/' + vendor + '/' + device + '/proprietary'
proprietary_files = sorted(Path('.').glob('proprietary-files*.txt'))


def split_line(line):
    entry, *sha1_parts = line.split('|', 1)
    metadata = ''
    if ';' in entry:
        entry, metadata = entry.split(';', 1)
        metadata = ';' + metadata

    return entry, metadata, sha1_parts[0] if sha1_parts else None


def get_file_path(line):
    entry, _, _ = split_line(line)
    file_path = entry.split(':', 1)[1] if ':' in entry else entry
    return file_path[1:] if file_path.startswith('-') else file_path


def cleanup(lines):
    for index, line in enumerate(lines):
        line = line.rstrip('\n')

        if not line or line[0] == '#':
            continue

        entry, metadata, _ = split_line(line)
        lines[index] = '%s%s\n' % (entry, metadata)


def update(lines):
    need_sha1 = False

    for index, line in enumerate(lines):
        line = line.rstrip('\n')

        if not line:
            continue

        if line[0] == '#':
            need_sha1 = ' - from' in line
            continue

        if need_sha1:
            entry, metadata, _ = split_line(line)
            file_path = get_file_path(entry)

            with open('%s/%s' % (vendor_path, file_path), 'rb') as file:
                file_hash = sha1(file.read()).hexdigest()

            lines[index] = '%s%s|%s\n' % (entry, metadata, file_hash)


for proprietary_file in proprietary_files:
    with proprietary_file.open('r') as file:
        lines = file.readlines()

    if len(sys.argv) == 2 and sys.argv[1] == '-c':
        cleanup(lines)
    else:
        update(lines)

    with proprietary_file.open('w') as file:
        file.writelines(lines)
