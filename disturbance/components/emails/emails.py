from wagov_utils.components.utils.email import (
    TemplateEmailBase as WAGovUtilsTemplateEmailBase,
)


class TemplateEmailBase(WAGovUtilsTemplateEmailBase):
    subject = ""
    html_template = "disturbance/emails/base_email.html"
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = "disturbance/emails/base_email.txt"

    def send_to_user(self, users, context=None):
        filtered_emails = {u.email for u in users if hasattr(u, "email")}
        # Loop through users
        for email in filtered_emails:
            # Send the email!
            self.send(email, context=context)
