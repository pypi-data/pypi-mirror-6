from Products.CMFCore.utils import getToolByName

def v2(context):
    ptool = getToolByName(context, 'portal_properties')
    qu_props = ptool.get('quickupload_properties')
    if not qu_props.hasProperty('pdfbook_logo'):
        qu_props._setProperty('pdfbook_logo', False, 'boolean')
