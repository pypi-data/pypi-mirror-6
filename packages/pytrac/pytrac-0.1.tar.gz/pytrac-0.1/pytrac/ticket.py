class Ticket(object):

    def __init__(self, server, notify=True):
        self.api = server.ticket
        self.notify = notify

    def search_raw(self, query):
        return self.api.query(query)

    def search(self, summary=None, owner=None, status=None, max=0):
        query = ''
        if summary:
            query += "summary~=%s&" % summary
        if owner:
            query += "owner=%s&" % owner
        if status:
            query += "status=%s&" % status
        if query == '':
            raise Exception("Query empty!")
        query += 'max=%s' % max
        return self.api.query(query)

    def _parse_ticket_info(self, ticket_data):
        '''make nice dict out of ticket info'''
        ticket_info = {
            'id': ticket_data[0],
            'created': ticket_data[1],  # this is xmlrpc.DateTime!
            'modified': ticket_data[2],
        }
        ticket_info.update(ticket_data[3])

        return ticket_info

    def info(self, ticket_id):
        '''return dictionary with info about specfic ticket'''
        ticket_data = self.api.get(ticket_id)
        return self._parse_ticket_info(ticket_data)

    def update(self, ticket_id, comment='', attrs=None, action='leave'):
        '''update the ticket with XXX'''
        ticket_info = self.info(ticket_id)

        attributes = {
            'action': action,
            '_ts': ticket_info['_ts'],
        }
        if attrs is not None:
            attributes.update(attrs)

        # catch exception (eg: set ticket to next although it is already at
        # next)
        result = self.api.update(
            ticket_info['id'],
            comment,
            attributes,
            self.notify,
        )
        return self._parse_ticket_info(result)

    def comment(self, ticket_id, comment):
        '''add comment to ticket'''
        return self.update(ticket_id, comment)

    def close(self, ticket_id, comment, resolution='fixed'):
        '''close ticket with resolution <RESOLUTION>'''
        self._check_resolution(ticket_id, resolution)
        return self.update(ticket_id, comment, {
            'status': 'closed',
            'action': 'resolve',
            'action_resolve_resolve_resolution': resolution})

    def _check_resolution(self, ticket_id, resolution):
        '''check if the resolution is valid'''
        # TODO: beautify me
        for action, label, hints, input_fields in self.api.getActions(ticket_id):
            if action == 'resolve':
                for fields in input_fields:
                    name, value, options = fields
                    if resolution in options:
                        return True
        raise Exception('invalid resolution: ' + resolution)
        return False

    def create(self):
        pass
