# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@uberdev.org>
# date: 2012/06/06
# copy: (C) Copyright 2012-EOT metagriffin -- see LICENSE.txt
#------------------------------------------------------------------------------
# This software is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#------------------------------------------------------------------------------

import unittest, sys, os, re, time, logging
import sqlalchemy as sa, pxml

import pysyncml
from .common import adict, ts, ts_iso, getAddressSize, getMaxMemorySize
from . import codec, test_helpers
from .test_helpers import makestats as stat, setlogging
from .items.note import NoteItem

setlogging(False)

#------------------------------------------------------------------------------
class ItemStorage:
  def __init__(self, nextID=1):
    self.nextID  = nextID
    self.entries = dict()
  def getAll(self):
    return self.entries.values()
  def add(self, item):
    item.id = self.nextID
    self.nextID += 1
    self.entries[item.id] = item
    return item
  def get(self, itemID):
    return self.entries[int(itemID)]
  def replace(self, item, reportChanges):
    self.entries[int(item.id)] = item
    return None
  def delete(self, itemID):
    del self.entries[int(itemID)]

#------------------------------------------------------------------------------
class Agent(pysyncml.BaseNoteAgent):
  def __init__(self, storage=None, *args, **kw):
    super(Agent, self).__init__(*args, **kw)
    self.storage = storage or ItemStorage()
  def getAllItems(self):                      return self.storage.getAll()
  def addItem(self, item):                    return self.storage.add(item)
  def getItem(self, itemID):                  return self.storage.get(itemID)
  def replaceItem(self, item, reportChanges): return self.storage.replace(item, reportChanges)
  def deleteItem(self, itemID):               return self.storage.delete(itemID)

#----------------------------------------------------------------------------
def findxml(xml, xpath):
  xtree = codec.Codec.autoDecode('application/vnd.syncml+xml', xml)
  return xtree.findtext(xpath)

#------------------------------------------------------------------------------
class TestServer(unittest.TestCase, pxml.XmlTestMixin, test_helpers.TrimDictEqual):

  maxDiff = None

  #----------------------------------------------------------------------------
  def assertIntsNear(self, val, chk, offset=1):
    if chk == val or ( chk - offset == val ) or ( chk + offset == val ):
      return
    self.assertEqual(val, chk)

  #----------------------------------------------------------------------------
  def setUp(self):
    self.initDatabases()
    self.initServer()

  #----------------------------------------------------------------------------
  def initDatabases(self):
    self.items   = ItemStorage(nextID=1000)
    self.db      = sa.create_engine('sqlite://')
    # if os.path.exists('../test.db'):
    #   os.unlink('../test.db')
    # self.db = sa.create_engine('sqlite:///../test.db')
    pysyncml.enableSqliteCascadingDeletes(self.db)

  #----------------------------------------------------------------------------
  def initServer(self):
    self.context = pysyncml.Context(engine=self.db, owner=None, autoCommit=True)
    self.store   = self.context.Store(uri='srv_note', displayName='Server Note Store',
                                      agent=Agent(storage=self.items))
    self.server  = self.context.Adapter(name='In-Memory Test Server')
    if self.server.devinfo is None:
      self.server.devinfo = self.context.DeviceInfo(
        devID             = __name__ + '.server',
        devType           = pysyncml.DEVTYPE_SERVER,
        manufacturerName  = 'pysyncml',
        modelName         = __name__ + '.server',
        )
    self.store = self.server.addStore(self.store)

  #----------------------------------------------------------------------------
  def makeRequestInit(self, targetID, sourceID,
                      storeName='MemoTaker', sessionID='1',
                      putDevInfo=True, getDevInfo=True,
                      sendAlert=True, alertCode=201, nextAnchor=None, lastAnchor=None,
                      ):
    modelName = __name__ + '.client'
    ret = '''<?xml version="1.0" encoding="utf-8"?>
<SyncML>
 <SyncHdr>
  <VerDTD>1.2</VerDTD>
  <VerProto>SyncML/1.2</VerProto>
  <SessionID>%(sessionID)s</SessionID>
  <MsgID>1</MsgID>
  <Source>
   <LocURI>%(sourceID)s</LocURI>
   <LocName>test</LocName>
  </Source>
  <Target><LocURI>%(targetID)s</LocURI></Target>
  <Cred>
   <Meta>
    <Format xmlns="syncml:metinf">b64</Format>
    <Type xmlns="syncml:metinf">syncml:auth-basic</Type>
   </Meta>
   <Data>Z3Vlc3Q6Z3Vlc3Q=</Data>
  </Cred>
  <Meta>
   <MaxMsgSize xmlns="syncml:metinf">150000</MaxMsgSize>
   <MaxObjSize xmlns="syncml:metinf">4000000</MaxObjSize>
  </Meta>
 </SyncHdr>
 <SyncBody>
''' % locals()

    if putDevInfo:
      ret += '''
  <Put>
   <CmdID>1</CmdID>
   <Meta><Type xmlns="syncml:metinf">application/vnd.syncml-devinf+xml</Type></Meta>
   <Item>
    <Source><LocURI>./devinf12</LocURI></Source>
    <Data>
     <DevInf xmlns="syncml:devinf">
      <VerDTD>1.2</VerDTD>
      <Man>pysyncml</Man>
      <Mod>%(modelName)s</Mod>
      <OEM>-</OEM>
      <FwV>-</FwV>
      <SwV>-</SwV>
      <HwV>-</HwV>
      <DevID>%(sourceID)s</DevID>
      <DevTyp>workstation</DevTyp>
      <UTC/>
      <SupportNumberOfChanges/>
      <SupportLargeObjs/>
      <DataStore>
       <SourceRef>./cli_memo</SourceRef>
       <DisplayName>%(storeName)s</DisplayName>
       <MaxGUIDSize>64</MaxGUIDSize>
       <Rx-Pref>
        <CTType>text/plain</CTType>
        <VerCT>1.1</VerCT>
       </Rx-Pref>
       <Rx>
        <CTType>text/plain</CTType>
        <VerCT>1.0</VerCT>
       </Rx>
       <Tx-Pref>
        <CTType>text/plain</CTType>
        <VerCT>1.1</VerCT>
       </Tx-Pref>
       <Tx>
        <CTType>text/plain</CTType>
        <VerCT>1.0</VerCT>
       </Tx>
       <SyncCap>
        <SyncType>1</SyncType>
        <SyncType>2</SyncType>
        <SyncType>3</SyncType>
        <SyncType>4</SyncType>
        <SyncType>5</SyncType>
        <SyncType>6</SyncType>
        <SyncType>7</SyncType>
       </SyncCap>
      </DataStore>
     </DevInf>
    </Data>
   </Item>
  </Put>
''' % locals()

    if getDevInfo:
      ret += '''
  <Get>
   <CmdID>2</CmdID>
   <Meta><Type xmlns="syncml:metinf">application/vnd.syncml-devinf+xml</Type></Meta>
   <Item>
    <Target><LocURI>./devinf12</LocURI></Target>
   </Item>
  </Get>
''' % locals()

    nextAnchor = '' if nextAnchor is None else '<Next>%s</Next>' % (nextAnchor,)
    lastAnchor = '' if lastAnchor is None else '<Last>%s</Last>' % (lastAnchor,)

    if sendAlert:
      ret += '''
  <Alert>
   <CmdID>3</CmdID>
   <Data>%(alertCode)d</Data>
   <Item>
    <Source><LocURI>./cli_memo</LocURI></Source>
    <Target><LocURI>srv_note</LocURI></Target>
    <Meta>
     <Anchor xmlns="syncml:metinf">
      %(lastAnchor)s
      %(nextAnchor)s
     </Anchor>
     <MaxObjSize xmlns="syncml:metinf">4000000</MaxObjSize>
    </Meta>
   </Item>
  </Alert>
''' % locals()

    ret += '''
  <Final/>
 </SyncBody>
</SyncML>''' % locals()

    return ret

  #----------------------------------------------------------------------------
  def makeRequestAlert(self, targetID, sourceID, sessionID='1',
                       peerNextAnchor=None, peerLastAnchor=None,
                       resultsStatus=True,
                       ):
    ret = '''<?xml version="1.0" encoding="utf-8"?>
<SyncML>
 <SyncHdr>
  <VerDTD>1.2</VerDTD>
  <VerProto>SyncML/1.2</VerProto>
  <SessionID>%(sessionID)s</SessionID>
  <MsgID>2</MsgID>
  <Source>
   <LocURI>%(sourceID)s</LocURI>
   <LocName>test</LocName>
  </Source>
  <Target><LocURI>%(targetID)s</LocURI></Target>
  <Meta>
   <MaxMsgSize xmlns="syncml:metinf">150000</MaxMsgSize>
   <MaxObjSize xmlns="syncml:metinf">4000000</MaxObjSize>
  </Meta>
 </SyncHdr>
 <SyncBody>
  <Status>
    <CmdID>1</CmdID>
    <MsgRef>1</MsgRef>
    <CmdRef>0</CmdRef>
    <Cmd>SyncHdr</Cmd>
    <SourceRef>%(targetID)s</SourceRef>
    <TargetRef>%(sourceID)s</TargetRef>
    <Data>200</Data>
  </Status>
''' % locals()

    alertStatusCmdRef = '3'

    if resultsStatus:
      alertStatusCmdRef = '6'
      ret += '''
  <Status>
    <CmdID>2</CmdID>
    <MsgRef>1</MsgRef>
    <CmdRef>4</CmdRef>
    <Cmd>Results</Cmd>
    <SourceRef>./devinf12</SourceRef>
    <Data>200</Data>
  </Status>
  ''' % locals()

    peerNextAnchor = '' if peerNextAnchor is None else '<Next>%s</Next>' % (peerNextAnchor,)
    peerLastAnchor = '' if peerLastAnchor is None else '<Last>%s</Last>' % (peerLastAnchor,)

    ret += '''
  <Status>
    <CmdID>3</CmdID>
    <MsgRef>1</MsgRef>
    <CmdRef>%(alertStatusCmdRef)s</CmdRef>
    <Cmd>Alert</Cmd>
    <SourceRef>srv_note</SourceRef>
    <TargetRef>./cli_memo</TargetRef>
    <Data>200</Data>
    <Item>
      <Data>
        <Anchor xmlns="syncml:metinf">
          %(peerLastAnchor)s
          %(peerNextAnchor)s
        </Anchor>
      </Data>
    </Item>
  </Status>
  <Sync>
    <CmdID>4</CmdID>
    <Source><LocURI>./cli_memo</LocURI></Source>
    <Target><LocURI>srv_note</LocURI></Target>
  </Sync>
  <Final/>
 </SyncBody>
</SyncML>''' % locals()

    return ret

  #----------------------------------------------------------------------------
  def makeRequestMap(self, targetID, sourceID, sessionID='1', isAdd=True):
    ret = '''<?xml version="1.0" encoding="utf-8"?>
<SyncML>
 <SyncHdr>
  <VerDTD>1.2</VerDTD>
  <VerProto>SyncML/1.2</VerProto>
  <SessionID>%(sessionID)s</SessionID>
  <MsgID>3</MsgID>
  <Source>
   <LocURI>%(sourceID)s</LocURI>
   <LocName>test</LocName>
  </Source>
  <Target><LocURI>%(targetID)s</LocURI></Target>
  <Meta>
   <MaxMsgSize xmlns="syncml:metinf">150000</MaxMsgSize>
   <MaxObjSize xmlns="syncml:metinf">4000000</MaxObjSize>
  </Meta>
 </SyncHdr>
 <SyncBody>
  <Status>
    <CmdID>1</CmdID>
    <MsgRef>2</MsgRef>
    <CmdRef>0</CmdRef>
    <Cmd>SyncHdr</Cmd>
    <SourceRef>%(targetID)s</SourceRef>
    <TargetRef>%(sourceID)s</TargetRef>
    <Data>200</Data>
  </Status>
  <Status>
    <CmdID>2</CmdID>
    <MsgRef>2</MsgRef>
    <CmdRef>3</CmdRef>
    <Cmd>Sync</Cmd>
    <SourceRef>srv_note</SourceRef>
    <TargetRef>cli_memo</TargetRef>
    <Data>200</Data>
  </Status>
''' % locals()

    if isAdd:
      ret += '''
  <Status>
    <CmdID>3</CmdID>
    <MsgRef>2</MsgRef>
    <CmdRef>4</CmdRef>
    <Cmd>Add</Cmd>
    <SourceRef>1000</SourceRef>
    <Data>201</Data>
  </Status>
  <Map>
    <CmdID>4</CmdID>
    <Source><LocURI>cli_memo</LocURI></Source>
    <Target><LocURI>srv_note</LocURI></Target>
    <MapItem>
      <Source><LocURI>1</LocURI></Source>
      <Target><LocURI>1000</LocURI></Target>
    </MapItem>
  </Map>
''' % locals()
    else:
      ret += '''
  <Status>
    <CmdID>3</CmdID>
    <MsgRef>2</MsgRef>
    <CmdRef>4</CmdRef>
    <Cmd>Replace</Cmd>
    <TargetRef>1</TargetRef>
    <Data>200</Data>
  </Status>
''' % locals()

    ret += '''
  <Final/>
 </SyncBody>
</SyncML>''' % locals()

    return ret

  #----------------------------------------------------------------------------
  def test_auth_none(self):
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body='<?xml version="1.0" encoding="utf-8"?>'
                    '<SyncML>'
                    '<SyncHdr>'
                    '<VerDTD>1.2</VerDTD>'
                    '<VerProto>SyncML/1.2</VerProto>'
                    '<SessionID>1</SessionID>'
                    '<MsgID>1</MsgID>'
                    '<Source>'
                    '<LocURI>test.server.devID</LocURI>'
                    '<LocName>test</LocName>'
                    '</Source>'
                    '<Target><LocURI>' + self.server.devID + '</LocURI></Target>'
                    '<Meta>'
                    '<MaxMsgSize xmlns="syncml:metinf">150000</MaxMsgSize>'
                    '<MaxObjSize xmlns="syncml:metinf">4000000</MaxObjSize>'
                    '</Meta>'
                    '</SyncHdr>'
                    '<SyncBody><Final/></SyncBody>'
                    '</SyncML>')
    self.assertEqual(pysyncml.Context.getAuthInfo(request, None), None)
    self.assertEqual(pysyncml.Context.getTargetID(request), self.server.devID)

  #----------------------------------------------------------------------------
  def test_auth_basic(self):
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body='<?xml version="1.0" encoding="utf-8"?>'
                    '<SyncML>'
                    '<SyncHdr>'
                    '<VerDTD>1.2</VerDTD>'
                    '<VerProto>SyncML/1.2</VerProto>'
                    '<SessionID>1</SessionID>'
                    '<MsgID>1</MsgID>'
                    '<Source>'
                    '<LocURI>test.server.devID</LocURI>'
                    '<LocName>test</LocName>'
                    '</Source>'
                    '<Target><LocURI>' + self.server.devID + '</LocURI></Target>'
                    '<Cred>'
                    '<Meta>'
                    '<Format xmlns="syncml:metinf">b64</Format>'
                    '<Type xmlns="syncml:metinf">syncml:auth-basic</Type>'
                    '</Meta>'
                    '<Data>Z3Vlc3Q6Z3Vlc3Q=</Data>'
                    '</Cred>'
                    '<Meta>'
                    '<MaxMsgSize xmlns="syncml:metinf">150000</MaxMsgSize>'
                    '<MaxObjSize xmlns="syncml:metinf">4000000</MaxObjSize>'
                    '</Meta>'
                    '</SyncHdr>'
                    '<SyncBody><Final/></SyncBody>'
                    '</SyncML>')
    self.assertEqual(
      pysyncml.Context.getAuthInfo(request, None),
      adict(auth=pysyncml.NAMESPACE_AUTH_BASIC,
            username='guest', password='guest'))
    self.assertEqual(pysyncml.Context.getTargetID(request), self.server.devID)

  #----------------------------------------------------------------------------
  def test_auth_with_namespace(self):
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body='<?xml version="1.0" encoding="utf-8"?>'
                    '<SyncML xmlns="SYNCML:SYNCML1.2">'
                    ' <SyncHdr>'
                    '  <VerDTD>1.2</VerDTD>'
                    '  <VerProto>SyncML/1.2</VerProto>'
                    '  <SessionID>1</SessionID>'
                    '  <MsgID>1</MsgID>'
                    '  <Source>'
                    '   <LocURI>test.server.devID</LocURI>'
                    '   <LocName>test</LocName>'
                    '  </Source>'
                    '  <Target><LocURI>' + self.server.devID + '</LocURI></Target>'
                    '  <Cred>'
                    '   <Meta>'
                    '    <Format xmlns="syncml:metinf">b64</Format>'
                    '    <Type xmlns="syncml:metinf">syncml:auth-basic</Type>'
                    '   </Meta>'
                    '   <Data>Z3Vlc3Q6Z3Vlc3Q=</Data>'
                    '  </Cred>'
                    '  <Meta>'
                    '   <MaxMsgSize xmlns="syncml:metinf">150000</MaxMsgSize>'
                    '   <MaxObjSize xmlns="syncml:metinf">4000000</MaxObjSize>'
                    '  </Meta>'
                    ' </SyncHdr>'
                    ' <SyncBody><Final/></SyncBody>'
                    '</SyncML>')
    self.assertEqual(
      pysyncml.Context.getAuthInfo(request, None),
      adict(auth=pysyncml.NAMESPACE_AUTH_BASIC,
            username='guest', password='guest'))
    self.assertEqual(pysyncml.Context.getTargetID(request), self.server.devID)

  #----------------------------------------------------------------------------
  def test_devinfo_dbsaveload(self):
    db = sa.create_engine('sqlite://')
    ctxt1 = pysyncml.Context(engine=db, owner=None, autoCommit=True)
    server1 = ctxt1.Adapter(devinfo=ctxt1.DeviceInfo(
      devID             = __name__ + '.server',
      devType           = pysyncml.DEVTYPE_SERVER,
      manufacturerName  = 'pysyncml',
      modelName         = __name__ + '.server',
      ))
    ctxt1.save()
    server2 = pysyncml.Context(engine=db, owner=None, autoCommit=True).Adapter()
    self.assertEqual(server1.devID, server2.devID)
    self.assertEqual(
      str(server1.devinfo),
      '<Device "%s.server": devType=server; manufacturerName=pysyncml; modelName=%s.server; oem=-; hardwareVersion=-; firmwareVersion=-; softwareVersion=-; utc=True; largeObjects=True; hierarchicalSync=True; numberOfChanges=True>' % (__name__, __name__))
    self.assertEqual(str(server1.devinfo), str(server2.devinfo))

  #----------------------------------------------------------------------------
  def test_store_saved_to_db(self):
    db = sa.create_engine('sqlite://')
    ctxt1 = pysyncml.Context(engine=db, owner=None, autoCommit=True)
    server1 = ctxt1.Adapter(devinfo=ctxt1.DeviceInfo(
      devID             = __name__ + '.server',
      devType           = pysyncml.DEVTYPE_SERVER,
      manufacturerName  = 'pysyncml',
      modelName         = __name__ + '.server',
      ))
    self.assertEqual(server1.stores.keys(), [])
    server1.addStore(ctxt1.Store(uri='srv_note', displayName='Server Note Store',
                                 agent=Agent(storage=self.items)))
    ctxt1._model.session.flush()
    self.assertEqual(server1.stores.keys(), ['srv_note'])
    self.assertEqual(
      str(server1.stores['srv_note']),
      '<Store "Server Note Store": uri=srv_note; maxGuidSize=%d; maxObjSize=%d; syncTypes=1,2,3,4,5,6,7; contentTypes=text/x-s4j-sifn@1.1:PrefTxRx,text/x-s4j-sifn@1.0:TxRx,text/plain@1.1,1.0:TxRx>'
      % (getAddressSize(), getMaxMemorySize()))
    ctxt1.save()
    server2 = pysyncml.Context(engine=db, owner=None, autoCommit=True).Adapter()
    self.assertEqual(server2.stores.keys(), ['srv_note'])
    self.assertEqual(str(server1.stores), str(server2.stores))

  #----------------------------------------------------------------------------
  def test_new_peer_nodevinfo(self):
    newPeerID = 'test.client.%d.devID' % (time.time(),)
    returnUrl = 'https://www.example.com/foo;s=a139bb50047b45ca9820fe53f5161e55'
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body='<?xml version="1.0" encoding="utf-8"?>'
                    '<SyncML>'
                    ' <SyncHdr>'
                    '  <VerDTD>1.2</VerDTD>'
                    '  <VerProto>SyncML/1.2</VerProto>'
                    '  <SessionID>1</SessionID>'
                    '  <MsgID>1</MsgID>'
                    '  <Source>'
                    '   <LocURI>' + newPeerID + '</LocURI>'
                    '   <LocName>test</LocName>'
                    '  </Source>'
                    '  <Target><LocURI>' + self.server.devID + '</LocURI></Target>'
                    '  <Cred>'
                    '   <Meta>'
                    '    <Format xmlns="syncml:metinf">b64</Format>'
                    '    <Type xmlns="syncml:metinf">syncml:auth-basic</Type>'
                    '   </Meta>'
                    '   <Data>Z3Vlc3Q6Z3Vlc3Q=</Data>'
                    '  </Cred>'
                    '  <Meta>'
                    '   <MaxMsgSize xmlns="syncml:metinf">150000</MaxMsgSize>'
                    '   <MaxObjSize xmlns="syncml:metinf">4000000</MaxObjSize>'
                    '  </Meta>'
                    ' </SyncHdr>'
                    ' <SyncBody><Final/></SyncBody>'
                    '</SyncML>')
    session  = pysyncml.Session()
    session.returnUrl = returnUrl
    response = pysyncml.Response()
    auth     = pysyncml.Context.getAuthInfo(request, None)
    stats = self.server.handleRequest(session, request, response)
    self.assertEqual(stats, dict())
    chk = adict(headers=dict((('content-type', 'application/vnd.syncml+xml; charset=UTF-8'),)),
                body=
                '<SyncML>'
                ' <SyncHdr>'
                '  <VerDTD>1.2</VerDTD>'
                '  <VerProto>SyncML/1.2</VerProto>'
                '  <SessionID>1</SessionID>'
                '  <MsgID>1</MsgID>'
                '  <Source>'
                '   <LocURI>' + __name__ + '.server</LocURI>'
                '   <LocName>In-Memory Test Server</LocName>'
                '  </Source>'
                '  <Target>'
                '   <LocURI>' + newPeerID + '</LocURI>'
                '   <LocName>test</LocName>'
                '  </Target>'
                '  <RespURI>' + returnUrl + '</RespURI>'
                '  <Meta>'
                '   <MaxMsgSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxMsgSize>'
                '   <MaxObjSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '  </Meta>'
                ' </SyncHdr>'
                ' <SyncBody>'
                '  <Status>'
                '   <CmdID>1</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>0</CmdRef>'
                '   <Cmd>SyncHdr</Cmd>'
                '   <SourceRef>' + newPeerID + '</SourceRef>'
                '   <TargetRef>' + __name__ + '.server</TargetRef>'
                '   <Data>212</Data>'
                '  </Status>'
                '  <Put>'
                '   <CmdID>2</CmdID>'
                '   <Meta><Type xmlns="syncml:metinf">application/vnd.syncml-devinf+xml</Type></Meta>'
                '   <Item>'
                '    <Source><LocURI>./devinf12</LocURI><LocName>./devinf12</LocName></Source>'
                '    <Data>'
                '     <DevInf xmlns="syncml:devinf">'
                '      <VerDTD>1.2</VerDTD>'
                '      <Man>pysyncml</Man>'
                '      <Mod>' + __name__ + '.server</Mod>'
                '      <OEM>-</OEM>'
                '      <FwV>-</FwV>'
                '      <SwV>-</SwV>'
                '      <HwV>-</HwV>'
                '      <DevID>' + __name__ + '.server</DevID>'
                '      <DevTyp>server</DevTyp>'
                '      <UTC/>'
                '      <SupportLargeObjs/>'
                '      <SupportHierarchicalSync/>'
                '      <SupportNumberOfChanges/>'
                '      <DataStore>'
                '       <SourceRef>srv_note</SourceRef>'
                '       <DisplayName>Server Note Store</DisplayName>'
                '       <MaxGUIDSize>' + str(getAddressSize()) + '</MaxGUIDSize>'
                '       <MaxObjSize>' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '       <Rx-Pref><CTType>text/x-s4j-sifn</CTType><VerCT>1.1</VerCT></Rx-Pref>'
                '       <Rx><CTType>text/x-s4j-sifn</CTType><VerCT>1.0</VerCT></Rx>'
                '       <Rx><CTType>text/plain</CTType><VerCT>1.1</VerCT></Rx>'
                '       <Rx><CTType>text/plain</CTType><VerCT>1.0</VerCT></Rx>'
                '       <Tx-Pref><CTType>text/x-s4j-sifn</CTType><VerCT>1.1</VerCT></Tx-Pref>'
                '       <Tx><CTType>text/x-s4j-sifn</CTType><VerCT>1.0</VerCT></Tx>'
                '       <Tx><CTType>text/plain</CTType><VerCT>1.1</VerCT></Tx>'
                '       <Tx><CTType>text/plain</CTType><VerCT>1.0</VerCT></Tx>'
                '       <SyncCap>'
                '        <SyncType>1</SyncType>'
                '        <SyncType>2</SyncType>'
                '        <SyncType>3</SyncType>'
                '        <SyncType>4</SyncType>'
                '        <SyncType>5</SyncType>'
                '        <SyncType>6</SyncType>'
                '        <SyncType>7</SyncType>'
                '       </SyncCap>'
                '      </DataStore>'
                '     </DevInf>'
                '    </Data>'
                '   </Item>'
                '  </Put>'
                '  <Get>'
                '   <CmdID>3</CmdID>'
                '   <Meta><Type xmlns="syncml:metinf">application/vnd.syncml-devinf+xml</Type></Meta>'
                '   <Item>'
                '    <Target><LocURI>./devinf12</LocURI><LocName>./devinf12</LocName></Target>'
                '   </Item>'
                '  </Get>'
                '  <Final/>'
                ' </SyncBody>'
                '</SyncML>')
    self.assertEqual(response.contentType, chk.headers['content-type'])
    self.assertXmlEqual(response.body, chk.body)

  #----------------------------------------------------------------------------
  def test_effective_id(self):
    newPeerID = 'test.client.%d.devID' % (time.time(),)
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit('http://example.com/sync', newPeerID, nextAnchor=ts_iso(),
                                              putDevInfo=False, getDevInfo=False, sendAlert=False,))
    session  = pysyncml.Session()
    returnUrl = 'https://example.com/sync;sessionid=a139bb50047b45ca9820fe53f5161e55'
    session.effectiveID = 'http://example.com/sync'
    session.returnUrl = returnUrl
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertEqual(stats, dict())
    chk = adict(headers=dict((('content-type', 'application/vnd.syncml+xml; charset=UTF-8'),)),
                body=
                '<SyncML>'
                ' <SyncHdr>'
                '  <VerDTD>1.2</VerDTD>'
                '  <VerProto>SyncML/1.2</VerProto>'
                '  <SessionID>1</SessionID>'
                '  <MsgID>1</MsgID>'
                '  <Source>'
                '   <LocURI>http://example.com/sync</LocURI>'
                '   <LocName>In-Memory Test Server</LocName>'
                '  </Source>'
                '  <Target>'
                '   <LocURI>' + newPeerID + '</LocURI>'
                '   <LocName>test</LocName>'
                '  </Target>'
                '  <RespURI>' + returnUrl + '</RespURI>'
                '  <Meta>'
                '   <MaxMsgSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxMsgSize>'
                '   <MaxObjSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '  </Meta>'
                ' </SyncHdr>'
                ' <SyncBody>'
                '  <Status>'
                '   <CmdID>1</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>0</CmdRef>'
                '   <Cmd>SyncHdr</Cmd>'
                '   <SourceRef>' + newPeerID + '</SourceRef>'
                '   <TargetRef>http://example.com/sync</TargetRef>'
                '   <Data>212</Data>'
                '  </Status>'
                '  <Put>'
                '   <CmdID>2</CmdID>'
                '   <Meta><Type xmlns="syncml:metinf">application/vnd.syncml-devinf+xml</Type></Meta>'
                '   <Item>'
                '    <Source><LocURI>./devinf12</LocURI><LocName>./devinf12</LocName></Source>'
                '    <Data>'
                '     <DevInf xmlns="syncml:devinf">'
                '      <VerDTD>1.2</VerDTD>'
                '      <Man>pysyncml</Man>'
                '      <Mod>' + __name__ + '.server</Mod>'
                '      <OEM>-</OEM>'
                '      <FwV>-</FwV>'
                '      <SwV>-</SwV>'
                '      <HwV>-</HwV>'
                '      <DevID>' + __name__ + '.server</DevID>'
                '      <DevTyp>server</DevTyp>'
                '      <UTC/>'
                '      <SupportLargeObjs/>'
                '      <SupportHierarchicalSync/>'
                '      <SupportNumberOfChanges/>'
                '      <DataStore>'
                '       <SourceRef>srv_note</SourceRef>'
                '       <DisplayName>Server Note Store</DisplayName>'
                '       <MaxGUIDSize>' + str(getAddressSize()) + '</MaxGUIDSize>'
                '       <MaxObjSize>' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '       <Rx-Pref><CTType>text/x-s4j-sifn</CTType><VerCT>1.1</VerCT></Rx-Pref>'
                '       <Rx><CTType>text/x-s4j-sifn</CTType><VerCT>1.0</VerCT></Rx>'
                '       <Rx><CTType>text/plain</CTType><VerCT>1.1</VerCT></Rx>'
                '       <Rx><CTType>text/plain</CTType><VerCT>1.0</VerCT></Rx>'
                '       <Tx-Pref><CTType>text/x-s4j-sifn</CTType><VerCT>1.1</VerCT></Tx-Pref>'
                '       <Tx><CTType>text/x-s4j-sifn</CTType><VerCT>1.0</VerCT></Tx>'
                '       <Tx><CTType>text/plain</CTType><VerCT>1.1</VerCT></Tx>'
                '       <Tx><CTType>text/plain</CTType><VerCT>1.0</VerCT></Tx>'
                '       <SyncCap>'
                '        <SyncType>1</SyncType>'
                '        <SyncType>2</SyncType>'
                '        <SyncType>3</SyncType>'
                '        <SyncType>4</SyncType>'
                '        <SyncType>5</SyncType>'
                '        <SyncType>6</SyncType>'
                '        <SyncType>7</SyncType>'
                '       </SyncCap>'
                '      </DataStore>'
                '     </DevInf>'
                '    </Data>'
                '   </Item>'
                '  </Put>'
                '  <Get>'
                '   <CmdID>3</CmdID>'
                '   <Meta><Type xmlns="syncml:metinf">application/vnd.syncml-devinf+xml</Type></Meta>'
                '   <Item>'
                '    <Target><LocURI>./devinf12</LocURI><LocName>./devinf12</LocName></Target>'
                '   </Item>'
                '  </Get>'
                '  <Final/>'
                ' </SyncBody>'
                '</SyncML>')
    self.assertEqual(response.contentType, chk.headers['content-type'])
    self.assertXmlEqual(response.body, chk.body)

  #----------------------------------------------------------------------------
  def test_new_peer_store(self):
    newPeerID = 'test.client.%d.devID' % (time.time(),)
    peerAnchor = ts_iso()
    returnUrl = 'https://www.example.com/foo;s=a139bb50047b45ca9820fe53f5161e55'
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID, nextAnchor=peerAnchor))
    session  = pysyncml.Session()
    session.returnUrl = returnUrl
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    anchor = findxml(response.body, './SyncBody/Alert/Item/Meta/Anchor/Next')
    self.assertTrue(anchor is not None)
    self.assertIntsNear(int(anchor), ts())
    chk = adict(headers=dict((('content-type', 'application/vnd.syncml+xml; charset=UTF-8'),)),
                body=
                '<SyncML>'
                ' <SyncHdr>'
                '  <VerDTD>1.2</VerDTD>'
                '  <VerProto>SyncML/1.2</VerProto>'
                '  <SessionID>1</SessionID>'
                '  <MsgID>1</MsgID>'
                '  <Source>'
                '   <LocURI>' + __name__ + '.server</LocURI>'
                '   <LocName>In-Memory Test Server</LocName>'
                '  </Source>'
                '  <Target>'
                '   <LocURI>' + newPeerID + '</LocURI>'
                '   <LocName>test</LocName>'
                '  </Target>'
                '  <RespURI>' + returnUrl + '</RespURI>'
                '  <Meta>'
                '   <MaxMsgSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxMsgSize>'
                '   <MaxObjSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '  </Meta>'
                ' </SyncHdr>'
                ' <SyncBody>'
                '  <Status>'
                '   <CmdID>1</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>0</CmdRef>'
                '   <Cmd>SyncHdr</Cmd>'
                '   <SourceRef>' + newPeerID + '</SourceRef>'
                '   <TargetRef>' + __name__ + '.server</TargetRef>'
                '   <Data>212</Data>'
                '  </Status>'
                '  <Status>'
                '   <CmdID>2</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>1</CmdRef>'
                '   <Cmd>Put</Cmd>'
                '   <SourceRef>./devinf12</SourceRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Status>'
                '   <CmdID>3</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>2</CmdRef>'
                '   <Cmd>Get</Cmd>'
                '   <TargetRef>./devinf12</TargetRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Results>'
                '   <CmdID>4</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>2</CmdRef>'
                '   <Meta><Type xmlns="syncml:metinf">application/vnd.syncml-devinf+xml</Type></Meta>'
                '   <Item>'
                '    <Source><LocURI>./devinf12</LocURI><LocName>./devinf12</LocName></Source>'
                '    <Data>'
                '     <DevInf xmlns="syncml:devinf">'
                '      <VerDTD>1.2</VerDTD>'
                '      <Man>pysyncml</Man>'
                '      <Mod>' + __name__ + '.server</Mod>'
                '      <OEM>-</OEM>'
                '      <FwV>-</FwV>'
                '      <SwV>-</SwV>'
                '      <HwV>-</HwV>'
                '      <DevID>' + __name__ + '.server</DevID>'
                '      <DevTyp>server</DevTyp>'
                '      <UTC/>'
                '      <SupportLargeObjs/>'
                '      <SupportHierarchicalSync/>'
                '      <SupportNumberOfChanges/>'
                '      <DataStore>'
                '       <SourceRef>srv_note</SourceRef>'
                '       <DisplayName>Server Note Store</DisplayName>'
                '       <MaxGUIDSize>' + str(getAddressSize()) + '</MaxGUIDSize>'
                '       <MaxObjSize>' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '       <Rx-Pref><CTType>text/x-s4j-sifn</CTType><VerCT>1.1</VerCT></Rx-Pref>'
                '       <Rx><CTType>text/x-s4j-sifn</CTType><VerCT>1.0</VerCT></Rx>'
                '       <Rx><CTType>text/plain</CTType><VerCT>1.1</VerCT></Rx>'
                '       <Rx><CTType>text/plain</CTType><VerCT>1.0</VerCT></Rx>'
                '       <Tx-Pref><CTType>text/x-s4j-sifn</CTType><VerCT>1.1</VerCT></Tx-Pref>'
                '       <Tx><CTType>text/x-s4j-sifn</CTType><VerCT>1.0</VerCT></Tx>'
                '       <Tx><CTType>text/plain</CTType><VerCT>1.1</VerCT></Tx>'
                '       <Tx><CTType>text/plain</CTType><VerCT>1.0</VerCT></Tx>'
                '       <SyncCap>'
                '        <SyncType>1</SyncType>'
                '        <SyncType>2</SyncType>'
                '        <SyncType>3</SyncType>'
                '        <SyncType>4</SyncType>'
                '        <SyncType>5</SyncType>'
                '        <SyncType>6</SyncType>'
                '        <SyncType>7</SyncType>'
                '       </SyncCap>'
                '      </DataStore>'
                '     </DevInf>'
                '    </Data>'
                '   </Item>'
                '  </Results>'
                '  <Status>'
                '   <CmdID>5</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>3</CmdRef>'
                '   <Cmd>Alert</Cmd>'
                '   <SourceRef>./cli_memo</SourceRef>'
                '   <TargetRef>srv_note</TargetRef>'
                '   <Data>200</Data>'
                '   <Item>'
                '    <Data>'
                '     <Anchor xmlns="syncml:metinf"><Next>' + peerAnchor + '</Next></Anchor>'
                '    </Data>'
                '   </Item>'
                '  </Status>'
                '  <Alert>'
                '    <CmdID>6</CmdID>'
                '    <Data>201</Data>'
                '    <Item>'
                '      <Source><LocURI>srv_note</LocURI></Source>'
                '      <Target><LocURI>cli_memo</LocURI></Target>'
                '      <Meta>'
                '        <Anchor xmlns="syncml:metinf">'
                '          <Next>' + anchor + '</Next>'
                '        </Anchor>'
                '        <MaxObjSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '      </Meta>'
                '    </Item>'
                '  </Alert>'
                '  <Final/>'
                ' </SyncBody>'
                '</SyncML>')
    self.assertEqual(response.contentType, chk.headers['content-type'])
    self.assertXmlEqual(response.body, chk.body)
    # TODO: confirm that the session object looks good...
    server2 = pysyncml.Context(engine=self.db, owner=None, autoCommit=True).Adapter()
    peers = server2.getKnownPeers()
    self.assertEqual(len(peers), 1)
    peer = peers[0]
    self.assertEqual(peer.name, 'test')
    self.assertEqual(peer.devID, newPeerID)
    self.assertEqual(peer.maxMsgSize, 150000)
    self.assertEqual(peer.maxObjSize, 4000000)
    self.assertTrue(peer.devinfo is not None)
    self.assertEqual(peer.devinfo.devID, newPeerID)
    self.assertEqual(peer.devinfo.manufacturerName, 'pysyncml')
    self.assertEqual(peer.devinfo.modelName, __name__ + '.client')
    self.assertEqual(peer.devinfo.oem, '-')
    self.assertEqual(peer.devinfo.firmwareVersion, '-')
    self.assertEqual(peer.devinfo.softwareVersion, '-')
    self.assertEqual(peer.devinfo.hardwareVersion, '-')
    self.assertEqual(peer.devinfo.devType, 'workstation')
    self.assertEqual(peer.devinfo.utc, True)
    self.assertEqual(peer.devinfo.largeObjects, True)
    self.assertEqual(peer.devinfo.hierarchicalSync, False)
    self.assertEqual(peer.devinfo.numberOfChanges, True)

  #----------------------------------------------------------------------------
  def test_sync_push_empty(self):
    # step 1: register a new peer
    newPeerID = 'test.client.%d.devID' % (time.time(),)
    peerAnchor = ts_iso()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID, nextAnchor=peerAnchor))
    session  = pysyncml.Session()
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    # step 2: don't register any changes...
    # step 3: initialize syncml transaction with a new session
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID,
                                              nextAnchor=peerAnchor, sessionID='2'))
    session  = pysyncml.Session()
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    # step 4: synchronize - send empty and expect empty
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestAlert(self.server.devID, newPeerID,
                                               peerNextAnchor=peerAnchor, sessionID='2'))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    chk = adict(headers=dict((('content-type', 'application/vnd.syncml+xml; charset=UTF-8'),)),
                body=
                '<SyncML>'
                ' <SyncHdr>'
                '  <VerDTD>1.2</VerDTD>'
                '  <VerProto>SyncML/1.2</VerProto>'
                '  <SessionID>2</SessionID>'
                '  <MsgID>2</MsgID>'
                '  <Source>'
                '   <LocURI>' + __name__ + '.server</LocURI>'
                '   <LocName>In-Memory Test Server</LocName>'
                '  </Source>'
                '  <Target>'
                '   <LocURI>' + newPeerID + '</LocURI>'
                '   <LocName>test</LocName>'
                '  </Target>'
                ' </SyncHdr>'
                ' <SyncBody>'
                '  <Status>'
                '   <CmdID>1</CmdID>'
                '   <MsgRef>2</MsgRef>'
                '   <CmdRef>0</CmdRef>'
                '   <Cmd>SyncHdr</Cmd>'
                '   <SourceRef>' + newPeerID + '</SourceRef>'
                '   <TargetRef>' + __name__ + '.server</TargetRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Status>'
                '   <CmdID>2</CmdID>'
                '   <MsgRef>2</MsgRef>'
                '   <CmdRef>4</CmdRef>'
                '   <Cmd>Sync</Cmd>'
                '   <SourceRef>./cli_memo</SourceRef>'
                '   <TargetRef>srv_note</TargetRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Sync>'
                '    <CmdID>3</CmdID>'
                '    <Source><LocURI>srv_note</LocURI></Source>'
                '    <Target><LocURI>cli_memo</LocURI></Target>'
                '    <NumberOfChanges>0</NumberOfChanges>'
                '  </Sync>'
                '  <Final/>'
                ' </SyncBody>'
                '</SyncML>')
    self.assertEqual(response.contentType, chk.headers['content-type'])
    self.assertXmlEqual(response.body, chk.body)

  #----------------------------------------------------------------------------
  def test_sync_push_one(self):
    # step 1: register a new peer
    newPeerID = 'test.client.%d.devID' % (time.time(),)
    peerAnchor = ts_iso()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID, nextAnchor=peerAnchor))
    session  = pysyncml.Session()
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    # step 2: register some changes
    self.initServer()
    item = self.items.add(NoteItem(name='foo', body='this is the foo'))
    self.store.registerChange(item.id, pysyncml.ITEM_ADDED)
    self.context.save()
    # step 3: initialize syncml transaction with a new session
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID,
                                              nextAnchor=peerAnchor, sessionID='2'))
    session  = pysyncml.Session()
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    # step 4: synchronize - send nothing and expect changes down
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestAlert(self.server.devID, newPeerID,
                                               peerNextAnchor=peerAnchor, sessionID='2'))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    chk = adict(headers=dict((('content-type', 'application/vnd.syncml+xml; charset=UTF-8'),)),
                body=
                '<SyncML>'
                ' <SyncHdr>'
                '  <VerDTD>1.2</VerDTD>'
                '  <VerProto>SyncML/1.2</VerProto>'
                '  <SessionID>2</SessionID>'
                '  <MsgID>2</MsgID>'
                '  <Source>'
                '   <LocURI>' + __name__ + '.server</LocURI>'
                '   <LocName>In-Memory Test Server</LocName>'
                '  </Source>'
                '  <Target>'
                '   <LocURI>' + newPeerID + '</LocURI>'
                '   <LocName>test</LocName>'
                '  </Target>'
                ' </SyncHdr>'
                ' <SyncBody>'
                '  <Status>'
                '   <CmdID>1</CmdID>'
                '   <MsgRef>2</MsgRef>'
                '   <CmdRef>0</CmdRef>'
                '   <Cmd>SyncHdr</Cmd>'
                '   <SourceRef>' + newPeerID + '</SourceRef>'
                '   <TargetRef>' + __name__ + '.server</TargetRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Status>'
                '   <CmdID>2</CmdID>'
                '   <MsgRef>2</MsgRef>'
                '   <CmdRef>4</CmdRef>'
                '   <Cmd>Sync</Cmd>'
                '   <SourceRef>./cli_memo</SourceRef>'
                '   <TargetRef>srv_note</TargetRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Sync>'
                '    <CmdID>3</CmdID>'
                '    <Source><LocURI>srv_note</LocURI></Source>'
                '    <Target><LocURI>cli_memo</LocURI></Target>'
                '    <NumberOfChanges>1</NumberOfChanges>'
                '    <Add>'
                '      <CmdID>4</CmdID>'
                '      <Meta><Type xmlns="syncml:metinf">text/plain</Type></Meta>'
                '      <Item>'
                '        <Source><LocURI>1000</LocURI></Source>'
                '        <Data>this is the foo</Data>'
                '      </Item>'
                '    </Add>'
                '  </Sync>'
                '  <Final/>'
                ' </SyncBody>'
                '</SyncML>')
    self.assertEqual(response.contentType, chk.headers['content-type'])
    self.assertXmlEqual(response.body, chk.body)

  #----------------------------------------------------------------------------
  def test_sync_map(self):
    # step 1: register a new peer
    newPeerID = 'test.client.%d.devID' % (time.time(),)
    peerAnchor = ts_iso()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID, nextAnchor=peerAnchor))
    session  = pysyncml.Session()
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    # step 2: register some changes
    self.initServer()
    item = self.items.add(NoteItem(name='foo', body='this is the foo'))
    self.store.registerChange(item.id, pysyncml.ITEM_ADDED)
    self.context.save()
    # step 3: initialize syncml transaction with a new session
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID,
                                              nextAnchor=peerAnchor, sessionID='2'))
    session  = pysyncml.Session()
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    # step 4: synchronize - send nothing and expect changes down
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestAlert(self.server.devID, newPeerID,
                                               peerNextAnchor=peerAnchor, sessionID='2'))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    # step 5: send mapping request, expect a confirm and nothing further
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestMap(self.server.devID, newPeerID, sessionID='2'))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC, peerAdd=1)))
    chk = adict(headers=dict((('content-type', 'application/vnd.syncml+xml; charset=UTF-8'),)),
                body=
                '<SyncML>'
                ' <SyncHdr>'
                '  <VerDTD>1.2</VerDTD>'
                '  <VerProto>SyncML/1.2</VerProto>'
                '  <SessionID>2</SessionID>'
                '  <MsgID>3</MsgID>'
                '  <Source>'
                '   <LocURI>' + __name__ + '.server</LocURI>'
                '   <LocName>In-Memory Test Server</LocName>'
                '  </Source>'
                '  <Target>'
                '   <LocURI>' + newPeerID + '</LocURI>'
                '   <LocName>test</LocName>'
                '  </Target>'
                ' </SyncHdr>'
                ' <SyncBody>'
                '  <Status>'
                '   <CmdID>1</CmdID>'
                '   <MsgRef>3</MsgRef>'
                '   <CmdRef>0</CmdRef>'
                '   <Cmd>SyncHdr</Cmd>'
                '   <SourceRef>' + newPeerID + '</SourceRef>'
                '   <TargetRef>' + __name__ + '.server</TargetRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Status>'
                '   <CmdID>2</CmdID>'
                '   <MsgRef>3</MsgRef>'
                '   <CmdRef>4</CmdRef>'
                '   <Cmd>Map</Cmd>'
                '   <SourceRef>cli_memo</SourceRef>'
                '   <TargetRef>srv_note</TargetRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Final/>'
                ' </SyncBody>'
                '</SyncML>')
    self.assertEqual(response.contentType, chk.headers['content-type'])
    self.assertXmlEqual(response.body, chk.body)

  #----------------------------------------------------------------------------
  def test_two_peers(self):
    # step 1: register a new peer
    newPeerID0 = 'NEW-PEER-0'
    peerAnchor = ts_iso()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID0,
                                              nextAnchor=peerAnchor, storeName='MT2'))
    session  = pysyncml.Session()
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    self.initServer()
    # step 2: register another new peer
    newPeerID = 'NEW-PEER-1'
    peerAnchor = ts_iso()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID, nextAnchor=peerAnchor))
    session  = pysyncml.Session()
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    # step 3: register some changes
    self.initServer()
    item = self.items.add(NoteItem(name='foo', body='this is the foo'))
    self.store.registerChange(item.id, pysyncml.ITEM_ADDED)
    self.context.save()
    # ensure that changes are registered for both...
    self.initServer()
    self.assertEqual(len(self.server.getKnownPeers()), 2)
    self.assertEqual(self.context._model.Change.q().count(), 2)
    # step 4: synchronize one of the peers
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID,
                                              nextAnchor=peerAnchor, sessionID='2'))
    session  = pysyncml.Session()
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    # step 4a: synchronize - send nothing and expect changes down
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestAlert(self.server.devID, newPeerID,
                                               peerNextAnchor=peerAnchor, sessionID='2'))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    # step 4b: send mapping request, expect a confirm and nothing further
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestMap(self.server.devID, newPeerID, sessionID='2'))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC, peerAdd=1)))
    # ensure that changes remain only for one of them...
    self.initServer()
    peers = self.server.getKnownPeers()
    self.assertEqual(len(peers), 2)
    self.assertEqual(self.context._model.Change.q().count(), 1)
    change = self.context._model.Change.q().one()
    peer0 = [e for e in peers if e.devID == newPeerID0][0]
    self.assertEqual(len(peer0.stores.values()), 1)
    store0 = peer0.stores.values()[0]
    self.assertEqual(change.store_id, store0.id)
    self.assertEqual(change.state, pysyncml.ITEM_ADDED)
    self.assertEqual(change.itemID, '1000')

  #----------------------------------------------------------------------------
  def test_sync_update(self):
    # step 1: register some content (no need to register since no peers)
    item = self.items.add(NoteItem(name='foo', body='this is the foo'))
    # step 2: initialize syncml transaction with a new peer
    newPeerID = 'test.UPDATE.client.%d.devID' % (time.time(),)
    peerAnchor = ts_iso()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID, nextAnchor=peerAnchor))
    session  = pysyncml.Session()
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    srvrAnchor = findxml(response.body, './SyncBody/Alert/Item/Meta/Anchor/Next')
    self.assertTrue(srvrAnchor is not None)
    self.assertIntsNear(int(srvrAnchor), ts())
    # step 3: synchronize - send nothing and expect changes down
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestAlert(self.server.devID, newPeerID,
                                               peerNextAnchor=peerAnchor, sessionID='2'))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    # step 4: send mapping request, expect a confirm and nothing further
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestMap(self.server.devID, newPeerID, sessionID='2'))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC, peerAdd=1)))
    # step 5: make some changes and register them
    self.initServer()
    self.items.replace(NoteItem(id=item.id, name='foo', body='and now it is the bar'), False)
    self.store.registerChange(item.id, pysyncml.ITEM_MODIFIED)
    self.context.save()
    # step 6: initialize syncml transaction with a current peer and new session
    #         (but sleep 1 second first so that anchors are forced to change)
    # TODO: fix the anchor generation so that sleeping is not necessary...
    self.initServer()
    time.sleep(1)
    peerAnchor2 = ts_iso()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID, sessionID='2',
                                              lastAnchor=peerAnchor, nextAnchor=peerAnchor2,
                                              alertCode=200, putDevInfo=False, getDevInfo=False,
                                              ))
    session  = pysyncml.Session()
    returnUrl = 'https://www.example.com/foo;s=90f62fc436b049588526c0e9d9443dd3'
    session.returnUrl = returnUrl
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_TWO_WAY)))
    srvrAnchor2 = findxml(response.body, './SyncBody/Alert/Item/Meta/Anchor/Next')
    self.assertTrue(srvrAnchor2 is not None)
    self.assertIntsNear(int(srvrAnchor2), ts())
    chk = adict(headers=dict((('content-type', 'application/vnd.syncml+xml; charset=UTF-8'),)),
                body=
                '<SyncML>'
                ' <SyncHdr>'
                '  <VerDTD>1.2</VerDTD>'
                '  <VerProto>SyncML/1.2</VerProto>'
                '  <SessionID>2</SessionID>'
                '  <MsgID>1</MsgID>'
                '  <Source>'
                '   <LocURI>' + __name__ + '.server</LocURI>'
                '   <LocName>In-Memory Test Server</LocName>'
                '  </Source>'
                '  <Target>'
                '   <LocURI>' + newPeerID + '</LocURI>'
                '   <LocName>test</LocName>'
                '  </Target>'
                '  <RespURI>' + returnUrl + '</RespURI>'
                '  <Meta>'
                '   <MaxMsgSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxMsgSize>'
                '   <MaxObjSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '  </Meta>'
                ' </SyncHdr>'
                ' <SyncBody>'
                '  <Status>'
                '   <CmdID>1</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>0</CmdRef>'
                '   <Cmd>SyncHdr</Cmd>'
                '   <SourceRef>' + newPeerID + '</SourceRef>'
                '   <TargetRef>' + __name__ + '.server</TargetRef>'
                '   <Data>212</Data>'
                '  </Status>'
                '  <Status>'
                '   <CmdID>2</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>3</CmdRef>'
                '   <Cmd>Alert</Cmd>'
                '   <SourceRef>./cli_memo</SourceRef>'
                '   <TargetRef>srv_note</TargetRef>'
                '   <Data>200</Data>'
                '   <Item>'
                '    <Data>'
                '     <Anchor xmlns="syncml:metinf">'
                '      <Last>' + peerAnchor + '</Last>'
                '      <Next>' + peerAnchor2 + '</Next>'
                '     </Anchor>'
                '    </Data>'
                '   </Item>'
                '  </Status>'
                '  <Alert>'
                '    <CmdID>3</CmdID>'
                '    <Data>200</Data>'
                '    <Item>'
                '      <Source><LocURI>srv_note</LocURI></Source>'
                '      <Target><LocURI>cli_memo</LocURI></Target>'
                '      <Meta>'
                '        <Anchor xmlns="syncml:metinf">'
                '          <Last>' + srvrAnchor + '</Last>'
                '          <Next>' + srvrAnchor2 + '</Next>'
                '        </Anchor>'
                '        <MaxObjSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '      </Meta>'
                '    </Item>'
                '  </Alert>'
                '  <Final/>'
                ' </SyncBody>'
                '</SyncML>')
    self.assertEqual(response.contentType, chk.headers['content-type'])
    self.assertXmlEqual(response.body, chk.body)
    # step 7: synchronize - send nothing and expect changes down (update to item)
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestAlert(self.server.devID, newPeerID, sessionID='2',
                                               peerLastAnchor=srvrAnchor, peerNextAnchor=srvrAnchor2,
                                               resultsStatus=False,
                                               ))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_TWO_WAY)))
    chk = adict(headers=dict((('content-type', 'application/vnd.syncml+xml; charset=UTF-8'),)),
                body=
                '<SyncML>'
                ' <SyncHdr>'
                '  <VerDTD>1.2</VerDTD>'
                '  <VerProto>SyncML/1.2</VerProto>'
                '  <SessionID>2</SessionID>'
                '  <MsgID>2</MsgID>'
                '  <Source>'
                '   <LocURI>' + __name__ + '.server</LocURI>'
                '   <LocName>In-Memory Test Server</LocName>'
                '  </Source>'
                '  <Target>'
                '   <LocURI>' + newPeerID + '</LocURI>'
                '   <LocName>test</LocName>'
                '  </Target>'
                '  <RespURI>' + returnUrl + '</RespURI>'
                ' </SyncHdr>'
                ' <SyncBody>'
                '  <Status>'
                '   <CmdID>1</CmdID>'
                '   <MsgRef>2</MsgRef>'
                '   <CmdRef>0</CmdRef>'
                '   <Cmd>SyncHdr</Cmd>'
                '   <SourceRef>' + newPeerID + '</SourceRef>'
                '   <TargetRef>' + __name__ + '.server</TargetRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Status>'
                '   <CmdID>2</CmdID>'
                '   <MsgRef>2</MsgRef>'
                '   <CmdRef>4</CmdRef>'
                '   <Cmd>Sync</Cmd>'
                '   <SourceRef>./cli_memo</SourceRef>'
                '   <TargetRef>srv_note</TargetRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Sync>'
                '    <CmdID>3</CmdID>'
                '    <Source><LocURI>srv_note</LocURI></Source>'
                '    <Target><LocURI>cli_memo</LocURI></Target>'
                '    <NumberOfChanges>1</NumberOfChanges>'
                '    <Replace>'
                '      <CmdID>4</CmdID>'
                '      <Meta><Type xmlns="syncml:metinf">text/plain</Type></Meta>'
                '      <Item>'
                '        <Target><LocURI>1</LocURI></Target>'
                '        <Data>and now it is the bar</Data>'
                '      </Item>'
                '    </Replace>'
                '  </Sync>'
                '  <Final/>'
                ' </SyncBody>'
                '</SyncML>')
    self.assertEqual(response.contentType, chk.headers['content-type'])
    self.assertXmlEqual(response.body, chk.body)
    # step 8: send final status and nothing further
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestMap(self.server.devID, newPeerID, sessionID='2',
                                             isAdd=False, ))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_TWO_WAY, peerMod=1)))

  #----------------------------------------------------------------------------
  def test_sync_update_with_repeat_devinfo_put(self):
    # NOTE: this is identical to test_sync_update, except that during the
    #       second sync session, the devinfo gets sent again.
    # step 1: register some content (no need to register since no peers)
    item = self.items.add(NoteItem(name='foo', body='this is the foo'))
    # step 2: initialize syncml transaction with a new peer
    newPeerID = 'test.REPEAT-DEVINFO.client.%d.devID' % (time.time(),)
    peerAnchor = ts_iso()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID, nextAnchor=peerAnchor))
    session  = pysyncml.Session()
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    srvrAnchor = findxml(response.body, './SyncBody/Alert/Item/Meta/Anchor/Next')
    self.assertTrue(srvrAnchor is not None)
    self.assertIntsNear(int(srvrAnchor), ts())
    # step 3: synchronize - send nothing and expect changes down
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestAlert(self.server.devID, newPeerID,
                                               peerNextAnchor=peerAnchor, sessionID='2'))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    # step 4: send mapping request, expect a confirm and nothing further
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestMap(self.server.devID, newPeerID, sessionID='2'))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC, peerAdd=1)))
    # step 5: make some changes and register them
    self.initServer()
    self.items.replace(NoteItem(id=item.id, name='foo', body='and now it is the bar'), False)
    self.store.registerChange(item.id, pysyncml.ITEM_MODIFIED)
    self.context.save()
    # step 6: initialize syncml transaction with a current peer and new session
    #         (but sleep 1 second first so that anchors are forced to change)
    #         and send the PUT/GET devinfo (to ensure that it does not break
    #         server-side bindings)
    # TODO: fix the anchor generation so that sleeping is not necessary...
    self.initServer()
    time.sleep(1)
    peerAnchor2 = ts_iso()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID, sessionID='2',
                                              lastAnchor=peerAnchor, nextAnchor=peerAnchor2,
                                              alertCode=200, putDevInfo=True, getDevInfo=True,
                                              ))
    session  = pysyncml.Session()
    returnUrl = 'https://www.example.com/foo;s=90f62fc436b049588526c0e9d9443dd3'
    session.returnUrl = returnUrl
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_TWO_WAY)))
    srvrAnchor2 = findxml(response.body, './SyncBody/Alert/Item/Meta/Anchor/Next')
    self.assertTrue(srvrAnchor2 is not None)
    self.assertIntsNear(int(srvrAnchor2), ts())
    chk = adict(headers=dict((('content-type', 'application/vnd.syncml+xml; charset=UTF-8'),)),
                body=
                '<SyncML>'
                ' <SyncHdr>'
                '  <VerDTD>1.2</VerDTD>'
                '  <VerProto>SyncML/1.2</VerProto>'
                '  <SessionID>2</SessionID>'
                '  <MsgID>1</MsgID>'
                '  <Source>'
                '   <LocURI>' + __name__ + '.server</LocURI>'
                '   <LocName>In-Memory Test Server</LocName>'
                '  </Source>'
                '  <Target>'
                '   <LocURI>' + newPeerID + '</LocURI>'
                '   <LocName>test</LocName>'
                '  </Target>'
                '  <RespURI>' + returnUrl + '</RespURI>'
                '  <Meta>'
                '   <MaxMsgSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxMsgSize>'
                '   <MaxObjSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '  </Meta>'
                ' </SyncHdr>'
                ' <SyncBody>'
                '  <Status>'
                '   <CmdID>1</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>0</CmdRef>'
                '   <Cmd>SyncHdr</Cmd>'
                '   <SourceRef>' + newPeerID + '</SourceRef>'
                '   <TargetRef>' + __name__ + '.server</TargetRef>'
                '   <Data>212</Data>'
                '  </Status>'
                '  <Status>'
                '   <CmdID>2</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>1</CmdRef>'
                '   <Cmd>Put</Cmd>'
                '   <SourceRef>./devinf12</SourceRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Status>'
                '   <CmdID>3</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>2</CmdRef>'
                '   <Cmd>Get</Cmd>'
                '   <TargetRef>./devinf12</TargetRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Results>'
                '   <CmdID>4</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>2</CmdRef>'
                '   <Meta><Type xmlns="syncml:metinf">application/vnd.syncml-devinf+xml</Type></Meta>'
                '   <Item>'
                '    <Source><LocURI>./devinf12</LocURI><LocName>./devinf12</LocName></Source>'
                '    <Data>'
                '     <DevInf xmlns="syncml:devinf">'
                '      <VerDTD>1.2</VerDTD>'
                '      <Man>pysyncml</Man>'
                '      <Mod>' + __name__ + '.server</Mod>'
                '      <OEM>-</OEM>'
                '      <FwV>-</FwV>'
                '      <SwV>-</SwV>'
                '      <HwV>-</HwV>'
                '      <DevID>' + __name__ + '.server</DevID>'
                '      <DevTyp>server</DevTyp>'
                '      <UTC/>'
                '      <SupportLargeObjs/>'
                '      <SupportHierarchicalSync/>'
                '      <SupportNumberOfChanges/>'
                '      <DataStore>'
                '       <SourceRef>srv_note</SourceRef>'
                '       <DisplayName>Server Note Store</DisplayName>'
                '       <MaxGUIDSize>' + str(getAddressSize()) + '</MaxGUIDSize>'
                '       <MaxObjSize>' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '       <Rx-Pref><CTType>text/x-s4j-sifn</CTType><VerCT>1.1</VerCT></Rx-Pref>'
                '       <Rx><CTType>text/x-s4j-sifn</CTType><VerCT>1.0</VerCT></Rx>'
                '       <Rx><CTType>text/plain</CTType><VerCT>1.1</VerCT></Rx>'
                '       <Rx><CTType>text/plain</CTType><VerCT>1.0</VerCT></Rx>'
                '       <Tx-Pref><CTType>text/x-s4j-sifn</CTType><VerCT>1.1</VerCT></Tx-Pref>'
                '       <Tx><CTType>text/x-s4j-sifn</CTType><VerCT>1.0</VerCT></Tx>'
                '       <Tx><CTType>text/plain</CTType><VerCT>1.1</VerCT></Tx>'
                '       <Tx><CTType>text/plain</CTType><VerCT>1.0</VerCT></Tx>'
                '       <SyncCap>'
                '        <SyncType>1</SyncType>'
                '        <SyncType>2</SyncType>'
                '        <SyncType>3</SyncType>'
                '        <SyncType>4</SyncType>'
                '        <SyncType>5</SyncType>'
                '        <SyncType>6</SyncType>'
                '        <SyncType>7</SyncType>'
                '       </SyncCap>'
                '      </DataStore>'
                '     </DevInf>'
                '    </Data>'
                '   </Item>'
                '  </Results>'
                '  <Status>'
                '   <CmdID>5</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>3</CmdRef>'
                '   <Cmd>Alert</Cmd>'
                '   <SourceRef>./cli_memo</SourceRef>'
                '   <TargetRef>srv_note</TargetRef>'
                '   <Data>200</Data>'
                '   <Item>'
                '    <Data>'
                '     <Anchor xmlns="syncml:metinf">'
                '      <Last>' + peerAnchor + '</Last>'
                '      <Next>' + peerAnchor2 + '</Next>'
                '     </Anchor>'
                '    </Data>'
                '   </Item>'
                '  </Status>'
                '  <Alert>'
                '    <CmdID>6</CmdID>'
                '    <Data>200</Data>'
                '    <Item>'
                '      <Source><LocURI>srv_note</LocURI></Source>'
                '      <Target><LocURI>cli_memo</LocURI></Target>'
                '      <Meta>'
                '        <Anchor xmlns="syncml:metinf">'
                '          <Last>' + srvrAnchor + '</Last>'
                '          <Next>' + srvrAnchor2 + '</Next>'
                '        </Anchor>'
                '        <MaxObjSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '      </Meta>'
                '    </Item>'
                '  </Alert>'
                '  <Final/>'
                ' </SyncBody>'
                '</SyncML>')
    self.assertEqual(response.contentType, chk.headers['content-type'])
    self.assertXmlEqual(response.body, chk.body)
    # step 7: synchronize - send nothing and expect changes down (update to item)
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestAlert(self.server.devID, newPeerID, sessionID='2',
                                               peerLastAnchor=srvrAnchor, peerNextAnchor=srvrAnchor2,
                                               resultsStatus=True,
                                               ))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_TWO_WAY)))
    chk = adict(headers=dict((('content-type', 'application/vnd.syncml+xml; charset=UTF-8'),)),
                body=
                '<SyncML>'
                ' <SyncHdr>'
                '  <VerDTD>1.2</VerDTD>'
                '  <VerProto>SyncML/1.2</VerProto>'
                '  <SessionID>2</SessionID>'
                '  <MsgID>2</MsgID>'
                '  <Source>'
                '   <LocURI>' + __name__ + '.server</LocURI>'
                '   <LocName>In-Memory Test Server</LocName>'
                '  </Source>'
                '  <Target>'
                '   <LocURI>' + newPeerID + '</LocURI>'
                '   <LocName>test</LocName>'
                '  </Target>'
                '  <RespURI>' + returnUrl + '</RespURI>'
                ' </SyncHdr>'
                ' <SyncBody>'
                '  <Status>'
                '   <CmdID>1</CmdID>'
                '   <MsgRef>2</MsgRef>'
                '   <CmdRef>0</CmdRef>'
                '   <Cmd>SyncHdr</Cmd>'
                '   <SourceRef>' + newPeerID + '</SourceRef>'
                '   <TargetRef>' + __name__ + '.server</TargetRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Status>'
                '   <CmdID>2</CmdID>'
                '   <MsgRef>2</MsgRef>'
                '   <CmdRef>4</CmdRef>'
                '   <Cmd>Sync</Cmd>'
                '   <SourceRef>./cli_memo</SourceRef>'
                '   <TargetRef>srv_note</TargetRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Sync>'
                '    <CmdID>3</CmdID>'
                '    <Source><LocURI>srv_note</LocURI></Source>'
                '    <Target><LocURI>cli_memo</LocURI></Target>'
                '    <NumberOfChanges>1</NumberOfChanges>'
                '    <Replace>'
                '      <CmdID>4</CmdID>'
                '      <Meta><Type xmlns="syncml:metinf">text/plain</Type></Meta>'
                '      <Item>'
                '        <Target><LocURI>1</LocURI></Target>'
                '        <Data>and now it is the bar</Data>'
                '      </Item>'
                '    </Replace>'
                '  </Sync>'
                '  <Final/>'
                ' </SyncBody>'
                '</SyncML>')
    self.assertEqual(response.contentType, chk.headers['content-type'])
    self.assertXmlEqual(response.body, chk.body)
    # step 8: send final status and nothing further
    self.initServer()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestMap(self.server.devID, newPeerID, sessionID='2',
                                             isAdd=False, ))
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_TWO_WAY, peerMod=1)))

  #----------------------------------------------------------------------------
  def test_force_slowsync(self):
    newPeerID = 'test.client.%d.devID' % (time.time(),)
    peerAnchor = ts_iso()
    request = adict(headers=dict((('content-type', 'application/vnd.syncml+xml'),)),
                    body=self.makeRequestInit(self.server.devID, newPeerID,
                                              alertCode=200, lastAnchor='bogus1', nextAnchor=peerAnchor))
    session  = pysyncml.Session()
    response = pysyncml.Response()
    stats = self.server.handleRequest(session, request, response)
    self.assertTrimDictEqual(stats, dict(srv_note=stat(mode=pysyncml.SYNCTYPE_SLOW_SYNC)))
    srvrAnchor = findxml(response.body, './SyncBody/Alert/Item/Meta/Anchor/Next')
    chk = adict(headers=dict((('content-type', 'application/vnd.syncml+xml; charset=UTF-8'),)),
                body=
                '<SyncML>'
                ' <SyncHdr>'
                '  <VerDTD>1.2</VerDTD>'
                '  <VerProto>SyncML/1.2</VerProto>'
                '  <SessionID>1</SessionID>'
                '  <MsgID>1</MsgID>'
                '  <Source>'
                '   <LocURI>' + __name__ + '.server</LocURI>'
                '   <LocName>In-Memory Test Server</LocName>'
                '  </Source>'
                '  <Target>'
                '   <LocURI>' + newPeerID + '</LocURI>'
                '   <LocName>test</LocName>'
                '  </Target>'
                '  <Meta>'
                '   <MaxMsgSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxMsgSize>'
                '   <MaxObjSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '  </Meta>'
                ' </SyncHdr>'
                ' <SyncBody>'
                '  <Status>'
                '   <CmdID>1</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>0</CmdRef>'
                '   <Cmd>SyncHdr</Cmd>'
                '   <SourceRef>' + newPeerID + '</SourceRef>'
                '   <TargetRef>' + __name__ + '.server</TargetRef>'
                '   <Data>212</Data>'
                '  </Status>'
                '  <Status>'
                '   <CmdID>2</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>1</CmdRef>'
                '   <Cmd>Put</Cmd>'
                '   <SourceRef>./devinf12</SourceRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Status>'
                '   <CmdID>3</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>2</CmdRef>'
                '   <Cmd>Get</Cmd>'
                '   <TargetRef>./devinf12</TargetRef>'
                '   <Data>200</Data>'
                '  </Status>'
                '  <Results>'
                '   <CmdID>4</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>2</CmdRef>'
                '   <Meta><Type xmlns="syncml:metinf">application/vnd.syncml-devinf+xml</Type></Meta>'
                '   <Item>'
                '    <Source><LocURI>./devinf12</LocURI><LocName>./devinf12</LocName></Source>'
                '    <Data>'
                '     <DevInf xmlns="syncml:devinf">'
                '      <VerDTD>1.2</VerDTD>'
                '      <Man>pysyncml</Man>'
                '      <Mod>' + __name__ + '.server</Mod>'
                '      <OEM>-</OEM>'
                '      <FwV>-</FwV>'
                '      <SwV>-</SwV>'
                '      <HwV>-</HwV>'
                '      <DevID>' + __name__ + '.server</DevID>'
                '      <DevTyp>server</DevTyp>'
                '      <UTC/>'
                '      <SupportLargeObjs/>'
                '      <SupportHierarchicalSync/>'
                '      <SupportNumberOfChanges/>'
                '      <DataStore>'
                '       <SourceRef>srv_note</SourceRef>'
                '       <DisplayName>Server Note Store</DisplayName>'
                '       <MaxGUIDSize>' + str(getAddressSize()) + '</MaxGUIDSize>'
                '       <MaxObjSize>' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '       <Rx-Pref><CTType>text/x-s4j-sifn</CTType><VerCT>1.1</VerCT></Rx-Pref>'
                '       <Rx><CTType>text/x-s4j-sifn</CTType><VerCT>1.0</VerCT></Rx>'
                '       <Rx><CTType>text/plain</CTType><VerCT>1.1</VerCT></Rx>'
                '       <Rx><CTType>text/plain</CTType><VerCT>1.0</VerCT></Rx>'
                '       <Tx-Pref><CTType>text/x-s4j-sifn</CTType><VerCT>1.1</VerCT></Tx-Pref>'
                '       <Tx><CTType>text/x-s4j-sifn</CTType><VerCT>1.0</VerCT></Tx>'
                '       <Tx><CTType>text/plain</CTType><VerCT>1.1</VerCT></Tx>'
                '       <Tx><CTType>text/plain</CTType><VerCT>1.0</VerCT></Tx>'
                '       <SyncCap>'
                '        <SyncType>1</SyncType>'
                '        <SyncType>2</SyncType>'
                '        <SyncType>3</SyncType>'
                '        <SyncType>4</SyncType>'
                '        <SyncType>5</SyncType>'
                '        <SyncType>6</SyncType>'
                '        <SyncType>7</SyncType>'
                '       </SyncCap>'
                '      </DataStore>'
                '     </DevInf>'
                '    </Data>'
                '   </Item>'
                '  </Results>'
                '  <Status>'
                '   <CmdID>5</CmdID>'
                '   <MsgRef>1</MsgRef>'
                '   <CmdRef>3</CmdRef>'
                '   <Cmd>Alert</Cmd>'
                '   <SourceRef>./cli_memo</SourceRef>'
                '   <TargetRef>srv_note</TargetRef>'
                '   <Data>508</Data>'
                '   <Item>'
                '    <Data>'
                '     <Anchor xmlns="syncml:metinf"><Next>' + peerAnchor + '</Next></Anchor>'
                '    </Data>'
                '   </Item>'
                '  </Status>'
                '  <Alert>'
                '    <CmdID>6</CmdID>'
                '    <Data>201</Data>'
                '    <Item>'
                '      <Source><LocURI>srv_note</LocURI></Source>'
                '      <Target><LocURI>cli_memo</LocURI></Target>'
                '      <Meta>'
                '        <Anchor xmlns="syncml:metinf">'
                '          <Next>' + str(srvrAnchor) + '</Next>'
                '        </Anchor>'
                '        <MaxObjSize xmlns="syncml:metinf">' + str(getMaxMemorySize()) + '</MaxObjSize>'
                '      </Meta>'
                '    </Item>'
                '  </Alert>'
                '  <Final/>'
                ' </SyncBody>'
                '</SyncML>')
    self.assertEqual(response.contentType, chk.headers['content-type'])
    self.assertXmlEqual(response.body, chk.body)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
