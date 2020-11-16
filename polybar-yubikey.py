#!/usr/bin/env python

r"""
Polybar script to show an indicator when YubiKey is waiting for a touch.
Requires github.com/maximbaz/yubikey-touch-detector: tool to detect when YubiKey is waiting for a touch
@author inv4d3r (https://github.com/inv4d3r)
@license BSD
"""

import argparse
import os
import socket
import sys

class YubiKeyTouchDetectorListener():
    """
    A class watching if YubiKey is waiting for a touch
    """

    def __init__(self, label_key, label_no_key):
        self.socket_path = "$XDG_RUNTIME_DIR/yubikey-touch-detector.socket"
        self.socket_path = os.path.expanduser(self.socket_path)
        self.socket_path = os.path.expandvars(self.socket_path)
        self.label_no_key = label_no_key
        self.label_key = label_key

    def _connect_socket(self):
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect(self.socket_path)
        except:  # noqa e722
            self.socket = None

    def run(self):
        self.socket = self._connect_socket()
        while True:
            output = self.label_no_key
            if self.socket is None:
                # Socket is not available, connect and try again soon
                self._connect_socket()
            else:
                data = self.socket.recv(5)
                if not data:
                    # Connection dropped, reconnect in next loop iteration
                    self.socket = None
                elif data == b"GPG_1":
                    output = self.label_key
                elif data == b"GPG_0":
                    output = self.label_no_key
                elif data == b"U2F_1":
                    output = self.label_key
                elif data == b"U2F_0":
                    output = self.label_no_key
            print(output, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n',
        '--label-no-key',
        help='label for no key touch',
        dest='label_no_key',
        default="",
    )
    parser.add_argument(
        '-l',
        '--label-key',
        help='label for key touch',
        dest='label_key',
        default="key",
    )

    args = parser.parse_args()

    yubikey_detector = YubiKeyTouchDetectorListener(args.label_key, args.label_no_key)
    yubikey_detector.run()
