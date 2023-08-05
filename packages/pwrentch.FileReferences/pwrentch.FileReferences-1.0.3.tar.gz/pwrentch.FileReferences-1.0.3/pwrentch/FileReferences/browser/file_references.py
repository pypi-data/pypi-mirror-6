from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

class ReferenceListView(BrowserView):

    template = ViewPageTemplateFile('reference_list.pt')

    def __call__(self):
        """"""
        # Determine which portal_types to include
        self.portalTypes = [ 'File', 'Image', ]
        if self.request.get("submit", None):
            for type in [ 'File', 'Image', ]:
                if not self.request.get("portal-type-" + type, None):
                    self.portalTypes.remove(type)
        if self.portalTypes == []:
            # If nothing was selected, then use everything
            self.portalTypes = [ 'File', 'Image', ]

        # Get all of the content items of the selected portalTypes
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        current_path = '/'.join(self.context.getPhysicalPath())
        brains = portal_catalog(
            path={'query': current_path},
            portal_type=self.portalTypes,
            show_inactive=True
            )
        files = { }
        for brain in brains:
            obj = brain.getObject()
            extension = self.determineContentType(obj).upper()
            #extension = obj.absolute_url().split(".")[-1].upper()
            #if extension == obj.absolute_url().upper():
            #    extension = "unknown"
            if not files.has_key(extension):
                files[extension] = [ ]
            files[extension].append(obj)

        # Make the dictionary of files available to the template
        self.files = files

        # Make the lists of file types available to the template
        self.allFileTypes = sorted(files.keys())
        self.fileTypes = sorted(files.keys())
        if self.request.get("submit", None):
            for type in self.allFileTypes:
                if not self.request.get("doc-type-" + type, None):
                    self.fileTypes.remove(type)
        return self.template()



    def getReferences(self, object):
        """"""
        reference_catalog = getToolByName(self.context, 'reference_catalog')
        references = reference_catalog.getBackReferences(object)
        return [ ref.getSourceObject() for ref in references ]



    def determineContentType(self, obj):
        """"""
        # Parse the url for a file extension
        extension = obj.absolute_url().split(".")[-1]
        if not extension or extension == obj.absolute_url() or len(extension) > 4:
            # File extension didn't work, try mime type
            extension = obj.getContentType().split("/")[-1]

            # Make educated guesses on mime types
            crossref = {
                'octet-stream': 'unknown',
                'jpeg': 'jpg',
                'vnd.ms-excel': 'xls',
                'vnd.ms-powerpoint': 'ppt',
                'vnd.ms-openxmlformats-opendocument.spreadsheetml.sheet': 'xlsx',
                'vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
                'vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            }
            extension = crossref.get(extension, extension)
        return extension