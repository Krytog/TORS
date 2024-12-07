#!/bin/bash

# Should be executed from the project root
ROOT_DIR="."
PROTO_DIR="./proto"

python3 -m grpc_tools.protoc \
       --proto_path=$ROOT_DIR \
       --python_out=$PROTO_DIR \
       --grpc_python_out=$PROTO_DIR \
       $PROTO_DIR/raft.proto

# The best work-around I've found
cp -r "./proto/proto"/* "./proto"
rm -r "./proto/proto"
