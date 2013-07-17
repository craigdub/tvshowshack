from pyramid.i18n import TranslationStringFactory
import colander
from deform import Form
from pyramid.view import view_config
from colander import Schema, SchemaNode, String
from deform.widget import RichTextWidget, TextAreaWidget
from pyramid_deform import FormView
import deform
from pyramid.renderers import render_to_response
import os

_ = TranslationStringFactory('tvshowshack')

class Person(colander.MappingSchema):
	email = colander.SchemaNode(colander.String())
	password1 = colander.SchemaNode(
								colander.String(),
								validator=colander.Length(min=5, max=100),
								widget=deform.widget.PasswordWidget(size=20),
								description='Enter a password')
	password2 = colander.SchemaNode(
								colander.String(),
								validator=colander.Length(min=5, max=100),
								widget=deform.widget.PasswordWidget(size=20),
								description='Enter a password')
class Search(colander.MappingSchema):
	search = colander.SchemaNode(colander.String())
	category = colander.SchemaNode(colander.String())
	type = colander.SchemaNode(
        colander.String(),
        widget = deform.widget.SelectWidget(values='tv'),
    )

class MediaSearch(colander.MappingSchema):
	txt = deform.widget.TextInputWidget(css_class='input-small search-wid')
	auto = deform.widget.AutocompleteInputWidget(
			css_class='input-small search-wid',
            size=60,
            min_length=1)
	search = colander.SchemaNode(colander.String(),widget=auto)
	category = colander.SchemaNode(colander.String(),widget=txt)
	choices = (
            ('', '- Select -'),
            ('tv', 'TV Show'),
            ('movie', 'Movie')
            )
	type = colander.SchemaNode(
        colander.String(),
        widget = deform.widget.SelectWidget(values=choices),css_class='dropdown-small search-wid'
    )

class AllViews(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    age = colander.SchemaNode(colander.Int(),
                             validator=colander.Range(0, 200))
    def searchMedia(self,videos):
	    #search = Searches()
	    search = MediaSearch()
	    search.auto.values = videos
	    myform = deform.Form(search, buttons=('submit',))
	    return myform

@view_config(route_name='home', renderer='templates/search.jinja2')
def my_view(request):
	inst = AllViews(request)
	frmSignup = AllViews()
	curs = request.db['videos'].find()
	videos = []

	for vid in curs:
		videos.append(vid)
	
	return {"form":frmSignup.searchMedia(videos), "videos":videos}


@view_config(route_name='video', renderer='templates/video.jinja2')
def my_view(request):
	inst = AllViews(request)
	frmSignup = AllViews()
	#if 'email' in request.POST:
	#	controls = request.POST.items()
	#	import pdb;pdb.set_trace()
	#	request.db['users'].insert({"email":db.request.POST['email'], "password":db.request.POST['password1']}) 
	#	try:
	#		appstruct = frmSignup.validate(controls)
	#	except deform.ValidationFailure, e:
	#		return {'form':e, "cssInc":headerInc('css'), "jsInc":headerInc('js')}
	titles = set()
	curs = request.db['videos'].find()
	videos = []

	for vid in curs:
		videos.append(vid)
		if vid['title'] != []:
			titles.add(vid['title'][0])
	
	return {"form":frmSignup.searchMedia(list(titles)), "videos":videos, 'titles':titles}

