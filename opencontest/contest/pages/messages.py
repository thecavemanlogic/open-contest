from django.http import HttpResponse

from contest.auth import logged_in_required
from contest.models.message import Message
from contest.models.user import User
from contest.pages.lib import Card
from contest.pages.lib.htmllib import UIElement, h, div, a, h2
from contest.pages.lib.page import Modal, Page


def formatFrom(fromUser, currentUser) -> str:
    if fromUser.id == currentUser.id or currentUser.isAdmin():
        return fromUser.username
    else:
        return "judge"


class MessageCard(UIElement):
    def __init__(self, msglist, user):
        msg = msglist[0]
        msgType = "Announcement" if msg.isGeneral else "Message"
    
        body = msg.message
        for reply in msglist[1:]:
            body += f"""\n<br><br>Reply from {formatFrom(reply.fromUser, user)} at 
                <span class='time-format'>{reply.timestamp}</span>:<br>
                {reply.message}"""
        
        self.html = Card(
            f"{msgType} from {formatFrom(msg.fromUser, user)} at <span class='time-format'>{msg.timestamp}</span>",
            body,
            reply=f"reply('{msg.fromUser.id}', '{msg.id}')" if msg.isAdmin and user.isAdmin() else None
        )


INBOX, PROCESSED, ANNOUNCEMENT = 'inbox', 'processed', 'announcements'


@logged_in_required
def displayMessages(request, *args, **kwargs):
    user = User.getCurrent(request)

    messages = []
    if INBOX in request.path:
        if user.isAdmin():
            inbox = {}
            Message.forEach(lambda msg: inbox.update({msg.id: msg}) if msg.isAdmin else None)

            # Remove from inbox messages that have been responded to
            Message.forEach(lambda msg: inbox.pop(msg.replyTo) if msg.replyTo in inbox else None)
            messages = list(inbox.values())
        else:
            Message.forEach(lambda msg: messages.append(msg) if (msg.toUser and msg.toUser.id == user.id or msg.fromUser == user or msg.isGeneral) else None)

    elif PROCESSED in request.path:
        def addReply(msg):
            if msg.replyTo in replies:
                replies[msg.replyTo].append(msg)
            else:
                replies[msg.replyTo] = [msg]

        # Find replies
        replies = {}
        Message.forEach(lambda msg: addReply(msg) if msg.replyTo else None)

        messages = [[Message.get(id)] + replies[id] for id in replies.keys()]

    elif ANNOUNCEMENT in request.path:
        Message.forEach(lambda msg: messages.append(msg) if msg.isGeneral else None)

    if len(messages) > 0 and not isinstance(messages[0], list):
        messages = [[msg] for msg in messages]

    messages = [*map(lambda msglist: MessageCard(msglist, user), sorted(messages, key=lambda msglist: -msglist[0].timestamp))]

    adminDetails = []
    if user.isAdmin():
        userOptions = [*map(lambda usr: h.option(usr.username, value=usr.id), User.all())]
        adminDetails = [
            h.h5("To"),
            h.select(cls="form-control recipient", contents=[
                h.option("general"),
                *userOptions
            ]),
            h.input(type="hidden", id="replyTo"),
            h.h5("Message")
        ]

    if user.isAdmin():
        filter = div(
            a(href='inbox', contents="Inbox"), ' | ',
            a(href='processed', contents="Handled"), ' | ',
            a(href='announcements', contents="Announcements"),
        )
    else:
        filter = div()

    return HttpResponse(Page(
        h2("Messages", cls="page-title"),
        div(cls="actions", contents=[
            h.button("+ Send Message", cls="button create-message", onclick="createMessage()")
        ]),
        filter,
        Modal(
            "Send Message",
            div(
                *adminDetails,
                h.textarea(cls="message col-12")
            ),
            div(
                h.button("Cancel", **{"type":"button", "class": "button button-white", "data-dismiss": "modal"}),
                h.button("Send", **{"type":"button", "class": "button", "onclick": "sendMessage()"})
            )
        ),
        div(cls="message-cards", contents=messages),
    ))
