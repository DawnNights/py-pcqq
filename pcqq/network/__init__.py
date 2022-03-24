from .pcapi import (
    send_friend_msg,
    friend_receipt,
    send_group_msg,
    group_receipt,
    upload_friend_image,
    upload_group_image
)

from .webapi import (
    get_group_info,
    set_group_card,
    set_group_shutup,
    get_user_name,
    get_user_cache,
    get_group_cache,
)

from .wtlogin import (
    set_online,
    login_out,
    heatbeat,
    qrcode_login,
    password_login,
    token_login
)
