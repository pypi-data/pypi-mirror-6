for attr, atype in (('pid', 'Int'),
                    ('pyro_id', 'String'),
                    ('hostname', 'String'),
                    ('does_long_transaction', 'String')):
    if attr in fsschema and ('CWWorker', attr) in fsschema[attr].rdefs:
        drop_attribute('CWWorker', attr)

for attr, atype in (('committing', 'Boolean'),
                    ('aborted', 'Boolean'),
                    ('on_behalf', 'CWUser')):
    if attr in fsschema and ('CWWorkerTask', atype) in fsschema[attr].rdefs:
        drop_relation_definition('CWWorkerTask', attr, atype)
