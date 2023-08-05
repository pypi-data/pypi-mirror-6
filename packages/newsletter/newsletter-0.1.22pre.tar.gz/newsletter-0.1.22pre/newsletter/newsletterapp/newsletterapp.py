#!/usr/bin/env python
"""
Newsletter app example using the newsletter package.

Also uses:
 * cherrypy for the webserver.
 * pywebsite.sqlitepickle for the database.
 * feedparser for html sanitisation.
 * tinymce rich text editor for editing the html.
 * jquery javascript lib.

depends: cherrypy, pywebsite, feedparser
"""

# pip install cherrypy pywebsite feedparser
import os, smtplib, re, time, hashlib, csv, pprint, subprocess
import xml.sax.saxutils
from email.mime.text import MIMEText
from email.Utils import formatdate


import cherrypy
import feedparser
import pywebsite.sqlitepickle


import sys
_import_again = False
try:
    from .base import NewsletterSend, Newsletter
except ImportError:
    _import_again = True
except ValueError:
    _import_again = True

if _import_again:
    # a hack to put the newsletter package in the path.
    sys.path.append(os.path.join("..", ".."))
    from newsletter.base import NewsletterSend, Newsletter



def sendmail(fromaddr, toaddrs, subject, body, 
            smtp_host, smtp_username, smtp_password, use_sendmail_cmd):
    """ sendmail(fromaddr, toaddrs, subject, body, 
                 smtp_host, smtp_username, smtp_password) sends an email.
    """
    # http://docs.python.org/library/email-examples.html#email-examples
    #msg = MIMEText(body, "plain")
    msg = MIMEText(body, "html")

    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = toaddrs
    msg["Date"] = formatdate(localtime=True)


    if use_sendmail_cmd:
        # try to use the local sendmail cmd to send the mail.
        email_message = msg.as_string()
        print email_message
        _local_sendmail_cmd(email_message)

    else:

        server = smtplib.SMTP(smtp_host)
        server.ehlo()
        # if we are using the SSL port then we try and use tls.
        if smtp_host.endswith(":587"):
            server.starttls()
        if smtp_username:
            server.login(smtp_username, smtp_password)
        server.sendmail(fromaddr, toaddrs, msg.as_string())
        server.quit()



def _local_sendmail_cmd(email_message):
    """ _local_sendmail_cmd uses the unix sendmail command to send the email.
    """
    sendmail_location = "/usr/sbin/sendmail"
    pipe = subprocess.Popen([sendmail_location, "-t"], stdin=subprocess.PIPE)
    pipe.communicate(email_message)

    retcode = pipe.wait()
    if retcode is not None and retcode >> 8:
        raise RuntimeError("email failed to send :%s:" % retcode)





def __utf8(value):
    if isinstance(value, unicode):
        return value.encode("utf-8")
    assert isinstance(value, str)
    return value
def qhtml(value):
    """ qhtml(value) returns an html encoded value.

        >>> qhtml(">")
        '&gt;'
        >>> qhtml("a")
        'a'
        >>> qhtml(u"a")
        'a'
    """
    return __utf8(xml.sax.saxutils.escape(value))

def sanitise_html(html):
    """ santise_html(html) returns some sanitised html.  
          It can be used to try and avoid basic html insertion attacks.
        
        >>> sanitise_html("<p>hello</p>")
        '<p>hello</p>'
        >>> sanitise_html("<script>alert('what')</script>")
        ''
    """
    return feedparser._sanitizeHTML(html, "utf-8", "text/html")


def validate_email(email):
    """ returns True if email is a valid email address

        >>> validate_email('joe@example.com')
        True
        >>> validate_email('joe.example.com')
        False
        >>> validate_email('joe+here@example.com')
        True

        NOTE: not completely correct, but will at least stop many problem 
              emails entering the system.
    """
    ereg = "^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$"
    return re.match(ereg, email) != None

def parse_email_csv(csv_text):
    """ parse_email_csv(str) returns a list of dicts with the fields.

        >>> parse_email_csv(chr(10).join(["email,full_name", "joe@example.com,Joe Bloggs"]))
        [{u'email': u'joe@example.com', u'full_name': u'Joe Bloggs'}]

        >>> parse_email_csv(chr(10).join(["email,full_name", "joe@example.com,Joe Bloggs", "arg@example.com,my name is jen"]))
        [{u'email': u'joe@example.com', u'full_name': u'Joe Bloggs'}, {u'email': u'arg@example.com', u'full_name': u'my name is jen'}]

        >>> parse_email_csv(chr(10).join([u"email,full_name", "joe@example.com,Joe Bloggs"]))
        [{u'email': u'joe@example.com', u'full_name': u'Joe Bloggs'}]

        >>> parse_email_csv(chr(10).join(["email,full_name", "joeexample.com,Joe Bloggs"]))
        Traceback (most recent call last):
        ...
        ValueError: ('email not valid', u'joeexample.com')

        >>> parse_email_csv(chr(10).join(["email,full_name", "joe@example.com"]))
        Traceback (most recent call last):
        ...
        ValueError: ('need same number of fields for each row', ([u'email', u'full_name'], [u'joe@example.com']))
    """

    details = []
    # the python 2.x csv module is buggy for unicode.
    lines = csv_text.replace("\r\n", "\n").split("\n")
    rows = [map(unicode, row) for row in csv.reader(lines)]

    fields = rows[0]
    
    if len(fields) < 2 or fields[0] != "email" or fields[1] != "full_name":
        raise ValueError("First two fields should be email,full_name", 
                         (fields, rows))

    for row in rows[1:]:
        if len(row) != len(fields):
            raise ValueError("need same number of fields for each row", 
                             (rows[0], row))
        if not validate_email(row[0]):
            raise ValueError("email not valid", row[0])

        details.append(dict(zip(fields, row)))
    return details


def template_replace(html, replace_vars):
    """ for the given html, we replace the variables in it.  
    
    The format for variables is %var_name%.

    If the var_name starts with an underscore, then it is not quoted.

    >>> html = "hello %somevar%.  What is your favourite %thing%?"
    >>> replace_vars = {"somevar": "there", "thing": "colour"}
    >>> template_replace(html, replace_vars)
    'hello there.  What is your favourite colour?'

    >>> html = "hello %somevar%. Favourite %thing%?"
    >>> replace_vars = {"somevar" : "there", 
    ...                 "thing" : "<script>alert('what')</script>"}
    >>> template_replace(html, replace_vars)
    "hello there. Favourite &lt;script&gt;alert('what')&lt;/script&gt;?"


    We can not use None as a value.
    >>> replace_vars = {"somevar": None, "thing": "colour"}
    >>> template_replace(html, replace_vars)
    Traceback (most recent call last):
    ...
    ValueError: ('error with replacement variables, can not be None', {'thing': 'colour', 'somevar': None})


    If we use a variable name with an underscore it will be inserted without quoting.
    >>> replace_vars = {"_somevar": "<b>you<b>", "thing": "colour"}
    >>> html = "hello %_somevar%. Favourite %thing%?"
    >>> template_replace(html, replace_vars)
    'hello <b>you<b>. Favourite colour?'
    """
    for v, r in replace_vars.items():
        if r is None:
            raise ValueError("error with replacement variables, can not be None", replace_vars)
        search_for = "%" + v + "%"
        if v.startswith("_"):
            safeish_html = r
        else:
            quoted_html = qhtml(r)
            safeish_html = sanitise_html(quoted_html)

        html = html.replace(search_for, safeish_html)

    return html



def encrypt_pwd(token):
    """ encrypt_pwd(token) encrypts for http basic auth.
    """
    return hashlib.sha1(token).hexdigest()




class MyNewsletterSend(NewsletterSend):
    """ MyNewsletterSend(config)
    """


    def __init__(self, config):
        """ MyNewsletterSend(config)
        """
        self.config = config
        self.static_dir = config.get("static_dir")
        self.db_dir = config.get("db_dir")
        self.fromaddr = config.get("from_addr")

        join = os.path.join
        self.send_parts_db_path = join(self.db_dir, "send_parts.sqlitepickle")
        self.newsletter_sends_db_path = join(self.db_dir, 
                                             "newsletter_sends.sqlitepickle")
        NewsletterSend.__init__(self)

    def send_send_part(self, send_part):
        """ send_send_part(send_part) sends the given send_part.
        """
        #print send_part
        toaddr = send_part['email']
        subject = send_part['subject']
        body = send_part['body']

        # hack to get the secret for the unsubscribe link.
        the_user = self._n._subscribers.get(send_part['user_id'], None)
        if the_user is None:
            secret = self._n._subscribers.get(send_part['user_id'])['secret']
        else:
            secret = ""

        # replace template values.
        replace_vars = {"FULL_NAME" : send_part.get('full_name', ''),
                        "EMAIL" :  send_part.get('email', ''),
                        "email" :  send_part.get('email', ''),
                        "secret" :  secret,
                        "base_url" :  self.config.get("base_url", ''),
        }

        body = template_replace(body, replace_vars)

        # let us sleep a little here before sending.
        time_to_sleep = float( self.config.get("smtp_sleep_between_sends") )
        time.sleep(time_to_sleep)

        sendmail(self.config.get('from_addr'), 
                toaddr, subject, body, 
                self.config.get('smtp_host'), 
                self.config.get('smtp_username'), 
                self.config.get('smtp_password'),
                self.config.get('sendmail_cmd'),
                )
        return True

    def make_send_parts_db(self):
        """ make_send_parts_db() returns a key/value 
                store for the send_parts_db
        """
        return pywebsite.sqlitepickle.SQLPickle(self.send_parts_db_path)
    def make_newsletter_sends_db(self):
        """ make_newsletter_sends_db() returns a key/value 
                store for the newsletter_sends_db
        """
        return pywebsite.sqlitepickle.SQLPickle(self.newsletter_sends_db_path)

class MyNewsletter(Newsletter):
    """ MyNewsletter(config)
    """
    def __init__(self, config):
        """ MyNewsletter(config)
        """
        self.config = config
        self.static_dir = config.get("static_dir")
        self.db_dir = config.get("db_dir")

        if not os.path.exists(self.db_dir):
            raise ValueError("Database dir for '%s' config item :db_dir: does not exist. Check the path, or consider making the directory." % self.db_dir)

        self.subscribers_db_path = os.path.join(self.db_dir, 
                                                "subscribers.sqlitepickle")

        self.fromaddr = config.get("from_addr")
             
        Newsletter.__init__(self)

    def email_template(self, template_name):
        """ email_template(template_name) returns a html template.
        """
        tmpl = os.path.join(self.static_dir, 
                            "email_templates", 
                            template_name + ".html")
        return open(tmpl, "rb").read()

    def send_subscribe_confirm_email(self, uid, user):
        """ send_subscribe_confirm_email(uid, user) sends a
               confirmation email to the given user.
        """
        toaddr = user['email']
        subject = "newsletter signup for great justice"

        body = self.email_template("send_subscribe_confirm_email")

        replace_vars = {"base_url": self.config.get("base_url"), 
                        "email": user['email'],
                        "secret": user['secret']}
        body = template_replace(body, replace_vars)

        sendmail(self.config.get('from_addr'), 
                toaddr, subject, body, 
                self.config.get('smtp_host'), 
                self.config.get('smtp_username'), 
                self.config.get('smtp_password'),
                self.config.get('sendmail_cmd'),
                )

    def send_unsubscribe_confirm_email(self, uid, user):
        """ send_unsubscribe_confirm_email(uid, user) sends an 
              unsubscribe confirmation email to the given user.
        """
        toaddr = user['email']
        subject = "newsletter unsubscribe signup for great justice"

        body = self.email_template("send_unsubscribe_confirm_email")
        replace_vars = {"base_url": self.config.get("base_url"), 
                        "email": user['email'],
                        "secret": user['secret']}

        body = template_replace(body, replace_vars)

        sendmail(self.config.get('from_addr'), 
                toaddr, subject, body, 
                self.config.get('smtp_host'), 
                self.config.get('smtp_username'), 
                self.config.get('smtp_password'),
                self.config.get('sendmail_cmd'),
                )

    def make_subscribers_db(self):
        """ make_subscribers_db() returns a key value store to be used as
              the subscribers db.
        """
        return pywebsite.sqlitepickle.SQLPickle(self.subscribers_db_path)





def create_SendMessages(mount_on, config):
    """ from the config given search for send_message_ ones.
        create instances of SendMessage on the object mount_on
    """
    for k in config.keys():
        if k.startswith("send_message_"):
            send_message_config = config[k]
            if send_message_config['send_message']:
                setattr(mount_on, 
                        send_message_config["mount_point"], 
                        SendMessage(config["newsletter"], 
                                    send_message_config, 
                                    mount_on))



class SendMessage(object):
    
    def __init__(self, config, send_message_config, web_newsletter):
        self.config = config
        self.send_message_config = send_message_config
        self.web_newsletter = web_newsletter

    def __call__(self, **kwargs):
        return self.send_message(**kwargs)
    
    def send_message(self, **kwargs):
        """ send_message(**kwargs) sends message 

            NOTE: Not exposed by default.  Need to enable it in config

            kwargs are used as variables to replace in the body and subject.

            wrap_it - if True we wrap html response in a header footer.
            toaddr - a single email address to send to.
        """
        if not self.send_message_config['exposed']:
            raise ValueError("not exposed")

        if not self.validate_input(kwargs):
            raise ValueError("not what we were expecting")
        
        wrap_it = kwargs.get('wrap_it', None)


        email_body_template = self.send_message_config.get('email_body_template')
        email_subject_template = self.send_message_config.get('email_subject_template')
        web_front_response_template = self.send_message_config.get('web_front_response_template')
        
        toaddr = self.send_message_config.get('toaddr', '')

        # We get the toaddr from the kwargs if it is set to None in the header
        if toaddr is None:
            toaddr = kwargs.get('toaddr', None)
            if toaddr is None or not validate_email(toaddr):
                raise ValueError("toaddr invalid")
        
        if toaddr == '':
            raise ValueError("toaddr invalid")

        replace_vars = dict(kwargs)
        replace_vars['toaddr'] = toaddr

        subject = self.web_newsletter.admin.email_template(email_subject_template)
        body = self.web_newsletter.admin.email_template(email_body_template)
        

        # replace the variables in the template.
        subject = template_replace(subject, replace_vars)
        body = template_replace(body, replace_vars)
        
        sendmail(self.send_message_config.get('fromaddr'), 
                toaddr, subject, body, 
                self.config.get('smtp_host'), 
                self.config.get('smtp_username'), 
                self.config.get('smtp_password'),
                self.config.get('sendmail_cmd'),
                )
        
        return self.web_newsletter.html_template(web_front_response_template, wrap_it)
        
        
    def validate_input(self, kwargs):
        """ returns True if the input is valid.
        """
        # see if a validation function has been used defined in the config file.
        validate_input = self.send_message_config.get('validate_input', None)
        if validate_input is not None:
            #validate_input = eval(validate_input)
            return validate_input(kwargs)
        
        return True

    exposed = True







class WebNewsletter(object):
    """ WebNewsletter() is an application meant for cherrypy for 
          sending email newsletters.
    """
    def load(self, config):
        """ load(config) loads the application given the configuration.
        """
        self.config = config["newsletter"]

        self.static_dir = self.config.get("static_dir")
        self.db_dir = self.config.get("db_dir")
        self.py_dirs = self.config.get("py_dirs", None)

        if self.py_dirs is not None:
            for py_dir in self.py_dirs:
                if py_dir not in sys.path:
                    sys.path.append(py_dir)

        self.fromaddr = self.config.get("from_addr")

        self._default_vars = {"base_url" : self.config.get('base_url'),
                             }


        self._n = MyNewsletter(self.config)
        self._ns = MyNewsletterSend(self.config)
        self._ns._n = self._n

        self.header = self.html_template("header", False, False)
        self.footer = self.html_template("footer", False, False)

        self.admin = WebNewsletterAdmin(self._n, self._ns, self.config)

        # mount any send_message_ from the config.
        create_SendMessages(self, config)



    def html_template(self, template_name, 
                            wrap_it = None, 
                            replace_vars = None):
        """ html_template(template_name) returns the given template.

            wrap_it - if not False, then we wrap it in the header and footer.
            replace_vars - we replace the dict of vars.
        """
        tmpl = os.path.join(self.static_dir, "web_front_templates", 
                            template_name + ".html")
        the_html = open(tmpl, "rb").read()

        # get rid of trailing new lines
        if the_html[-1] == "\n":
            the_html = the_html[:-1]


        if replace_vars is None:
            replace_vars = {}

        the_html = self.in_header_footer(the_html, wrap_it)
        if replace_vars is not False:
            the_html = self.html_render(the_html, replace_vars)

        return the_html

    def html_render(self, html, replace_vars):
        """ renders the html with the replace_vars
              Also uses some default variables, which can be 
              over ridden with the ones passed in.
        """
        # 
        combined_vars = dict(self._default_vars)
        combined_vars.update(replace_vars)
        return template_replace(html, combined_vars)


    def in_header_footer(self, msg, wrap_it):
        """ return the passed in msg in something if wrap_it is True.
        """
        if wrap_it is True:
            return "\n".join([self.header, 
                                "<div class='newsletterMsg'>", 
                                msg,
                                "</div>", 
                                self.footer])
        else:
            return msg

    def index(self, wrap_it = True):
        """ index(wrap_it = True) returns the default index page.
            wrap_it - if True we wrap the main message in the 
                        header and footer.
        """
        return self.html_template("index", wrap_it)

    def subscribe(self, email, full_name, wrap_it = True):
        """ subscribe(email, full_name, wrap_it = True)
        """
        if validate_email(email):
            info = {"full_name": full_name,
                    "tags": ""}
            if self._n.subscribe(email, info):
                return self.html_template("subscribe", wrap_it)
        else:
            return self.html_template("subscribe_email_invalid", wrap_it)

    def confirm_subscribe(self, email, secret, wrap_it = True):
        """ confirm_subscribe(email, secret, wrap_it = True)
        """
        if self._n.confirm_subscribe(email, secret):
            return self.html_template("confirm_subscribe", wrap_it)

    def confirm_unsubscribe(self, email, secret, wrap_it = True):
        """ confirm_unsubscribe(email, secret, wrap_it = True)
        """
        if self._n.confirm_unsubscribe(email, secret):
            return self.html_template("confirm_unsubscribe", wrap_it)





    index.exposed = True
    subscribe.exposed = True
    confirm_subscribe.exposed = True
    confirm_unsubscribe.exposed = True



class WebNewsletterAdmin(object):
    """ WebNewsletterAdmin(n, ns, config)
    """

    def __init__(self, n, ns, config):
        """ WebNewsletterAdmin(n, ns, config)
        """
        self._n = n
        self._ns = ns

        self.config = config
        self.static_dir = config.get("static_dir")
        self.db_dir = config.get("db_dir")

        admin_base_url = self.config.get('admin_base_url', self.config.get('base_url') + "admin/")
        self._default_vars = {"base_url" : self.config['base_url'],
                              "admin_base_url": admin_base_url,
                             }

    def html_template(self, template_name, wrap_it = True, replace_vars = None):
        """ html_template(template_name) returns the html for 
              the given template, wrapped in a header and footer.
        """

        the_html = self._html_template(template_name)
        if replace_vars is None:
            replace_vars = {}

        the_html = self.in_header_footer(the_html, wrap_it)
        if replace_vars is not False:
            the_html = self.html_render(the_html, replace_vars)

        return the_html




    def _html_template(self, template_name):
        """ html_template(template_name) returns the html for 
              the given template.
        """
        tmpl = os.path.join(self.static_dir, 
                            "web_admin_templates", 
                            template_name + ".html")
        return open(tmpl, "rb").read()

    def html_render(self, html, replace_vars):
        """ renders the html with the replace_vars
              Also uses some default variables, which can be 
              over ridden with the ones passed in.
        """
        combined_vars = dict(self._default_vars)
        combined_vars.update(replace_vars)
        return template_replace(html, combined_vars)

    def in_header_footer(self, msg, wrap_it = True):
        """ return the passed in msg in something if wrap_it is True.
        """
        if wrap_it is True:
            return "\n".join([self._html_template("header"),
                                self._html_template("menu"),
                                "<div class='newsletterAdminMsg'>", 
                                msg,
                                "</div>", 
                                self._html_template("footer"),
                                ])
        else:
            return msg

    def index(self):
        """ returns the default index page.
        """
        return self.html_template("index")

    def import_emails(self, csv_text = None, 
                            subscribe_automatically = False):
        """ For importing emails into the newsletter.
        """

        if subscribe_automatically == "yes":
            subscribe_automatically = True
        else:
            subscribe_automatically = False

        if csv_text is None:
            # show input fields
            return self.html_template("import_emails")
            
        else:
            # parse all the csv first, and validate it.
            details = parse_email_csv(csv_text)
            for d in details:
                info = dict(d)
                # remove the email field
                info.pop('email')
                # we set it as subscribed automatically.
                self._n.subscribe(d['email'], 
                                  info = info, 
                                  subscribed = subscribe_automatically)
            return self.html_template("import_success")

    def create(self, newsletter_send_id, subject, body):
        """ create(newsletter_send_id, subject, body)
        """
        self._ns.create(subject, body)
        return self.html_template("create")

    def update(self, newsletter_send_id, subject, body):
        """ update(newsletter_send_id, subject, body)
        """
        self._ns.update_message(newsletter_send_id, subject, body)
        return self.html_template("update")

    def list_sends(self):
        """ list_sends() lists the newsletter sends we have done.
        """
        top = self._html_template("list_sends_top")
        row = self._html_template("list_sends_row")
        add_tag = self._html_template("list_sends_add_tag")
        bottom = self._html_template("list_sends_bottom")

        tags = self._get_tags_subscribers().keys()

        middle = ""
        for send_id in self._ns.newsletter_send_ids():
            asend = self._ns.get(send_id)
            status = asend['status']
            # add buttons for each tag.
            add_tag_parts = ""
            for tag in tags:
                replace_vars = {"send_id": send_id, "tag": tag}
                add_tag_parts += self.html_render(add_tag, replace_vars)

            replace_vars = {"send_id": send_id, 
                            "status":status, 
                            "_add_tag_parts": add_tag_parts}
            middle += self.html_render(row, replace_vars)

        the_html = "\n".join((top, middle, bottom))

        return self.html_render(self.in_header_footer(the_html), {})

    def send(self, newsletter_send_id):
        """ send(newsletter_send_id)
        """
        if self._ns.send(newsletter_send_id):
            return "sent %s" % newsletter_send_id
        else:
            return "did not send %s" % newsletter_send_id
        
    def send_all(self):
        """ send_all() sends all of the open newsletter sends.
        """
        for newsletter_send_id in self._ns.newsletter_send_ids():
            asend = self._ns.get(newsletter_send_id)
            status = asend['status']
            if status == "open":
                self._ns.send(newsletter_send_id)

    def send_test_email(self, newsletter_send_id, subscriber_id):
        """ send_test_email(newsletter_send_id, subscriber_id) sends 
              off a test email for the given newsletter send and subscriber.
        """
        users = [self._n.get_subscriber(subscriber_id)]
        self._ns.send_test_email(newsletter_send_id, users)
        return self.html_template("send_test_email")


    def email_template(self, template_name):
        """ email_template(template_name) returns a html template.
        """
        tmpl = os.path.join(self.static_dir, 
                            "email_templates", 
                            template_name + ".html")
        the_html = open(tmpl, "rb").read()

        # get rid of trailing new lines
        if the_html[-1] == "\n":
            the_html = the_html[:-1]

        return the_html

    def edit(self, newsletter_send_id = None):
        """ edit(newsletter_send_id) edits the given newsletter send.
        """
        if newsletter_send_id == None:
            action = "create"
            a_newsletter_send = None
            newsletter_send_id = ""
        else:
            action = "../update"
            a_newsletter_send = self._ns.get(newsletter_send_id, None)

        if a_newsletter_send == None:
            subject = ""
            body = self.email_template("default_send")
        else:
            subject = a_newsletter_send['subject']
            body = a_newsletter_send['body']

        replace_vars = {
            "action": action,
            "newsletter_send_id": newsletter_send_id,
            "subject": subject,
            "body": body,
        }
        return self.html_template("edit", True, replace_vars)

    def list_subscribers(self, send_id = None, show_attached = None):
        """ list_subscribers(send_id, show_attached)
            send_id - if not None then allow adding to that send_id.
            show_attached - if True, then we only show subscribers
                 attached to the send_id given.
        """
        top = self._html_template("list_subscribers_top")
        bottom = self._html_template("list_subscribers_bottom")
        if send_id and show_attached:
            tmpl = "list_subscribers_row_show_attached"
            row = self._html_template(tmpl)
        elif send_id:
            #row = self._html_template("list_subscribers_row")
            row = self._html_template("list_subscribers_row_send_id")
        else:
            row = self._html_template("list_subscribers_row")

        middle = ""
        if send_id and show_attached:
            for s in self._ns.get_send_parts(send_id):
                send_part_id = s['id']
                #middle += row % (s['email'], s['id'], 
                #                 send_id, send_id, s['user_id'])
                replace_vars = {"send_part_email": s['email'], 
                                "send_part_id": s['id'],
                                "send_part_user_id": s['user_id'],
                                "send_id": send_id,
                                }
                middle += self.html_render(row, replace_vars)


        else:
            if send_id is None:
                the_send_id = ""
            else:
                the_send_id = send_id
            
            for k, s in self._n.subscribers(items = True):
                tags = s.get('tags', '')
                replace_vars = {"send_part_email": s['email'], 
                                "subscribers_id": k,
                                "tags": tags,
                                "send_id": the_send_id,
                                }
                middle += self.html_render(row, replace_vars)
                    

        the_html = "\n".join([top, middle, bottom])
        return self.html_render(self.in_header_footer(the_html), {})


    def add_subscriber_to_send(self, subscriber_id, send_id):
        """ add_subscriber_to_send(subscriber_id, send_id)
        """
        subscriber = self._n.get_subscriber(subscriber_id)
        self._ns.add_users(send_id, [subscriber])
        return self.html_template("add_subscriber_to_send")

    def add_all_subscribers_to_send(self, send_id):
        """ add_all_subscribers_to_send(send_id) adds all the subscribers 
              to this send_id
        """
        self._ns.add_users(send_id, self._n.subscribers())
        return self.html_template("add_all_subscribers_to_send")

    def _get_tags_subscribers(self):
        """ returns a dict keyed by tags, valued by a list of 
              subscribers with that tag.
        """
        r = {}
        for s in self._n.subscribers():
            tags = s.get('tags', '').split()
            for tag in tags:
                if not r.has_key(tag):
                    r[tag] = []
                r[tag].append(s)
        return r


    def add_all_subscribers_with_tag_to_send(self, send_id, tag):
        """ adds all subscribers with the given tag to the send_id given.
        """
        to_add = []
        for s in self._n.subscribers():
            tags = s.get('tags', '').split()
            if tag in tags:
                to_add.append(s)
            
        self._ns.add_users(send_id, to_add)
        return self.html_template("add_all_subscribers_with_tag_to_send")
        



    def remove_subscriber_from_send(self, send_part_id, send_id):
        """ remove_subscriber_from_send(send_part_id, send_id) removes 
              the send_part from the send.
        """
        self._ns.remove_user(send_id, send_part_id)
        return self.html_template("remove_subscriber_from_send")
        
    def help(self):
        return self.html_template("help")





    # expose these methods so cherrypy can access these methods
    #  through the web.
    index.exposed = True
    import_emails.exposed = True
    create.exposed = True
    update.exposed = True
    list_sends.exposed = True
    send.exposed = True
    send_test_email.exposed = True
    edit.exposed = True
    list_subscribers.exposed = True
    add_subscriber_to_send.exposed = True
    add_all_subscribers_to_send.exposed = True
    add_all_subscribers_with_tag_to_send.exposed = True
    remove_subscriber_from_send.exposed = True
    help.exposed = True



def make_new_install(dst_directory):
    """ make_new_install(dst_directory) 
    """
    # Find the directory of files for the newsletter and copy them over.
    #  Awesome.
    if os.path.exists(dst_directory):
        raise ValueError("%s already exists")

    import shutil

    # a hack to put the newsletter package in the path.
    sys.path.append(os.path.join("..", ".."))
    import newsletter.newsletterapp
    
    # do not copy in .py files.
    def ignorepy(src, names):
        return [n for n in names if (n.endswith("py") or n.endswith("pyc"))]

    src_dir =  os.path.split(os.path.abspath(newsletter.newsletterapp.__file__))[0]
    
    
    #print (src_dir, dst_directory)
    shutil.copytree(src_dir, dst_directory, ignore=ignorepy)

    # create the log directory if it doesn't exist.
    log_dir = os.path.join(dst_directory, "log")
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    
    db_dir = os.path.join(dst_directory, "db")
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)


    # update the config file to show the dst directory.
    



def main():
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port",
                       type = int,
                      help="port to listen on")
    parser.add_option("-m", "--mount_point", dest="mount_point",
                      default = "",
                      help="mount point to mount on")
    parser.add_option("-c", "--config", dest="config",
                      default = "newsletterapp.ini",
                      help="config ini file")
    parser.add_option("-t", "--test", dest="test",
                      default = False, action="store_true",
                      help="run tests")
    parser.add_option("-s", "--send_all", dest="send_all",
                      default = False, action="store_true",
                      help="send the email queue")
    parser.add_option("-n", "--new_install", dest="new_install",
                      default = "",
                      help="create a new install directory")

    (options, args) = parser.parse_args()


    if options.test:
        def _test():
            import doctest
            doctest.testmod()
        _test()
    elif options.new_install:
        # woo, hoo.  We are creating a new install directory.
        make_new_install(options.new_install)

    elif options.send_all:
        # run just to send the newsletters.
        cfg = options.config
        mount_point = options.mount_point
        wnl = WebNewsletter()
        cherrypy.tree.mount(wnl, mount_point, config = cfg)
        wnl.load(cherrypy.tree.apps[mount_point].config)
        # send all of the open newsletters
        wnl.admin.send_all()
        
    else:
        # We run the webserver.
        mount_point = options.mount_point
        cfg = options.config

        py_dir = os.path.join(os.path.split(cfg)[0], "pypackages")
        if py_dir not in sys.path:
            sys.path.append(py_dir)
        
        
        # Site-wide (global) config
        log_dir = os.path.join("log")
        #if not os.path.exists(log_dir):
        #    os.mkdir(log_dir)
        #cherrypy.config.update({'environment': 'production'})

        cherrypy.config.update({'log.error_file': os.path.join(log_dir, 'error.log'),
                                #...
                                })


        wnl = WebNewsletter()

        # configuration as a python datastructure, rather than via ini file.
        if 0:
            cfG = {'/': {'tools.staticdir.root': os.path.join(os.path.abspath('.'), 'static')},
                   '/admin': {'tools.basic_auth.encrypt': encrypt_pwd,
                              'tools.basic_auth.on': True,
                              'tools.basic_auth.realm': 'Please Enter User/Password',
                              'tools.basic_auth.users': {'admin': encrypt_pwd("admin")}},
                   '/css': {'tools.staticdir.dir': 'css', 'tools.staticdir.on': True},
                   '/images': {'tools.staticdir.dir': 'images', 'tools.staticdir.on': True},
                   '/js': {'tools.staticdir.dir': 'js', 'tools.staticdir.on': True},
                   '/tiny_mce': {'tools.staticdir.dir': 'tiny_mce', 'tools.staticdir.on': True},
                   'newsletter': {'base_url': "http://localhost:" + str(cherrypy.server.socket_port) + "/",
                                  'db_dir': 'db',
                                  'smtp_host': 'localhost',
                                  'smtp_password': '',
                                  'smtp_sleep_between_sends': 1.0,
                                  'smtp_username': '',
                                  'static_dir': 'static'}}

        cherrypy.tree.mount(wnl, mount_point, config = cfg)

        # See if we have a custom WebNewsletter. If so, use that.
        newsletter_cfg = cherrypy.tree.apps[mount_point].config['newsletter']
        if newsletter_cfg.get('custom_webnewsletter', None):
            wnl = newsletter_cfg.get('custom_webnewsletter', None)()
            cherrypy.tree.mount(wnl, mount_point, config = cfg)

        # Need to call load() after mounting it so we 
        #   have the config from cherrypy.
        wnl.load(cherrypy.tree.apps[mount_point].config)

        # we use the port from the cmd line if it exists.
        if options.port:
            cherrypy.server.socket_port = options.port
        else:
            global_cfg = cherrypy.tree.apps[mount_point].config.get('global', {})
            cfg_port = global_cfg.get('server.socket_port', 9999)
            cherrypy.server.socket_port = cfg_port

        #pprint.pprint(cherrypy.tree.apps[mount_point].config)

        cherrypy.engine.start()
        cherrypy.engine.block()


if __name__ == "__main__":
    main()
