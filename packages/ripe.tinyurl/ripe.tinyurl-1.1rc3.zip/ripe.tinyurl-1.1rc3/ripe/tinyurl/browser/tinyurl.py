from Products.Five import BrowserView
import base64
import hashlib
from Products.validation import validation
from Products.CMFCore.utils import getToolByName

msgs = {'id_exists': 'Item already exists, we increased the hash size',
        'invalid_url': 'Please enter a valid URL',
        'empty_url': 'Please enter a URL',
        'url_exists': 'The URL has already been applied to the site'}


def encode_url(url):
    # create a hash of the url inputted
    hashed = base64.urlsafe_b64encode(hashlib.md5(url).digest())
    return hashed


def encode_url_len(hashed, length):
    # cut the hash to a certain given input
    n = int(length)
    return hashed[0:n]


def id_exists(new_id, list_of_ids):
    # does the id already exist?
    if new_id in list_of_ids:
        return True
    return False


def publish_link(obj, wf):
    # publish all links automatically
    wf.setDefaultChain('simple_publication_workflow')
    try:
        wf.doActionFor(obj, 'publish')
        obj.reindexObject()
    except:
        # we have an unauthorised account here
        pass


def create_link(parent, url, req_hash_len, wf, cat):
    # add the link object to the given folder
    # if the id already exists in the folder
    # then return a new hashed version
    message = ''
    req_hash_len = int(req_hash_len)
    hashed_id = encode_url(url)
    new_id = encode_url_len(hashed_id, req_hash_len)
    child_ids = parent.objectIds()
    while id_exists(new_id, child_ids):
        already_entered = link_exists(cat, new_id, url)
        if already_entered:
            return already_entered
        req_hash_len = req_hash_len + 1
        new_id = encode_url_len(hashed_id, req_hash_len)
        message = msgs['id_exists']
    parent.invokeFactory('Link', id=new_id,
                         title=new_id,
                         remoteUrl=url)
    publish_link(parent[new_id], wf)
    return {'msg': message,
            'hashid': new_id}


def link_exists(cat, new_id, url):
    # check to see if the link already exists
    # if it doesn't then return the hash
    prev_link = cat(id=new_id)
    if prev_link:
        if prev_link[0].getObject().getRemoteUrl() == url:
            return {'hashid': new_id,
                    'msg': msgs['url_exists']}
    return None


def valid_url(url):
    # check to see if there is a valid url
    msg = ''
    if not url:
        return msgs['empty_url']
    va = validation.validatorFor('isURL')
    is_valid = va(url)
    if is_valid != 1:
        msg = msgs['invalid_url']
    return msg


def show_last_five(cat, creator):
    # display last 5 items
    my_links = cat(portal_type="Link",
                   Creator=creator,
                   sort_on='Date',
                   sort_order="reverse")
    return my_links[:30]


class TinyUrlView(BrowserView):

    def tiny_url_handler(self):
        # we want to return the inputted url if any
        # a hashid if the form has been posted
        # and any error messages
        tiny_url = {'url': 'http://',
                    'hashid': '',
                    'msg': '',
                    'links': []}

        cat = getToolByName(self.context, 'portal_catalog')
        pm = getToolByName(self.context, 'portal_membership')

        user = pm.getAuthenticatedMember().getUserName()

        tiny_url['links'] = show_last_five(cat, user)

        form = self.request.form
        if not form:
            # default screen
            return tiny_url

        if 'remoteUrl' in form.keys():
            tiny_url['url'] = form['remoteUrl']
            wf = getToolByName(self.context, 'portal_workflow')

            # validate the url
            tiny_url['msg'] = valid_url(form['remoteUrl'])
            if tiny_url['msg']:
                # we have a broken url
                return tiny_url

            link = create_link(self.context, tiny_url['url'],
                               form['hash_length'],
                               wf,
                               cat)
            tiny_url['hashid'] = link['hashid']
            tiny_url['msg'] = link['msg']

        return tiny_url
