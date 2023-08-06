add_entity_type('ProcessingStudy')
add_relation_definition('Run', 'in_study', 'ProcessingStudy')
add_relation_definition('RunChain', 'in_study', 'ProcessingStudy')

sync_schema_props_perms('ParameterDefinition')
for ptype in ('Int', 'Float', 'String', 'File'):
    sync_schema_props_perms('ParameterValue' + ptype)
sync_schema_props_perms('param_def')
