# -*- coding: utf-8 -*-
'''Domain functions for public'''


def compose_username(nick, email, provider):
    """
    @brief Compose the username

    The username policy via openid is as follow:
    * Try to use the nick name
    * If not available fall back to email
    * Append the the openid provider as domain. Delimiter is % in order to 
      diferentiate from @ (if email is used)

    @param nick The nick name or None
    @param email The email or None
    @param provider the Authentication provider
    @return Non in case no user name was derived, otherwise the username
    """
    if nick:
        return '{0}%{1}'.format(nick, provider)
    else:
        if email:
            return '{0}%{1}'.format(email, provider)
    return None


def get_first_last_name(fullname):
    """
    @brief Extract first and last name from full name
    @param fullname
    @return tupel of (first_name, last_name)
    """
    if not fullname:
        return ('', '')
    words = fullname.split(' ')
    if len(words) == 0:
        return ('', '')
    elif len(words) == 1:
        return ('', words[0])
    else:
        return (' '.join(words[0:-2]), words[-1])