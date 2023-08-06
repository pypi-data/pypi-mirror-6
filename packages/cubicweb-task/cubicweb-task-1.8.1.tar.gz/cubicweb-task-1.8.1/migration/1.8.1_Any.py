for attr in ('cost', 'author'):
    # check first, another cube could have added it
    if attr not in fsschema['Task'].subjrels:
        drop_attribute('Task', attr)
