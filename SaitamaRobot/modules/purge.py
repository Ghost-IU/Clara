import asyncio

from telethon import events
from telethon.errors.rpcerrorlist import MessageDeleteForbiddenError
from telethon.tl.types import ChannelParticipantsAdmins

from SaitamaRobot import DEMONS
from SaitamaRobot import DEV_USERS
from SaitamaRobot import DRAGONS
from SaitamaRobot import OWNER_ID
from SaitamaRobot import telethn
from SaitamaRobot import TIGERS
from SaitamaRobot import WOLVES
from SaitamaRobot.modules.helper_funcs.telethn.chatstatus import can_delete_messages
from SaitamaRobot.modules.helper_funcs.telethn.chatstatus import user_is_admin


# Check if user has admin rights

# async def is_administrator(user_id: int, message):
# admin = False
# async for user in telethn.iter_participants(
# message.chat_id, filter=ChannelParticipantsAdmins
# ):
# if user_id == user_is_admin or can_delete_messages:
# admin = True
# break
# return admin
async def purge(event):
    chat = event.chat_id
    msgs = []

    if (
        not await user_is_admin(
            user_id=event.sender_id,
            message=event,
        )
        and event.from_id not in [1087968824]
    ):
        await event.reply("Only Admins are allowed to use this command")
        return

    msg = await event.get_reply_message()
    if not msg:
        await event.reply("Reply to a message to select where to start purging from.")
        return

    try:
        msg_id = msg.id
        count = 0
        to_delete = event.message.id - 1
        await event.client.delete_messages(chat, event.message.id)
        msgs.append(event.reply_to_msg_id)
        for m_id in range(to_delete, msg_id - 1, -1):
            msgs.append(m_id)
            count += 1
            if len(msgs) == 100:
                await event.client.delete_messages(chat, msgs)
                msgs = []

        await event.client.delete_messages(chat, msgs)
        del_res = await event.client.send_message(
            event.chat_id, f"Purged {count} messages."
        )

        await asyncio.sleep(2)
        await del_res.delete()

    except MessageDeleteForbiddenError:
        text = "Failed to delete messages.\n"
        text += "Selected messages may be too old or you haven't given me enough admin rights!"
        del_res = await event.respond(text, parse_mode="md")
        await asyncio.sleep(5)
        await del_res.delete()


async def delete_msg(event):
    if event.from_id is None:
        return

    if (
        not await user_is_admin(
            user_id=event.sender_id,
            message=event,
        )
        and event.from_id not in [1087968824]
    ):
        await event.reply("Only Admins are allowed to use this command")
        return

    if not await can_delete_messages(message=event):
        await event.reply("Can't seem to delete this?")
        return

    message = await event.get_reply_message()
    if not message:
        await event.reply("Whadya want to delete?")
        return
    chat = await event.get_input_chat()
    del_message = [message, event.message]
    await event.client.delete_messages(chat, del_message)


__help__ = """
Deleting a selected amount of messages are easy with this command. \
Bot purges messages all together or individually.
*Admin only:*
 × /del: Deletes the message you replied to.
 × /purge: Deletes all messages between this and the replied to message.
"""
PURGE_HANDLER = purge, events.NewMessage(pattern="^[!/]purge$")
DEL_HANDLER = delete_msg, events.NewMessage(pattern="^[!/]del$")

telethn.add_event_handler(*PURGE_HANDLER)
telethn.add_event_handler(*DEL_HANDLER)

__mod_name__ = "Purges"
