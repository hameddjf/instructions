# from django import template
#
# register = template.Library()
#
#
# @register.inclusion_tag('registration/partials/link.html')
# def link(request, link_name, content):
#     return {
#         'request': request,
#         'link_name': link_name,
#         'link': "account:{}".format(link_name),
#         'content': content
#     }
