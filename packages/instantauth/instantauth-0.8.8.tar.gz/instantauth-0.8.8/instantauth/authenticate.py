
from .exceptions import *

class Authentication(object):
    def __init__(self, streamcoder, cryptor, verifier, datacoder, session_handler, secret_key):
        self.streamcoder = streamcoder
        self.cryptor = cryptor
        self.verifier = verifier
        self.datacoder = datacoder
        self.session_handler = session_handler
        self.secret_key = secret_key

    def _merge_context(self, context):
        for k, v in self.cryptor.derived_context.items():
            setattr(context, k, v)
        for k, v in self.verifier.derived_context.items():
            setattr(context, k, v)
        for k, v in self.datacoder.derived_context.items():
            setattr(context, k, v)

    def get_first_context(self, data, type=None, **params):
        """
        :param data: Stream data decodable by streamcoder
        :param type: Authentication type
        :return: Authentication context
        :rtype: :class:`instantauth.authenticate.Context`

        Decode process:

        | #0 Sender-Encoded Raw Stream |
                       |
                  streamcoder
                       V
        | #1 Sender-Encrypted Raw Data |
                       |
                    cryptor
                       V
        | #2 Receiver-Decrypted Raw Data | --verifier--> | Public Key |
                       |                                       |
                    verifier                                   V
                       V                                       |
          | #3 Sender-Encrypted Data | ---------->-------------+
                                                               |
                                                            cryptor
                                                               V
          | #5 Receiver-Decoded Data | <--coder-- | #4 Sender-Encoded Data |

        """
        #0: raw stream
        decoded_stream = self.streamcoder.decode(data) # 1:
        decrypted = self.cryptor.decrypt_stream(decoded_stream, self.secret_key) #2
        destructed = self.verifier.destruct_first_data(decrypted, self.secret_key) #3
        raw_data = self.cryptor.decrypt_first_data(destructed.data, self.secret_key) #4
        semantic_data = self.datacoder.decode(raw_data) #5
        context = Context(None, semantic_data)
        context.session = self.session_handler.session_from_session_key(destructed.public_key, type, **params)
        self._merge_context(context)
        return context

    def get_context(self, data):
        """
        :param data: Stream data decodable by streamcoder
        :return: Authentication context
        :rtype: :class:`instantauth.authenticate.Context`

        Decode process:

        | #0 Sender-Encoded Raw Stream |
                       |
                  streamcoder
                       V
        | #1 Sender-Encrypted Raw Data |
                       |
                    cryptor
                       V
        | #2 Receiver-Decrypted Raw Data | --verifier--> | Public Key | --session_handler--> | Session |
                       |                                       |                                  |
                    verifier                                   V                            session_handler
                       V                                       |                                  V
          | #3 Sender-Encrypted Data | ---------->-------------+--------------<------------ | Private Key |
                                                               |
                                                            cryptor
                                                               V
          | #5 Receiver-Decoded Data | <--coder-- | #4 Sender-Encoded Data |
        """
        #0: raw stream
        decoded_stream = self.streamcoder.decode(data) #1
        decrypted = self.cryptor.decrypt_stream(decoded_stream, self.secret_key) #2
        destructed = self.verifier.destruct_data(decrypted, self.secret_key) #3
        if not destructed.public_key:
            raise AuthenticationError
        try:
            session = self.session_handler.session_from_public_key(destructed.public_key)
        except KeyError:
            raise AuthenticationError('No public key found', key=destructed.public_key)
        if not session:
            raise AuthenticationError('No session found')

        private_key = self.session_handler.get_private_key(session)
        raw_data = self.cryptor.decrypt_data(destructed.data, private_key, self.secret_key) #4
        semantic_data = self.datacoder.decode(raw_data) #5
        if not self.verifier.verify(destructed, private_key, self.secret_key):
            raise AuthenticationError('Session verification failed')
        context = Context(session, semantic_data)
        self._merge_context(context)
        return context

    def build_first_data(self, data, session_key):
        """

        :param data:
        :param session_key:
        :rtype: :class:`bytes`

        Encode process:

        | #1 Original Data | --coder--> | #2 Encoded Data | --cryptor--> | #3 Encrypted Data |
                                                                                   |
                                                                                verifier
                                                                                   V
                           | #5 Encrypted Packed Data | <--cryptor-- | #4 Verification-Packed Data |
        """
        #1 data
        coded_data = self.datacoder.encode(data) #2
        encrypted_data = self.cryptor.encrypt_first_data(coded_data, self.secret_key) #3
        merged_data = self.verifier.construct_first_data(encrypted_data, session_key, self.secret_key) #4
        encrypted = self.cryptor.encrypt_stream(merged_data, self.secret_key) #5
        encoded_stream = self.streamcoder.encode(encrypted)
        return encoded_stream

    def build_data(self, data, session):
        """

        :param data: Structured data encodable by datacoder
        :param session: Authentication session
        :rtype: :class:`bytes`

        Encode process:

        | #1 Original Data | --coder--> | #2 Encoded Data | --cryptor--> | #3 Encrypted Data |
                                                                                   |
                                                                                verifier
                                                                                   V
                           | #5 Encrypted Packed Data | <--cryptor-- | #4 Verification-Packed Data |

        """
        #1: data
        private_key = self.session_handler.get_private_key(session)
        public_key = self.session_handler.get_public_key(session)
        coded_data = self.datacoder.encode(data) #2
        assert(coded_data is not None)
        encrypted_data = self.cryptor.encrypt_data(coded_data, private_key, self.secret_key) #3
        assert(encrypted_data is not None)
        merged_data = self.verifier.construct_data(encrypted_data, private_key, public_key, self.secret_key) #4
        encrypted = self.cryptor.encrypt_stream(merged_data, self.secret_key) #5
        encoded_stream = self.streamcoder.encode(encrypted)
        return encoded_stream


class Context(object):
    def __init__(self, session, data):
        self.session = session
        self.data = data

    def __repr__(self):
        return u'<Context({},{})>'.format(self.session, self.data)
