# -*- coding: utf-8 -*-
import pytest
from enma.extensions import mail


@pytest.mark.skipif('False', reason='requires a working email configuration')
def test_reset_passwd_email_sent(user, testapp):
    """
    Test if a send password email is to be send
    """

    with mail.record_messages() as outbox:
        from enma.user.mail import send_reset_password_link

        assert len(outbox) == 0
        send_reset_password_link(user)

        assert len(outbox) == 1
