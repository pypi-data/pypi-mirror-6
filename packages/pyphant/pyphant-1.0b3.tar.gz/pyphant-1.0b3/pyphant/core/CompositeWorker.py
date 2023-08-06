# -*- coding: utf-8 -*-

# Copyright (c) 2006-2007, Rectorate of the University of Freiburg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the Freiburg Materials Research Center,
#   University of Freiburg nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

u"""
The Composite worker acts as a container for graphs of workers.
At the moment these can only be entire recipes, but it is planned
that they can be subgraphs, too.
"""


import EventDispatcher, Worker, Connectors, Param
import copy
import pkg_resources


class CompositeWorkerChangedEvent(object):
    def __init__(self, worker, message, data=None):
        self.worker = worker
        self.message = message
        self.data = data

class WorkerAddedEvent(CompositeWorkerChangedEvent):
    def __init__(self, worker, data=None):
        CompositeWorkerChangedEvent.__init__(self, worker,
                                             "Worker Added", data)

class WorkerRemovedEvent(CompositeWorkerChangedEvent):
    def __init__(self, worker, data=None):
        CompositeWorkerChangedEvent.__init__(self, worker,
                                             "Worker Removed", data)

class ConnectionEvent(CompositeWorkerChangedEvent):
    def __init__(self, plug, socket, message, data=None):
        CompositeWorkerChangedEvent.__init__(self, socket.worker,
                                             message, data)
        self.plug = plug
        self.socket = socket
class ConnectionCreatedEvent(ConnectionEvent):
    def __init__(self, plug, socket, data=None):
        ConnectionEvent.__init__(self, plug, socket,
                                 "Connection created", data)
class ConnectionDestroyedEvent(ConnectionEvent):
    def __init__(self, plug, socket, data=None):
        ConnectionEvent.__init__(self, plug, socket,
                                 "Connection destroyed", data)
class ConnectorsExternalizationStateChangedEvent(CompositeWorkerChangedEvent):
    def __init__(self, worker, connector, data=None):
        CompositeWorkerChangedEvent.__init__(
            self, worker, "Connectors externalization state changed", data
            )
        self.connector = connector

class CompositeWorker(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = pkg_resources.get_distribution("pyphant").version
    name = "Composite"
    _params = [("noSockets", "Number of sockets", 0, None),
               ("noPlugs", "Number of plugs", 0, None)]

    def _id(self):
        if self.parent == None:
            return ""
        else:
            return super(CompositeWorker, self)._id()
    id = property(_id)

    def inithook(self):
        self._workers = []
        self._sources = []
        self._sinks = []
        self._eventDispatcher = EventDispatcher.EventDispatcher()
        for i in xrange(self.paramNoSockets.value):
            name = "socket%i" % i
            socketProxy = Connectors.ConnectorProxy(self, True, name)
            setattr(self, 'socket'+self.upperFirstLetter(name), socketProxy)
            self._sockets[name] = socketProxy
        for i in xrange(self.paramNoPlugs.value):
            name = "plug%i" % i
            plugProxy = Connectors.ConnectorProxy(self, False, name)
            setattr(self, 'plug'+self.upperFirstLetter(name), plugProxy)
            self._plugs[name] = plugProxy

    def addWorker(self, worker, data=None):
        if not self.checkWorkerName(worker, worker.getParam('name').value):
            raise ValueError(u'Duplicate worker name')
        worker.registerParamListener(self.vetoWorkerName,
                                     'name', Param.ParamChangeRequested)
        self._workers.append(worker)
        if len(worker.getPlugs()) == 0:
            self._sinks.append(worker)
        if len(worker.getSockets()) == 0:
            self._sources.append(worker)
        self._notifyListeners(WorkerAddedEvent(worker, data))

    def removeWorker(self, worker, data=None):
        self._workers.remove(worker)
        if worker in self._sources:
            self._sources.remove(worker)
        if worker in self._sinks:
            self._sinks.remove(worker)
        self._notifyListeners(WorkerRemovedEvent(worker, data))

    def getWorker(self, name):
        cands = [w for w in self._workers if w.getParam('name').value == name]
        if len(cands) > 1:
            raise RuntimeError(
                "Ambiguous worker name <%s> in CompositeWorker <%s>."
                % (name, self)
                )
        if len(cands) == 0:
            return None
        return cands[0]

    def getWorkers(self, desiredWorker=''):
        if desiredWorker == '':
            result = self._workers
        else:
            result = [w for w in self._workers
                      if w.__class__.__name__ == desiredWorker]
            if result == []:
                raise ValueError("Recipe does not contain Worker %s"
                                 % desiredWorker)
        return result

    def findConnectorForId(self, id):
        splittedId = id.split('.', 1)
        if len(splittedId) == 1:
            return super(CompositeWorker, self).findConnectorForId(
                splittedId[0]
                )
        else:
            w = self.getWorker(splittedId[0])
            return w.findConnectorForId(splittedId[1])

    def getAllPlugs(self):
        return sum([w.getPlugs() for w in self.getWorkers()], [])

    def getOpenSocketsForPlug(self, plug):
        walker = self.createCompositeWorkerWalker()
        return sum(walker.visit(lambda w:
                                [s for s in w.getSockets()
                                 if not s.isFull()],
                                [plug.worker]),
                   [])

    def getSources(self):
        return self._sources

    def getSinks(self):
        return self._sinks

    #pickle
    def __getstate__(self):
        pdict = copy.copy(self.__dict__)
        pdict['_eventDispatcher'] = EventDispatcher.EventDispatcher()
        return pdict

    def generateEvents(self, listenerDict):
        map(lambda worker: listenerDict[WorkerAddedEvent](
                WorkerAddedEvent(worker)
                ), self._workers)
        def connectionInformer(worker):
            for socket in worker.getSockets():
                if socket.isFull():
                    [ (issubclass(ConnectionCreatedEvent, x)
                       and l(ConnectionCreatedEvent(socket.getPlug(), socket)))
                      for (x, l) in listenerDict.items() ]
        connectionInformer(self)
        map(connectionInformer, self._workers)

    def createCompositeWorkerWalker(self):
        return CompositeWorkerWalker(self)

    def registerListener(self, listener,
                         eventType=CompositeWorkerChangedEvent):
        self._eventDispatcher.registerListener( listener, eventType)

    def unregisterListener(self, listener,
                           eventType=CompositeWorkerChangedEvent):
        self._eventDispatcher.unregisterListener( listener, eventType )

    def _notifyListeners(self, event):
        self._eventDispatcher.dispatchEvent(event)

    def connectionCreated(self, plug, socket):
        if self.parent:
            self.parent.connectionCreated(plug, socket)
        self._notifyListeners(ConnectionCreatedEvent(plug, socket))

    def connectionDestroyed(self, plug, socket):
        if self.parent:
            self.parent.connectionDestroyed(plug, socket)
        self._notifyListeners(ConnectionDestroyedEvent(plug, socket))

    def workersConnectorStateChanged(self, worker, connector):
        self._notifyListeners(
            ConnectorsExternalizationStateChangedEvent(worker, connector)
            )

    def vetoWorkerName(self, paramChangeEvent):
        if not self.checkWorkerName(paramChangeEvent.param.worker,
                                    paramChangeEvent.newValue):
            raise Param.VetoParamChange(paramChangeEvent)

    def checkWorkerName(self, worker, name):
        ws = [w for w in self._workers
              if w.getParam('name').value == name]
        if ws == [] or ws[0] == worker:
            return True
        else:
            return False

class CompositeWorkerWalker(object):
    def __init__(self, compositeWorker):
        self._compositeWorker = compositeWorker

    def visit(self, visitor, start):
        visited = []
        toVisit = start
        while toVisit:
            worker = toVisit.pop(0)
            yield visitor(worker)
            visited.append(worker)
            for socket in worker.getSockets():
                plug = socket.getPlug()
                if plug:
                    worker = plug.worker
                    if worker not in visited:
                        toVisit.append(worker)


