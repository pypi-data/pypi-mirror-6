from archetypes.referencebrowserwidget.browser import view


class QueryCatalogView(view.QueryCatalogView):

    def __call__(self, *args, **kwargs):
        self.request.set_lazy('language_constraint', 'all')
        return super(QueryCatalogView, self).__call__(*args, **kwargs)


class ReferenceBrowserPopup(view.ReferenceBrowserPopup):

    def update(self):
        self.request.set_lazy('language_constraint', 'all')
        super(ReferenceBrowserPopup, self).update()
