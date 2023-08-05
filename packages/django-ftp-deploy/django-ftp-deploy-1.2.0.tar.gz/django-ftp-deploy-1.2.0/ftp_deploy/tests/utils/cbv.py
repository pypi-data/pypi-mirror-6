def setup_view(view, request, *args, **kwargs):
    """Test Class Base Views"""
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view