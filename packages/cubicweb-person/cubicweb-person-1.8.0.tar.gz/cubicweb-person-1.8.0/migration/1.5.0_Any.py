if 'PostalAddress' in schema:
    add_relation_definition('Person', 'postal_address', 'PostalAddress')
if 'IMAddress' in schema:
    add_relation_definition('Person', 'im_address', 'IMAddress')

