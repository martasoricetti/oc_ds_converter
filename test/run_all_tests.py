# SPDX-FileCopyrightText: 2023 Arianna Moretti <arianna.moretti4@unibo.it>
#
# SPDX-License-Identifier: ISC

from subprocess import Popen

def main():
    Popen(
        ['python', '-m', 'unittest', 'discover', '-s', 'test', '-p', '*.py', '-b']
    )