from zope.interface import Interface, Attribute


class IMessage(Interface):
    namespace = Attribute('message namespace')

    def __str__():
        """ Render message as text
        """

    def __unicode__():
        """Render message as unicode
        """


class IMessageService(Interface):
    """ Utility for registering messages it should receive only IMessages
    """
    def send(message, request, namespace=u"message"):
        """ send message
        """

    def receive(request, namespace=u"message"):
        """ receive message, return a list of tuples (type, message)
        """
