# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: kafka_management.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'kafka_management.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16kafka_management.proto\x12\x0c\x65ventgateway\"A\n\x0ePublishRequest\x12\x11\n\ttopic_key\x18\x01 \x01(\t\x12\x0b\n\x03key\x18\x02 \x01(\t\x12\x0f\n\x07payload\x18\x03 \x01(\x0c\".\n\x0fPublishResponse\x12\n\n\x02ok\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"&\n\x10SubscribeRequest\x12\x12\n\ntopic_keys\x18\x01 \x03(\t\"\xa7\x01\n\rEventEnvelope\x12\r\n\x05topic\x18\x01 \x01(\t\x12\x0b\n\x03key\x18\x02 \x01(\t\x12\x0f\n\x07payload\x18\x03 \x01(\x0c\x12\x39\n\x07headers\x18\x04 \x03(\x0b\x32(.eventgateway.EventEnvelope.HeadersEntry\x1a.\n\x0cHeadersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x0c:\x02\x38\x01\x32\xa2\x01\n\x0c\x45ventGateway\x12\x46\n\x07Publish\x12\x1c.eventgateway.PublishRequest\x1a\x1d.eventgateway.PublishResponse\x12J\n\tSubscribe\x12\x1e.eventgateway.SubscribeRequest\x1a\x1b.eventgateway.EventEnvelope0\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'kafka_management_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_EVENTENVELOPE_HEADERSENTRY']._loaded_options = None
  _globals['_EVENTENVELOPE_HEADERSENTRY']._serialized_options = b'8\001'
  _globals['_PUBLISHREQUEST']._serialized_start=40
  _globals['_PUBLISHREQUEST']._serialized_end=105
  _globals['_PUBLISHRESPONSE']._serialized_start=107
  _globals['_PUBLISHRESPONSE']._serialized_end=153
  _globals['_SUBSCRIBEREQUEST']._serialized_start=155
  _globals['_SUBSCRIBEREQUEST']._serialized_end=193
  _globals['_EVENTENVELOPE']._serialized_start=196
  _globals['_EVENTENVELOPE']._serialized_end=363
  _globals['_EVENTENVELOPE_HEADERSENTRY']._serialized_start=317
  _globals['_EVENTENVELOPE_HEADERSENTRY']._serialized_end=363
  _globals['_EVENTGATEWAY']._serialized_start=366
  _globals['_EVENTGATEWAY']._serialized_end=528
# @@protoc_insertion_point(module_scope)
