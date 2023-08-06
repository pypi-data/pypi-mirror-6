class Signals:
    __signals__ = []
    def get_connections(self):
        self._assert_connections()
        return self._signals_connections
        
    def emit(self, signal, *args):
        self._assert_connections()
        if signal in self.__signals__:
            if signal not in self._signals_silenced:
                if signal in self._signals_connections:
                    returns = []
                    for func, user_data in self._signals_connections[signal]:
                        # signal args
                        data = list(args)
                        # insert me
                        data.insert(0, self)
                        # add user args
                        data.extend(list(user_data))
                        # call it
                        returns.append(func(*tuple(data)))
                    return returns
        else:
            raise TypeError('Signal is not a valid signal prototype.')
    
    def connect(self, signal, func, *user_data):
        self._assert_connections()
        if signal in self.__signals__:
            if hasattr(func, "__call__"):
                if signal in self._signals_connections:
                    self._signals_connections[signal].append((func,user_data))
                    return len(self._signals_connections[signal])-1
                else:
                    self._signals_connections[signal] = [(func,user_data)]
                    return 0
            else:
                raise TypeError('Callback must be a callable object.')
        else:
            raise TypeError('Signal is not a valid signal prototype.')
        
    def disconnect(self, signal, index):
        self._assert_connections()
        if signal in self._signals_connections and index in self._signals_connections[signal]:
            self._signals_connections[signal].remove(index)
    
    def disconnect_all(self, match_class):
        self._assert_connections()
        for signal, callbacks in self._signals_connections.iteritems():
            for index, cb in enumerate(callbacks):
                if hasattr(cb[0], 'im_class') and cb[0].im_class == match_class:
                    del self._signals_connections[signal][index]

    def has_connection(self, signal):
        return len(self.get_connections().get(signal, [])) > 0

    def _assert_connections(self):
        if not hasattr(self, "_signals_connections"):
            self._signals_connections = {}
            self._signals_silenced = set()

    def silence(self, *signals):
        """Method to silence these signals from triggering
        """
        self._assert_connections()
        [self._signals_silenced.add(signal) for signal in signals]

    def listen(self, *signals):
        """Method to begin listening to silenced signals
        """
        self._assert_connections()
        [self._signals_silenced.remove(signal) for signal in signals]
