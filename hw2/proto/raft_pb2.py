# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/raft.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10proto/raft.proto\x12\x04raft\x1a\x1bgoogle/protobuf/empty.proto\"`\n\x0bVoteRequest\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x14\n\x0c\x63\x61ndidate_id\x18\x02 \x01(\x04\x12\x15\n\rlog_last_term\x18\x03 \x01(\x04\x12\x16\n\x0elog_last_index\x18\x04 \x01(\x04\"5\n\x0cVoteResponse\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x17\n\x0fis_vote_granted\x18\x02 \x01(\x08\"\x94\x01\n\x14\x41ppendEntriesRequets\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x11\n\tleader_id\x18\x02 \x01(\x04\x12\x15\n\rlog_prev_term\x18\x03 \x01(\x04\x12\x16\n\x0elog_prev_index\x18\x04 \x01(\x04\x12\x0f\n\x07\x65ntries\x18\x05 \x03(\t\x12\x1b\n\x13leader_commit_index\x18\x06 \x01(\x04\"<\n\x15\x41ppendEntriesResponse\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x15\n\ris_successful\x18\x02 \x01(\x08\x32\x82\x01\n\x04Raft\x12\x30\n\x07\x41skVote\x12\x11.raft.VoteRequest\x1a\x12.raft.VoteResponse\x12H\n\rAppendEntries\x12\x1a.raft.AppendEntriesRequets\x1a\x1b.raft.AppendEntriesResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.raft_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_VOTEREQUEST']._serialized_start=55
  _globals['_VOTEREQUEST']._serialized_end=151
  _globals['_VOTERESPONSE']._serialized_start=153
  _globals['_VOTERESPONSE']._serialized_end=206
  _globals['_APPENDENTRIESREQUETS']._serialized_start=209
  _globals['_APPENDENTRIESREQUETS']._serialized_end=357
  _globals['_APPENDENTRIESRESPONSE']._serialized_start=359
  _globals['_APPENDENTRIESRESPONSE']._serialized_end=419
  _globals['_RAFT']._serialized_start=422
  _globals['_RAFT']._serialized_end=552
# @@protoc_insertion_point(module_scope)