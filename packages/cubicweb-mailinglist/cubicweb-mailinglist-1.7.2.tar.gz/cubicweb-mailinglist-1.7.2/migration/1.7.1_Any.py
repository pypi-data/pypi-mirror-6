add_attribute('MailingList', 'email_address')

# need to disable integrity check, else operations will be triggered
# once ML use_email EmailAddress relation has been droppeed, triggering
# type resolver error
with session.allow_all_hooks_but('integrity'):
    for ml in rql('MailingList X').entities():
        email = ml.use_email[0]
        ml.set_attributes(email_address=email.address)
        email.cw_delete()
drop_relation_definition('MailingList', 'use_email', 'EmailAddress')
