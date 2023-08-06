class Fetcher(object):
    
    def fetch(self):
        """
        Fetch from whatever data store. Returns the appropriate object
        rerpesentation of the fetched data. By convention, that data should be
        passable to a Sender.send for sending.
        """
        raise NotImplementedError("This fetcher has not yet implemented this method.")
    
    def close(self):
        """
        Override this method for the clean-up steps when this fetcher is
        disposed of.
        """
        pass

class Sender(object):
    
    def send(self, data):
        """
        Sends the data provided as argument to wherever route.
        """
        raise NotImplementedError("This sender has not yet implemented this method.")

    def close(self):
        """
        Override this method for the clean-up steps when this fetcher is
        disposed of.
        """
        pass
