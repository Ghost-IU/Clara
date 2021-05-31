import time
from datetime import datetime

from bs4 import BeautifulSoup
from requests import get
from telegram import (Bot, InlineKeyboardButton, InlineKeyboardMarkup,
                      ParseMode, Update)
from telegram.error import BadRequest
from telegram.ext import run_async
from ujson import loads

from SaitamaRobot import dispatcher
from SaitamaRobot.modules.disable import DisableAbleCommandHandler
from SaitamaRobot.modules.helper_funcs.alternate import typing_action

GITHUB = "https://github.com"
DEVICES_DATA = "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json"


@typing_action
def magisk(update, context):
    url = "https://raw.githubusercontent.com/topjohnwu/magisk-files/"
    releases = ""
    for type, branch in {
        "Stable": ["master/stable", "master"],
        "Canary": ["master/canary", "canary"],
    }.items():
        data = get(url + branch[0] + ".json").json()
        if type != "Canary":
            releases += (
                f"*{type}*: \n"
                f'• App - [{data["magisk"]["version"]}-{data["magisk"]["versionCode"]}]({data["magisk"]["link"]}) - [Changelog]({data["magisk"]["note"]})\n \n'
            )
        else:
            releases += (
                f"*{type}*: \n"
                f'• App - [{data["magisk"]["version"]}-{data["magisk"]["versionCode"]}]({data["magisk"]["link"]}) - [Changelog]({data["magisk"]["note"]})\n'
                f"\n Now magisk is packed as all in one, refer [this installation](https://topjohnwu.github.io/Magisk/install.html) procedure for more info.\n"
            )

    update.message.reply_text(
        "*Latest Magisk Releases:*\n\n{}".format(releases),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


@typing_action
def device(update, context):
    args = context.args
    if len(args) == 0:
        reply = "No codename provided, write a codename for fetching informations."
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if (err.message == "Message to delete not found") or (
                err.message == "Message can't be deleted"
            ):
                return
    device = " ".join(args)
    db = get(DEVICES_DATA).json()
    newdevice = device.strip("lte") if device.startswith("beyond") else device
    try:
        reply = f"Search results for {device}:\n\n"
        brand = db[newdevice][0]["brand"]
        name = db[newdevice][0]["name"]
        model = db[newdevice][0]["model"]
        codename = newdevice
        reply += (
            f"<b>{brand} {name}</b>\n"
            f"Model: <code>{model}</code>\n"
            f"Codename: <code>{codename}</code>\n\n"
        )
    except KeyError:
        reply = f"Couldn't find info about {device}!\n"
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if (err.message == "Message to delete not found") or (
                err.message == "Message can't be deleted"
            ):
                return
    update.message.reply_text(
        "{}".format(reply), parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )


@typing_action
def twrp(update, context):
    args = context.args
    if len(args) == 0:
        reply = "No codename provided, write a codename for fetching informations."
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if (err.message == "Message to delete not found") or (
                err.message == "Message can't be deleted"
            ):
                return

    _device = " ".join(args)
    url = get(f"https://eu.dl.twrp.me/{_device}/")
    if url.status_code == 404:
        reply = f"Couldn't find twrp downloads for {_device}!\n"
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if (err.message == "Message to delete not found") or (
                err.message == "Message can't be deleted"
            ):
                return
    else:
        reply = f"*Latest Official TWRP for {_device}*\n"
        db = get(DEVICES_DATA).json()
        newdevice = _device.strip("lte") if _device.startswith("beyond") else _device
        try:
            brand = db[newdevice][0]["brand"]
            name = db[newdevice][0]["name"]
            reply += f"*{brand} - {name}*\n"
        except KeyError as err:
            pass
        page = BeautifulSoup(url.content, "lxml")
        date = page.find("em").text.strip()
        reply += f"*Updated:* {date}\n"
        trs = page.find("table").find_all("tr")
        row = 2 if trs[0].find("a").text.endswith("tar") else 1
        for i in range(row):
            download = trs[i].find("a")
            dl_link = f"https://eu.dl.twrp.me{download['href']}"
            dl_file = download.text
            size = trs[i].find("span", {"class": "filesize"}).text
            reply += f"[{dl_file}]({dl_link}) - {size}\n"

        update.message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )


@typing_action
def orangefox(update, context):
    message = update.effective_message
    chat = update.effective_chat
    device = message.text[len("/orangefox ") :]
    btn = ""

    if device:
        link = get(
            f"https://api.orangefox.download/v3/releases/?codename={device}&sort=date_desc&limit=1"
        )

        if link.status_code == 404:
            msg = f"OrangeFox recovery is not avaliable for {device}"
        else:
            page = loads(link.content)
            file_id = page["data"][0]["_id"]
            link = get(
                f"https://api.orangefox.download/v3/devices/get?codename={device}"
            )
            page = loads(link.content)
            oem = page["oem_name"]
            model = page["model_name"]
            full_name = page["full_name"]
            maintainer = page["maintainer"]["username"]
            link = get(f"https://api.orangefox.download/v3/releases/get?_id={file_id}")
            page = loads(link.content)
            dl_file = page["filename"]
            build_type = page["type"]
            version = page["version"]
            changelog = page["changelog"][0]
            size = str(round(float(page["size"]) / 1024 / 1024, 1)) + "MB"
            dl_link = page["mirrors"]["DL"]
            date = datetime.fromtimestamp(page["date"])
            md5 = page["md5"]
            msg = f"*Latest OrangeFox Recovery for the {full_name}*\n\n"
            msg += f"• Manufacturer: `{oem}`\n"
            msg += f"• Model: `{model}`\n"
            msg += f"• Codename: `{device}`\n"
            msg += f"• Build type: `{build_type}`\n"
            msg += f"• Maintainer: `{maintainer}`\n"
            msg += f"• Version: `{version}`\n"
            msg += f"• Changelog: `{changelog}`\n"
            msg += f"• Size: `{size}`\n"
            msg += f"• Date: `{date}`\n"
            msg += f"• File: `{dl_file}`\n"
            msg += f"• MD5: `{md5}`\n"
            btn = [[InlineKeyboardButton(text=f"Download", url=dl_link)]]
    else:
        msg = "Enter the device codename to fetch, like:\n`/orangefox mido`"

    update.message.reply_text(
        text=msg,
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


__help__ = """
Get the latest Magsik releases or TWRP for your device!
*Android related commands:*
 × /magisk - Gets the latest magisk release for Stable/Beta/Canary.
 × /device <codename> - Gets android device basic info from its codename.
 × /twrp <codename> -  Gets latest twrp for the android device using the codename.
 × /orangefox <codename> -  Gets latest orangefox recovery for the android device using the codename.
"""

__mod_name__ = "Android"

MAGISK_HANDLER = DisableAbleCommandHandler("magisk", magisk)
TWRP_HANDLER = DisableAbleCommandHandler("twrp", twrp, pass_args=True)
DEVICE_HANDLER = DisableAbleCommandHandler("device", device, pass_args=True)
ORANGEFOX_HANDLER = DisableAbleCommandHandler("orangefox", orangefox, pass_args=True)

dispatcher.add_handler(MAGISK_HANDLER)
dispatcher.add_handler(TWRP_HANDLER)
dispatcher.add_handler(DEVICE_HANDLER)
dispatcher.add_handler(ORANGEFOX_HANDLER)
