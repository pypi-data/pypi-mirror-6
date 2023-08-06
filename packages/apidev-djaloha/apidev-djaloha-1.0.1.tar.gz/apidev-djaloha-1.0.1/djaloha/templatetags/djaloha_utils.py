# -*- coding: utf-8 -*-

from django import template
register = template.Library()
from django.db.models import get_model
from djaloha.forms import DjalohaForm

@register.filter
def convert_crlf(value):
   """
   Replace carriage return and line feed character by their javascript value
   Make possible to include title with those characters in the aloha links
   """
   return value.replace('\r', '\\r').replace('\n', '\\n')
   
@register.filter
def remove_br(value):
   """
   Remove the <br> tag by spaces except at the end
   Used for providing title without this tag 
   """
   return value.replace('<br>', ' ').strip()

class DjalohaEditNode(template.Node):
    
    def __init__(self, model_class, lookup, field_name, *args, **kwargs):
        super(DjalohaEditNode, self).__init__()
        self._model_class = model_class
        self._lookup_args = lookup
        self._lookup = {}
        self._field_name = field_name
        self.read_only = args[0] if args else kwargs.get('read_only', False)
        
    def _get_form_class(self):
        return DjalohaForm
    
    def _resolve_lookup(self, lookup, context):
        #resolve context. keep string values as is
        for (k, v) in self._lookup_args.items():
            v = unicode(v)
            new_v = v.strip('"').strip("'")
            if len(v)-2 == len(new_v):
                lookup[k] = new_v
            else:
                try:
                    try:
                        var_name, attr = new_v.strip('.')
                    except:
                        var_name, attr = new_v, None
                    var = template.Variable(var_name).resolve(context)
                    if attr:
                        var_value = getattr(var, attr, '')
                    else:
                        var_value = var
                    lookup[k] = var_value
                except template.VariableDoesNotExist:
                    lookup[k] = context[v]
                    
    def _render_value(self, context, obj_lookup, value):
        #if edit mode : activate aloha form
        if (not self.read_only) and context.get('djaloha_edit'):
            form_class = self._get_form_class()
            form = form_class(self._model_class, obj_lookup, self._field_name, field_value=value)
            return form.as_is()
        else:
            return value
        
    
    def render(self, context):
        self._resolve_lookup(self._lookup, context)
        
        #get or create the object to edit
        self._object, _is_new = self._model_class.objects.get_or_create(**self._lookup)
        value = getattr(self._object, self._field_name)
        
        return self._render_value(context, self._lookup, value)
        
class DjalohaMultipleEditNode(DjalohaEditNode):
    
    def _get_objects(self, lookup):
        return self._model_class.objects.none()
    
    def _get_object_lookup(self, obj):
        return {"id": obj.id}
    
    def _pre_object_render(self, obj):
        return ""
    
    def _post_object_render(self, obj):
        return ""
    
    def render(self, context):
        self._resolve_lookup(self._lookup, context)
        
        content = u""
        for obj in self._get_objects(self._lookup):
            value = getattr(obj, self._field_name)
            content += self._pre_object_render(obj)
            content += self._render_value(context, self._get_object_lookup(obj), value)
            content += self._post_object_render(obj)
        return content

            
def get_djaloha_edit_args(parser, token):
    full_model_name = token.split_contents()[1]
    lookups = token.split_contents()[2].split(';')
    field_name = token.split_contents()[3]

    app_name, model_name = full_model_name.split('.')
    model_class = get_model(app_name, model_name)

    lookup = {}
    for l in lookups:
        try:
            k, v = l.split('=')
        except ValueError:
            raise template.TemplateSyntaxError(
                u"djaloha_edit {0} is an invalid lookup. It should be key=value".format(l))
        lookup[k] = v
    
    if not lookup:
        raise template.TemplateSyntaxError(u"The djaloha_edit templatetag requires at least one lookup")
    return model_class, lookup, field_name

#@register.tag
#def djaloha_edit(parser, token):
#    model_class, lookup, field_name = get_djaloha_edit_args(parser, token)
#    return DjalohaEditNode(model_class, lookup, field_name)
