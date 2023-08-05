"""

Setting up a Newsletter, and subscribing people to it.

    >>> import pprint
    >>> class MyNewsletter(Newsletter):
    ...     _fake_emails = []
    ...     def send_subscribe_confirm_email(self, uid, user):
    ...         self._fake_emails.append(("subscribe", uid, user))
    ...     def send_unsubscribe_confirm_email(self, uid, user):
    ...         self._fake_emails.append(("unsubscribe", uid, user))

    >>> n = MyNewsletter()
    >>> n.subscribe("bla@example.com")
    True

    >>> secret = n.subscribers(unconfirmed = True)[0]['secret']
    >>> n.confirm_subscribe(email = 'bla@example.com', secret = secret)
    True

    >>> n.subscribers()
    [{'secret': '...', 'email': 'bla@example.com', 'subscribed': True}]

    >>> n.subscribe("notbla@example.com", subscribed = True)
    True

    >>> len(n.subscribers())
    2



Setting up a NewletterSend and sending email to people on it.
    >>> class MyNewsletterSend(NewsletterSend):
    ...     def send_send_part(self, send_part):
    ...         print ('sending log ' + pprint.pformat(send_part))
    ...         return True

    >>> ns = MyNewsletterSend()
    >>> newsletter_send_id = ns.create("a subject", "this is the body of the message")

Add some users to the send.
    >>> ns.add_users(newsletter_send_id,  n.subscribers())
    True

Check that the users have been added correctly.

    >>> import pprint
    >>> len(list(ns._send_parts.items()))
    2

    >>> pprint.pprint(list(sorted([sp for sp in ns._send_parts.values()])))
    [{'body': 'this is the body of the message',
      'email': 'bla@example.com',
      'full_name': '',
      'id': '...',
      'newsletter_send_id': '...',
      'status': 'open',
      'subject': 'a subject',
      'user_id': '...'},
     {'body': 'this is the body of the message',
      'email': 'notbla@example.com',
      'full_name': '',
      'id': '...',
      'newsletter_send_id': '...',
      'status': 'open',
      'subject': 'a subject',
      'user_id': '...'}]


Make sure we can not add the same users multiple times to the same newsletter send.
    >>> ns.add_users(newsletter_send_id,  n.subscribers())
    True
    >>> len(list(ns._send_parts.items()))
    2


Send the newsletter.
    >>> ns.send(newsletter_send_id)
    sending log {'body': 'this is the body of the message',
     'email': 'bla@example.com',
     'full_name': '',
     'id': '...',
     'newsletter_send_id': '...',
     'status': 'sending',
     'subject': 'a subject',
     'user_id': '...'}
    sending log {'body': 'this is the body of the message',
     'email': 'notbla@example.com',
     'full_name': '',
     'id': '...',
     'newsletter_send_id': '...',
     'status': 'sending',
     'subject': 'a subject',
     'user_id': '...'}
    True



Mini todo list.

* actions
  X - create, update, delete newsletters.
  X- select people to send email to.
    X - everyone on the list.
    - select categories of people.
  - unsubscribe through url.  Given an email, and a secret code.
  - unsubscribe through admin section.  Given an email.
    - search for users by email.
  - subscription form
    - 
  X - confirmation email, for double opt in.  Sends them a url with a secret to click on.
    - 














"""

import uuid
import time

class Newsletter(object):
    """

    We create a subclass which mocks out the sending of confirmation emails.
        >>> class MyNewsletter(Newsletter):
        ...     _fake_emails = []
        ...     def send_subscribe_confirm_email(self, uid, user):
        ...         self._fake_emails.append(("subscribe", uid, user))
        ...     def send_unsubscribe_confirm_email(self, uid, user):
        ...         self._fake_emails.append(("unsubscribe", uid, user))
        

        >>> n = MyNewsletter()
        >>> n.subscribers()
        []

        >>> n.subscribe("bla@example.com")
        True
        >>> n.subscribers(unconfirmed = True)
        [{'secret': '...', 'email': 'bla@example.com', 'subscribed': False}]

    Add the same subscriber again, and we should not overwrite details.
        >>> n.subscribe("bla@example.com")
        True

    See if we sent the confirmation email.
        >>> n._fake_emails[0]
        ('subscribe', '...', {'secret': '...', 'email': 'bla@example.com', 'subscribed': False})

        >>> n.subscribers(unconfirmed = True)
        [{'secret': '...', 'email': 'bla@example.com', 'subscribed': False}]




        >>> secret = n.subscribers(unconfirmed = True)[0]['secret']
        >>> n.confirm_subscribe(email = 'bla@example.com', secret = secret)
        True

        >>> n.subscribers()
        [{'secret': '...', 'email': 'bla@example.com', 'subscribed': True}]


        >>> n.unsubscribe(email = 'bla@example.com')
        True

        >>> n._fake_emails[1]
        ('unsubscribe', ..., {'secret': '...', 'email': 'bla@example.com', 'subscribed': True})


    Let us unsubscribe someone who is not subscribed.  Returns True anyway,
      because otherwise it could leak subscribers.
        >>> n.unsubscribe(email = 'notsubbed@example.com')
        True
        

        >>> n.confirm_unsubscribe(email = 'bla@example.com', secret = secret)
        True

        >>> n.subscribers()
        []

        >>> n.subscribers(unconfirmed = True)
        []
    """

    def __init__(self):
        """
        """
        # keyed by unique id, valued by a dict of info.
        self._subscribers = self.make_subscribers_db()

    def make_subscribers_db(self):
        """ make_subscribers_db() returns a dict like object for storing the
                subscribers.
        """
        return {}



    def subscribe(self, email, info = {}, subscribed = False):
        """
            subscribed - if True we confirm the subscription automatically.  
                         If False we ask the user to confirm the subscription.
        """
        if subscribed not in [True, False]:
            raise ValueError("subscribed needs to be True or False")

        user = {"email": email}
        user.update(info)
        user['secret'] = self._make_secret()
        user['subscribed'] = subscribed


        u = [u for u in self._subscribers.values() if u['email'] == email]
        if u:
            # If we are already subscribed, do not overwrite their details.
            pass
        else:
            uid = self._make_uid()
            user["user_id"] = uid
            self._subscribers.update({uid: user})
            if subscribed:
                # we confirm the subscription automatically.
                self.confirm_subscribe(email = user['email'], secret = user['secret'])
            else:
                self.send_subscribe_confirm_email(uid, user)


        return True


    def send_subscribe_confirm_email(self, uid, user):
        """
        """
        pass

    def send_unsubscribe_confirm_email(self, uid, user):
        """
        """
        pass



    def confirm_subscribe(self, email, secret):
        """
        """
        # get the user with this email and secret.
        for uid,u in self._subscribers.items():
            if u['email'] == email and u['secret'] == secret:
                u['subscribed'] = True
                self._subscribers.update({uid:u})
                return True
        return False



    def unsubscribe(self, email):
        """
        """
        # unsubscribes have to use confirm_unsubscribe afterwards.

        users = [u for u in self._subscribers.items() if u[1]['email'] == email]
        if users:
            uid, user = users[0]
            self.send_unsubscribe_confirm_email(uid, user)
            return True
        else:
            return True



    def confirm_unsubscribe(self, email, secret):
        """
        """
        if 0:
            u = [u for u in self._subscribers.items() if u[1]['email'] == email and u[1]['secret'] == secret]
            if u:
                u[0][1]['subscribed'] = False
                uid = u[0][0]
                del self._subscribers[uid]
                return True
            else:
                return False



        for uid,u in self._subscribers.items():
            if u['email'] == email and u['secret'] == secret:
                u['subscribed'] = True
                self._subscribers.pop(uid)
                return True
        return False

            

    def subscribers(self, unconfirmed = False, items = False):
        """
        """
        if items:
            if unconfirmed:
                return [(k, u) for k, u in self._subscribers.items() if u['subscribed'] == False]
            else:
                return [(k, u) for k, u in self._subscribers.items() if u['subscribed'] == True]
        else:
            if unconfirmed:
                return [u for u in self._subscribers.values() if u['subscribed'] == False]
            else:
                return [u for u in self._subscribers.values() if u['subscribed'] == True]


    def get_subscriber(self, subscriber_id):
        return self._subscribers.get(subscriber_id)



    def _make_uid(self):
        return str(uuid.uuid4())

    def _make_secret(self):
        return str(uuid.uuid4())





class NewsletterSend(object):
    """

    There are multiple NewsletterSends for a Newsletter.

    Add subscribers from the Newsletter.








        >>> import pprint
        >>> class MyNewsletterSend(NewsletterSend):
        ...     def send_send_part(self, send_part):
        ...         print ('sending log ' + pprint.pformat(send_part))
        ...         return True
        

        >>> ns = MyNewsletterSend()

    TODO: what about html emails?  Attachments?

        >>> newsletter_send_id = ns.create("a subject", "this is the body of the message")

        >>> ns.update_message(newsletter_send_id, "a new subject", "new message body")
        True


    

    Send a test email.
        >>> ns.send_test_email(newsletter_send_id, [{"email":"asdf2@example.com", "full_name":"Joe blogs", "user_id": "1"}])
        sending log {'body': 'new message body',
         'email': 'asdf2@example.com',
         'full_name': 'Joe blogs',
         'id': '...',
         'newsletter_send_id': '...',
         'status': 'open',
         'subject': 'a new subject',
         'user_id': '1'}
        True





    Add some users to the send.
        >>> ns.add_users(newsletter_send_id,  [{"email":"asdf1@example.com", "full_name":"Joe blogs", "user_id": "1"},
        ...                          {"email":"asdf2@example.com", "full_name":"Jane blogs", "user_id": "2"}])
        True



    Check that the users have been added correctly.

        >>> import pprint
        >>> len(list(ns._send_parts.items()))
        2

        >>> pprint.pprint(list(sorted([sp for sp in ns._send_parts.values()])))
        [{'body': 'new message body',
          'email': 'asdf1@example.com',
          'full_name': 'Joe blogs',
          'id': '...',
          'newsletter_send_id': '...',
          'status': 'open',
          'subject': 'a new subject',
          'user_id': '1'},
         {'body': 'new message body',
          'email': 'asdf2@example.com',
          'full_name': 'Jane blogs',
          'id': '...',
          'newsletter_send_id': '...',
          'status': 'open',
          'subject': 'a new subject',
          'user_id': '2'}]




    Send the newsletter.

        >>> ns.send(newsletter_send_id)
        sending log {'body': 'new message body',
         'email': 'asdf1@example.com',
         'full_name': 'Joe blogs',
         'id': '...',
         'newsletter_send_id': '...',
         'status': 'sending',
         'subject': 'a new subject',
         'user_id': '1'}
        sending log {'body': 'new message body',
         'email': 'asdf2@example.com',
         'full_name': 'Jane blogs',
         'id': '...',
         'newsletter_send_id': '...',
         'status': 'sending',
         'subject': 'a new subject',
         'user_id': '2'}
        True

        >>> ns._newsletter_sends.get(newsletter_send_id)['status']
        'finished'


    Here we try and send the newletter again, but it does not send anything.
        >>> ns.send(newsletter_send_id)
        False







    Testing some internal methods.
        >>> a_newsletter_send = ns._get_newsletter_send(newsletter_send_id)
        
        >>> a_user = {"email":"asdf2@example.com", "full_name":"Joe blogs", "user_id": "1"}
        >>> ns._create_send_part(a_newsletter_send, a_user)
        {'status': 'open', 'body': 'new message body', 'user_id': '1', 'email': 'asdf2@example.com', 'newsletter_send_id': '...', 'full_name': 'Joe blogs', 'id': '...', 'subject': 'a new subject'}

    """

    def __init__(self):
        self._newsletter_sends = self.make_newsletter_sends_db()
        self._send_parts = self.make_send_parts_db()


    def make_send_parts_db(self):
        """ make_send_parts_db() returns a dict like object for storing the
                send_parts.
        """
        return {}

    def make_newsletter_sends_db(self):
        """ make_newsletter_sends_db() returns a dict like object for storing the
                newsletter_sends.
        """
        return {}


    def send_send_part(self, send_part):
        """ send_send_part(send_part) where the actual email sending happens.
        """

        return True


    def get(self, newsletter_send_id, default = None):
        """
        """
        return self._newsletter_sends.get(newsletter_send_id, default)
        

    def create(self, subject, body):
        """ create(subject, body) returns the newsletter_send_id for this send.
        """
        uid = self._make_uid()
        send = dict(id=uid,
                    subject = subject, 
                    body = body, 
                    created = time.time(),
                    status='open')
        self._newsletter_sends.update({uid: send})
        return uid

    def update_message(self, newsletter_send_id, subject, body):
        """ update_message(newsletter_send_id, subject, body) returns True on a
               successful update.
        """
        a_newsletter_send = self._newsletter_sends.get(newsletter_send_id)
        a_newsletter_send["subject"] = subject
        a_newsletter_send["body"] = body
        self._newsletter_sends.update({newsletter_send_id : a_newsletter_send})

        return True


    def send(self, newsletter_send_id):
        """ send(newsletter_send_id) sends the NewsletterSend with the given
                newsletter_send_id.  Returns True on success.
        """
        a_newsletter_send = self._newsletter_sends.get(newsletter_send_id)
        if a_newsletter_send.get("status") != "open":
            return False

        a_newsletter_send["status"] = "sending"
        self._newsletter_sends.update({newsletter_send_id : a_newsletter_send})

        # Send to all of the users attached to this newsletter_send_id
        #           which have not sent already.
        # update the users as we send.
        send_parts = self.get_send_parts(newsletter_send_id)
        for sp in send_parts:
            # update the send part to "sending"
            sp['status'] = 'sending'
            self._send_parts.update(dict(id = sp))

            # send the message.
            self.send_send_part(sp)
            # update the send part to "sent"
            sp['status'] = 'sent'
            self._send_parts.update(dict(id = sp))
            pass

        a_newsletter_send["status"] = "finished"
        self._newsletter_sends.update({newsletter_send_id : a_newsletter_send})
        

        return True
        
        
    def send_test_email(self, newsletter_send_id, users):
        """ send_test_email(newsletter_send_id, users) sends a test email to these users.
        """
        # send a test to the users given.
        ns = self._get_newsletter_send(newsletter_send_id)
        
        send_parts = [self._create_send_part(ns, user) for user in users]

        for sp in send_parts:
            self.send_send_part(sp)
            
        return True
        
        
    def add_users(self, newsletter_send_id, users):
        """ add_users(newsletter_send_id, users) adds the given users to the
            newsletterSend.
        
            users - the users to be sent emails.
            [{"email":"", "full_name":"", "user_id": ""}, ...]
        """
        # Create some NewsletterSendPart objects.
        ns = self._get_newsletter_send(newsletter_send_id)

        # Can only add users to a send which is open.  Not one that has already
        # been sent.
        if ns['status'] != 'open':
            raise ValueError("Tried to add users to a send which is not open to send.")

        # check that the same email is not already in there already.
        users_not_in = self._get_users_not_in(users, self._send_parts)

        for user in users_not_in:
            send_part = self._create_send_part(ns, user)
            self._send_parts.update({send_part['id']: send_part})
        
        return True

    def _get_users_not_in(self, users, send_parts):
        """ returns the users that are not already in the send_parts.  
                Based on email address only.
        """
        send_part_emails = set([s['email'] for s in send_parts.values()])
        return [u for u in users if u['email'] not in send_part_emails]

    def remove_user(self, newsletter_send_id, send_part_id):
        ns = self._get_newsletter_send(newsletter_send_id)
        
        if ns['status'] != 'open':
            raise ValueError("Tried to remove users from a send which is not open to send.")
        
        self._send_parts.pop(send_part_id)
        return True



    def newsletter_send_ids(self):
        return self._newsletter_sends.keys()



    def get_send_parts(self, newsletter_send_id):
        """
        """
        # we return them sorted, so that they can be repeated.
        return sorted([sp for sp in self._send_parts.values() if sp['newsletter_send_id'] == newsletter_send_id and sp['status'] == 'open'])


    def _get_newsletter_send(self, newsletter_send_id):
        return self._newsletter_sends.get(newsletter_send_id)

    def _create_send_part(self, newsletter_send, user):
        
        send_part = dict(
            id = self._make_uid(),
            newsletter_send_id = newsletter_send['id'],
            user_id = user['user_id'],
            full_name = user.get('full_name', ''),
            email = user['email'],
            body = newsletter_send['body'],
            subject = newsletter_send['subject'],
            status = "open")
        
        return send_part


    def _make_uid(self):
        return str(uuid.uuid4())











if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags = doctest.ELLIPSIS)
    
