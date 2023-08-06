add_entity_type('CodeKeyword')

add_relation_definition('Keyword', 'descendant_of', 'Keyword')
sync_schema_props_perms('Keyword')
checkpoint()
