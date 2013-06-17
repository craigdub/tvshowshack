from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('tvshowshack')

def my_view(request):
    return {'project':'tvshowshack'}
