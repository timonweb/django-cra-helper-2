from cra_helper import REACT_ASSETS


def static(request):
    if REACT_ASSETS:
        return {'react_assets': REACT_ASSETS}