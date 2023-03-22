import os

from core.client import QQClient
from core.entities import MessageEvent
from core.protocol import wtlogin, event
from .plugin import Session, default_manager


def run_bot(uin: int = 0):
    cli = QQClient(uin)

    path = os.path.join(cli.stru.path, "session.token")
    if os.path.exists(path):
        cli.run_task(wtlogin.login_by_token(cli))
    else:
        cli.run_task(wtlogin.login_by_scan(cli))
    
    async def plugin_handle_message(event: MessageEvent):
        session = Session(
            driver=cli,
            message=event.message.format(),
            event=event,
            matched=None
        )
        
        await default_manager.exec_all(session)

    cli.manage.append(event.handle_msg_receipt(cli))
    cli.manage.append(event.handle_group_msg(cli, plugin_handle_message))
    cli.manage.append(event.handle_private_msg(cli, plugin_handle_message))

    async def run_handler():
        await cli.recv_and_exec(cli.stru.session_key)
        cli.add_task(run_handler())
    cli.add_task(run_handler())
    
    cli.loop.run_forever()