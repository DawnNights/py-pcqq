from cryptography.hazmat.bindings._openssl import ffi, lib

def EncryptECDH(pub:bytes, PublicKey:bytes, PrivateKey:bytes):
    eckey = lib.EC_KEY_new_by_curve_name(711)

    big = lib.BN_new()
    lib.BN_bin2bn(PrivateKey[4:],len(PrivateKey)-4, big)

    lib.EC_KEY_set_private_key(eckey, big)
    lib.BN_free(big)

    group = lib.EC_KEY_get0_group(eckey)
    point = lib.EC_POINT_new(group)
    ctx = lib.BN_CTX_new()

    lib.EC_POINT_oct2point(group, point, PublicKey, len(PublicKey), ctx)
    lib.EC_KEY_set_public_key(eckey, point)

    group1 = lib.EC_KEY_get0_group(eckey)
    lib.EC_KEY_get0_public_key(eckey)

    point2 = lib.EC_POINT_new(group1)
    lib.EC_POINT_oct2point(group1, point2, pub, len(pub), ctx)
    shared = b'\x00'*16

    lib.ECDH_compute_key(shared, 16, point2, eckey, ffi.NULL)
    lib.EC_KEY_free(eckey)

    return shared