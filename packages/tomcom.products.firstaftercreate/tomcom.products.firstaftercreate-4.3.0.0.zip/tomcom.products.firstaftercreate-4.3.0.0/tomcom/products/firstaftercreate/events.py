def order(event):
    """ """
    context=event.object
    parent=context.aq_parent
    portal=context.getAdapter('portal')()
    tcconfig=portal.getBrowser('tcconfig')

    config=tcconfig.get('_firstaftercreate')

    if context.portal_type in config.get('portal_type',[]):
        parent.moveObjectToPosition(context.getId(),0)