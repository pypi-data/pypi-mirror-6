import os

class LoadBitBucketPayload(object):

    """Helper class for load payloads"""

    def payload(self):
        with open('%s/payloads/bb_payload.txt' % os.path.dirname(__file__), 'r') as content_file:
            payload = content_file.read()
        return payload

    def payload_empty(self):
        with open('%s/payloads/bb_payload_empty.txt' % os.path.dirname(__file__), 'r') as content_file:
            payload = content_file.read()
        return payload

    def payload_added(self):
        with open('%s/payloads/bb_payload_added.txt' % os.path.dirname(__file__), 'r') as content_file:
            payload = content_file.read()
        return payload

    def payload_modified(self):
        with open('%s/payloads/bb_payload_modified.txt' % os.path.dirname(__file__), 'r') as content_file:
            payload = content_file.read()
        return payload

    def payload_removed1(self):
        with open('%s/payloads/bb_payload_removed1.txt' % os.path.dirname(__file__), 'r') as content_file:
            payload = content_file.read()
        return payload

    def payload_removed2(self):
        with open('%s/payloads/bb_payload_removed2.txt' % os.path.dirname(__file__), 'r') as content_file:
            payload = content_file.read()
        return payload
