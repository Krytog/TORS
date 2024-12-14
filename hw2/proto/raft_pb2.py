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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10proto/raft.proto\x12\x04raft\"`\n\x0bVoteRequest\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x14\n\x0c\x63\x61ndidate_id\x18\x02 \x01(\x04\x12\x15\n\rlog_last_term\x18\x03 \x01(\x04\x12\x16\n\x0elog_last_index\x18\x04 \x01(\x04\"5\n\x0cVoteResponse\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x17\n\x0fis_vote_granted\x18\x02 \x01(\x08\"z\n\x08LogEntry\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x0f\n\x07\x63ommand\x18\x02 \x01(\t\x12\x0b\n\x03key\x18\x03 \x01(\t\x12\x12\n\x05value\x18\x04 \x01(\tH\x00\x88\x01\x01\x12\x16\n\told_value\x18\x05 \x01(\tH\x01\x88\x01\x01\x42\x08\n\x06_valueB\x0c\n\n_old_value\"\xa4\x01\n\x14\x41ppendEntriesRequest\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x11\n\tleader_id\x18\x02 \x01(\x04\x12\x15\n\rlog_prev_term\x18\x03 \x01(\x04\x12\x16\n\x0elog_prev_index\x18\x04 \x01(\x04\x12\x1f\n\x07\x65ntries\x18\x05 \x03(\x0b\x32\x0e.raft.LogEntry\x12\x1b\n\x13leader_commit_index\x18\x06 \x01(\x04\"<\n\x15\x41ppendEntriesResponse\x12\x0c\n\x04term\x18\x01 \x01(\x04\x12\x15\n\ris_successful\x18\x02 \x01(\x08\x32\x82\x01\n\x04Raft\x12\x30\n\x07\x41skVote\x12\x11.raft.VoteRequest\x1a\x12.raft.VoteResponse\x12H\n\rAppendEntries\x12\x1a.raft.AppendEntriesRequest\x1a\x1b.raft.AppendEntriesResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.raft_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_VOTEREQUEST']._serialized_start=26
  _globals['_VOTEREQUEST']._serialized_end=122
  _globals['_VOTERESPONSE']._serialized_start=124
  _globals['_VOTERESPONSE']._serialized_end=177
  _globals['_LOGENTRY']._serialized_start=179
  _globals['_LOGENTRY']._serialized_end=301
  _globals['_APPENDENTRIESREQUEST']._serialized_start=304
  _globals['_APPENDENTRIESREQUEST']._serialized_end=468
  _globals['_APPENDENTRIESRESPONSE']._serialized_start=470
  _globals['_APPENDENTRIESRESPONSE']._serialized_end=530
  _globals['_RAFT']._serialized_start=533
  _globals['_RAFT']._serialized_end=663
# @@protoc_insertion_point(module_scope)
