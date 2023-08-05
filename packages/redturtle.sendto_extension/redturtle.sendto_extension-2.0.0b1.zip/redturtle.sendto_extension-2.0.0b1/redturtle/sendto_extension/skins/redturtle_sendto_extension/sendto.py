## Script (Python) "sendto"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Redirect to @@sendto
##

request = context.REQUEST
querystring = request.QUERY_STRING
new_url = context.absolute_url() + '/@@sendto'
if querystring:
    new_url += '?' + querystring
request.response.redirect(new_url, 301)
