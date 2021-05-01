import html
import re
from datetime import datetime
from html import escape
from typing import List
from typing import Optional

from requests import get
from telegram import Chat
from telegram import ChatAction
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import Message
from telegram import MessageEntity
from telegram import ParseMode
from telegram import TelegramError
from telegram.error import BadRequest
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.utils.helpers import escape_markdown
from telegram.utils.helpers import mention_html
from telegram.utils.helpers import mention_markdown

from SaitamaRobot import DEMONS
from SaitamaRobot import DEV_USERS
from SaitamaRobot import dispatcher
from SaitamaRobot import DRAGONS
from SaitamaRobot import OWNER_ID
from SaitamaRobot import TIGERS
from SaitamaRobot import TOKEN
from SaitamaRobot import WOLVES
from SaitamaRobot.modules.disable import DisableAbleCommandHandler
from SaitamaRobot.modules.helper_funcs.alternate import typing_action


@typing_action
def repo(update, context):
    message = update.effective_message
    args = message.text.split(None, 2)[1:]
    text = ""

    # handle args
    if len(args) == 0:
        return message.reply_text(
            "Enter someone's GitHub username to view their repos or get repo data with username and repo name!"
        )
    elif len(args) == 1:
        user = args[0]
        usr_data = get(
            f"https://api.github.com/users/{user}/repos?per_page=40").json()

        if len(usr_data) != 0:
            reply_text = f"*{user}*" + f"'s" + "* Repos:*\n"
            for i in range(len(usr_data)):
                reply_text += f"× [{usr_data[i]['name']}]({usr_data[i]['html_url']})\n"
            message.reply_text(
                reply_text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
        else:
            return message.reply_text(
                "*User/Organization not found!* \nEnter a valid username.",
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        user, repo = args
        rep_data = get(f"https://api.github.com/repos/{user}/{repo}").json()
        brc_data = get(
            f"https://api.github.com/repos/{user}/{repo}/branches").json()
        try:
            text = f"*Repo name:* {rep_data['full_name']}"
            text += f"\n*Language*: {rep_data['language']}"
            if f"{rep_data['license']}" is None:
                licensePlate = "None"
            else:
                try:
                    licensePlate = rep_data["license"]["name"]
                except TypeError:
                    licensePlate = rep_data["license"]
            text += f"\n*License*: `{licensePlate}`"

            whitelist = [
                "description",
                "id",
                "homepage",
                "archived",
                "updated_at",
                "created_at",
                "open_issues",
            ]

            rename = {
                "id": "Repo ID",
                "created_at": "Created date",
                "updated_at": "Last updated",
                "open_issues": "Open issues",
            }

            empty = [None, "null", "", False]

            for x, y in rep_data.items():
                if x in whitelist:

                    x = rename.get(x, x.title())

                    if x in ["Created date", "Last updated"]:
                        y = datetime.strptime(y, "%Y-%m-%dT%H:%M:%SZ")

                    if y not in empty:
                        if x == "Homepage":
                            y = f"[Here!]({y})"
                        elif x in [
                                "Created date",
                                "Last updated",
                                "Description",
                        ]:
                            text += f"\n*{x}:* \n`{y}`"
                        else:
                            text += f"\n*{x}:* `{y}`"

            count = 0
            for i in range(len(brc_data)):
                count += 1
            text += f"\n*Branches:* `{count}`"
            text += f"\n*🍴 Forks:* `{rep_data['forks_count']}` | *🌟 Stars:* `{rep_data['stargazers_count']}` "

            chat = update.effective_chat
            dispatcher.bot.send_photo(
                "{}".format(chat.id),
                f"{rep_data['html_url']}",
                caption=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(text="Repo link",
                                             url=f"{rep_data['html_url']}"),
                        InlineKeyboardButton(
                            text="Issues",
                            url=f"https://github.com/{user}/{repo}/issues",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Pull Requests",
                            url=f"https://github.com/{user}/{repo}/pulls",
                        ),
                        InlineKeyboardButton(
                            text="Commits",
                            url=
                            f"https://github.com/{user}/{repo}/commits/{rep_data['default_branch']}",
                        ),
                    ],
                ]),
            )
        except KeyError:
            return message.reply_text(
                "*User/Organization not found!* \nMake sure to enter a valid username.",
                parse_mode=ParseMode.MARKDOWN,
            )


__help__ = """
Some useful git functions to make Github browsing easier and faster.
× /repo <username>: Displays a list of hyperlinked public repos by a user on Github.
× /repo <username> <repo>: Get stats on a public repo.

Creds : https://github.com/marchingon12/Perry
"""

__mod_name__ = "GitHub"

REPO_HANDLER = CommandHandler("repo", repo, pass_args=True)

dispatcher.add_handler(REPO_HANDLER)
