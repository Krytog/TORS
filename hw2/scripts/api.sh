#!/bin/bash

leader() {
    local addr=$1

    local url="http://$addr/leader"

    curl -s -X GET "$url"
}

read() {
    local addr=$1
    local key=$2

    local url="http://$addr/data/$key"

    curl -s -X GET "$url"
}

create() {
    local addr=$1
    local key=$2
    local value=$3

    local url="http://$addr/create?key=$key&value=$value"

    curl -s -X POST "$url"
}

debug_log() {
    local addr=$1

    local url="http://$addr/debug/log"

    curl -s -X GET "$url"
}

debug_store() {
    local addr=$1

    local url="http://$addr/debug/store"

    curl -s -X GET "$url"
}
