from .bot import run_bot, login_for_test

from .client import (
    send_group_msg,
    send_friend_msg,
    set_group_card,
    set_group_shutup,
    get_group_info_all_nocache,
    get_group_members_nocache,
    get_user_name,
    get_group_name,
    set_online,
    login_out
)

from .plugin import (
    Session,
    on,
    on_type,
    on_full,
    on_fulls,
    on_command,
    on_commands,
    on_regex
)