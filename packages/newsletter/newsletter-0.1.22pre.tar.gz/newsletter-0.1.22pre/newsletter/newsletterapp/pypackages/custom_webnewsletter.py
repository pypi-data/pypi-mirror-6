# custom newsletter app

import newsletter.newsletterapp.newsletterapp


class MyWebNewsletter(newsletter.newsletterapp.newsletterapp.WebNewsletter):


    # Here we show a subscribe function that just has an email, no full_name.
    def subscribe(self, email, wrap_it = True):
        """ subscribe(email, wrap_it = True)
        """
        if newsletter.newsletterapp.newsletterapp.validate_email(email):
            tags = ""
            info = {"full_name": '',
                    "tags": tags}
            if self._n.subscribe(email, info):
                return self.html_template("subscribe", wrap_it)
        else:
            return self.html_template("subscribe_email_invalid", wrap_it)

    subscribe.exposed = True
