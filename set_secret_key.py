# -*- coding: utf-8 -*-
import os
import sys


def main(secret_id, secret_key):
    id_command = r"setx TENCENTCLOUD_SECRET_ID %s /m" % secret_id
    key_command = r"setx TENCENTCLOUD_SECRET_KEY %s /m" % secret_key

    os.system(id_command)
    os.system(key_command)


if __name__ == "__main__":
    secret_id, secret_key = sys.argv[1:3]
    main(secret_id, secret_key)
