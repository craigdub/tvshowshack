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
"""
	class PageSchema(Schema):
		title = SchemaNode(String())
		description = SchemaNode(
		String(),
		widget=TextAreaWidget(cols=40, rows=5),
		missing=u"",
		)
		body = SchemaNode(
			String(),
			widget=RichTextWidget(),
			missing=u"",
		)
"""

"""
	@view_config(route_name='home', renderer='form.pt')
	class PageEditView(FormView):
		schema = PageSchema()
		buttons = ('save',)
		form_options = (('formid', 'pyramid-deform'),('method', 'GET'))
		@view_config(request_param='form.save')
		def save_success(self, appstruct):
			context = self.request.context
			context.title = appstruct['title']
			context.description = appstruct['description']
			context.body = appstruct['body']
			self.request.session.flash(u"Your changes have been saved.")
			return HTTPFound(location=self.request.path_url)
		def appstruct(self):
			return {'title': context.title,'description': context.description,'body': context.body}
"""
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

class ProjectorViews(object):
	def __init__(self, request):
		self.request = request
	def site_view(self):
		schema = Person()
		myform = deform.Form(schema, buttons=('submit',))
		print os.getcwd()
		return myform

def headerInc(dir, p=os.getcwd()+'/tvshowshack/static'):
	pth = os.path.join(p,dir)
	return os.listdir(pth)

@view_config(route_name='signup', renderer='templates/mytemplate.jinja2')
def my_view(request):
	inst = ProjectorViews(request)
	frmSignup = inst.site_view()
	if 'email' in request.POST:
		controls = request.POST.items()
		import pdb;pdb.set_trace()
		request.db['users'].insert({"email":db.request.POST['email'], "password":db.request.POST['password1']}) 
		try:
			appstruct = frmSignup.validate(controls)
		except deform.ValidationFailure, e:
			return {'form':e, "cssInc":headerInc('css'), "jsInc":headerInc('js')}
	return {"form":frmSignup,"cssInc":headerInc('css'), "jsInc":headerInc('js')}

