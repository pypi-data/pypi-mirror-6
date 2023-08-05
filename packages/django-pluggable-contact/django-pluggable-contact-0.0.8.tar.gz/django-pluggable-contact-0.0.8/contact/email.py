from __future__ import unicode_literals

import re

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template.defaultfilters import wrap

from bs4 import BeautifulSoup, Tag, NavigableString

html_comment_re = re.compile(r'<!--[\w\W\s\S]+?-->')
style_tag_re = re.compile(r'<style[\w\W\s\W]+?</style>')
consec_space_re = re.compile(r' +')
consec_nl_re = re.compile('\n+')
starts_with_space_re = re.compile('\n +?')
ends_with_space_re = re.compile(' +?\n')


def convert_a(a):
    link_text = a.get_text()
    link_href = a.get('href', '')
    replacement = link_text
    if link_href and not link_text in link_href:
        if link_href.startswith('mailto:'):
            link_href = link_href.replace('mailto:', '')
        replacement += ' <%s>' % link_href
    a.replace_with(NavigableString(replacement))


def convert_strong(strong):
    strong.replace_with(NavigableString(strong.get_text().upper()))


def convert_em(em):
    em.replace_with(NavigableString('*%s*' % em.get_text()))


def convert_ul(ul):
    s = ''
    for li in ul('li'):
        s += '* %s\n' % li.text
    ul.replace_with(NavigableString(s))


def convert_ol(ol):
    s = ''
    idx = 1
    for li in ol('li'):
        s += '%s. %s\n' % (idx, li.text)
        idx += 1
    ol.replace_with(NavigableString(s))


def add_lbrs(subtree, name):
    for e in subtree(name):
        e.append(NavigableString('\n'))


def to_plain_text(html):
    # Strip all comments from HTML
    html = html_comment_re.sub('', html)

    # Strip out <style> tags
    html = style_tag_re.sub('', html)

    # Strip newlines and consecutive spaces
    html = consec_nl_re.sub('', html)
    html = consec_space_re.sub(' ', html)

    soup = BeautifulSoup(html)

    # First convert all A tags to `text <link>` format
    for e in soup.body('a'):
        convert_a(e)

    # Take care of strong emphasis
    for e in soup.body('strong'):
        convert_strong(e)
    for e in soup.body('b'):
        convert_strong(e)

    # Take care of emphasis
    for e in soup.body('em'):
        convert_em(e)
    for e in soup.body('i'):
        convert_em(e)

    # Take care of unordered lists
    for e in soup.body('ul'):
        convert_ul(e)

    # Take care of ordered lists
    for e in soup.body('ol'):
        convert_ol(e)

    # Add linebreaks after common block tags
    for t in ('p', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
        add_lbrs(soup.body, t)

    s = ''

    for e in soup.body.descendants:
        if type(e) == Tag:
            if e.name == 'img':
                # add the alt text as text
                s += e.get('alt', '')
            if e.name == 'br':
                # add <br> marker
                s += '<br>'
            if e.name == 'hr':
                s += '%s\n' % (''.join(['-' for i in range(75)]))
        elif isinstance(e, unicode):
            s += e

    # Add newline after each linebreak
    s = s.replace('\n', '\n\n')

    # Restore <br> linebreaks
    s = s.replace('<br>\n\n', '\n')
    s = s.replace('<br>', '\n')

    # Replace multiple spaces with a single space
    s = consec_space_re.sub(' ', s)

    # Remove spaces at the beginning of the line
    s = starts_with_space_re.sub('\n', s)

    # Remove spaces at the end of the line
    s = ends_with_space_re.sub('\n', s)

    return wrap(s.strip(), 75)


def create_message_body(template, data, text_only=False):
    """ Create plain-text and HTML body of a message

    Returns a 2-tuple where first item is plain-text, and second item is HTML
    attachment if any. If text_only flag is set to true, second item of the
    tuple is always None.

    When ``text_only`` flag is set, the template is considered to be plain-text.

    :param template: Template name
    :param data: Template data
    :param text_only: Whether to generate the HTML part
    """

    body = render_to_string(template, data)

    if text_only:
        return body, None
    else:
        return to_plain_text(body), body


def create_message(subject, text, from_email, recipients, headers, html=None):
    """ Create an EmailMultiAlternatives instance

    :param subject: Message subject
    :param text: Plain-text message body
    :param from_email: Sender email
    :param recipients: Recipient list
    :param headers: Extra headers
    :param html: HTML attachment if any (default: None)
    """

    # Make sure recipients are an iterable
    if not hasattr(recipients, '__iter__'):
        recipients = [recipients]

    # Construct the message instance
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=from_email,
        to=recipients,
        headers=headers
    )

    if html:
        # HTML body was specified so attach it
        msg.attach_alternative(html, 'text/html')

    return msg


def send_message(msg):
    """ Take EmailMultiAlternatives instance and send it

    :param msg: EmailMultiAlternatives instance
    """
    return msg.send()


def send_html_email(subject, from_email, to, template, data, text_only=False,
                    reply_to=None, send_separately=False, headers={}):
    """ Send HTML email based on a template

    Use ``send_separately`` parameter to send to multiple recipients one by one
    (instead of including all recipients in the ``To`` header).

    When sending to multiple recipients separately, you can customize the data
    per recipient by assigning each recipient's data to a key on ``data``
    parameter that matches the recipient. For example::

        data = {
            'test1@example.com': { ... },
            'test2@example.com': { ... },
            ...
        }
        recipients = data.keys()
        send_html_email('Test', 'foo@example.com', recipients,
                        'email/test.html', data)

    :param subject: Message subject
    :param from_email: Sender email
    :param to: Recipients (either string or iterable of strings)
    :param template: Name of the email template
    :param data: Data for the template
    :param text_only: Whether to send email as plain-text without HTML part
    (default: False)
    :param reply_to: Reply-To address (default: None)
    :param send_separately: Whether to send to multiple recipients one by one
    (default: False)
    :param headers: Extra headers (default: {})
    """

    # Set up Reply-To header if necessary
    if reply_to:
        headers['Reply-To'] = reply_to

    # ``to`` must be an iterable
    if not hasattr(to, '__iter__'):
        to = [to]

    if len(to) and send_separately:
        # We need to send to each recipient a separate copy of the message.
        for r in to:
            if r in data:
                text, html = create_message_body(template, data[r], text_only)
            else:
                text, html = create_message_body(template, data, text_only)
            send_message(
                create_message(subject, text, from_email, r, headers, html),
            )
    else:
        # Send normally (note that when sending to multiple recipients, each
        # recipient will be able to see the other recipients' emails. Use
        # ``send_separately`` argument to send multiple messages.
        text, html = create_message_body(template, data, text_only)
        send_message(
            create_message(subject, text, from_email, to, headers, html),
        )

    return (text, html)

