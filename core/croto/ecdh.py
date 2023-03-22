from cryptography.hazmat.bindings._openssl import ffi, lib


class ECDH:
    def __init__(self):
        self.public_key = bytes(25)
        self.share_key = bytes(16)

        self.ec_key = lib.EC_KEY_new_by_curve_name(711)
        self.group = lib.EC_KEY_get0_group(self.ec_key)
        self.point = lib.EC_POINT_new(self.group)

        if lib.EC_KEY_generate_key(self.ec_key) == 1:
            lib.EC_POINT_point2oct(self.group, lib.EC_KEY_get0_public_key(
                self.ec_key), 2, self.public_key, len(self.public_key), ffi.NULL)

            buf = bytes([
                4, 191, 71, 161, 207, 120, 166,
                41, 102, 139, 11, 195, 159, 142,
                84, 201, 204, 243, 182, 56, 75,
                8, 184, 174, 236, 135, 218, 159,
                48, 72, 94, 223, 231, 103, 150,
                157, 193, 163, 175, 17, 21, 254,
                13, 204, 142, 11, 23, 202, 207
            ])
            if lib.EC_POINT_oct2point(self.group, self.point, buf, len(buf), ffi.NULL) == 1:
                lib.ECDH_compute_key(self.share_key, len(
                    self.share_key), self.point, self.ec_key, ffi.NULL)

    def twice(self, tk_key: bytes):
        twice_key = bytes(16)

        if lib.EC_POINT_oct2point(self.group, self.point, tk_key, len(tk_key), ffi.NULL) == 1:
            lib.ECDH_compute_key(twice_key, len(twice_key),
                                 self.point, self.ec_key, ffi.NULL)

        return twice_key
