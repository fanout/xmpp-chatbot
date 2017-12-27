# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from xml.etree import cElementTree as ET
from sleekxmpp.xmlstream import JID
from sleekxmpp.stanza import Message, Presence, Iq
from django.http import HttpResponse, HttpResponseNotAllowed

def stanza_from_string(s):
	if not isinstance(s, unicode):
		s = s.decode('utf-8')
	e = ET.fromstring(s)
	if e.tag == '{jabber:client}message':
		stanza = Message(xml=e)
	elif e.tag == '{jabber:client}presence':
		stanza = Presence(xml=e)
	elif e.tag == '{jabber:client}iq':
		stanza = Iq(xml=e)
	else:
		raise ValueError('string is not valid stanza')
	return stanza

def stanzas_to_response(stanza_list):
	body = ''
	for s in stanza_list:
		s_str = s.__str__()
		if not isinstance(s_str, unicode):
			s_str = s_str.decode('utf-8')
		body += s_str + '\n'
	return HttpResponse(body, content_type='text/plain')

def xmpp(request, to):
	if request.method == 'POST':
		try:
			s = stanza_from_string(request.body)
			sfrom = JID(s.get_from().full)
			sto = JID(s.get_to().full)
		except:
			return HttpResponse('invalid stanza\n', content_type='text/plain')

		if isinstance(s, Presence):
			stype = s._get_attr('type')
			if stype == 'subscribe' or stype == 'unsubscribe':
				out = []

				# ack request
				resp = Presence()
				resp.set_from(sto)
				resp.set_to(sfrom)
				resp.set_type(stype + 'd')
				out.append(resp)

				# send presence
				resp = Presence()
				sto.resource = 'chillpad'
				sto.regenerate()
				resp.set_from(sto)
				resp.set_to(sfrom)
				if stype == 'unsubscribe':
					resp.set_type('unavailable')
				out.append(resp)

				return stanzas_to_response(out)
			elif stype == 'probe':
				resp = Presence()
				sto.resource = 'chillpad'
				sto.regenerate()
				resp.set_from(sto)
				resp.set_to(sfrom)
				return stanzas_to_response([resp])
			else:
				# ignore
				return HttpResponse()
		elif isinstance(s, Message):
			is_chat = (s._get_attr('type') == 'chat')
			resp = Message()
			resp.set_from(sto)
			resp.set_to(sfrom)
			if is_chat:
				resp.set_type('chat')
			resp['body'] = 'You sent: %s' % s['body']
			return stanzas_to_response([resp])
		else:
			# be a jerk and ignore IQs
			return HttpResponse()
	else:
		return HttpResponseNotAllowed(['POST'])
