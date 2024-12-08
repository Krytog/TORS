from raft.state import STATE, LogEntry
from raft.timings import TIMING

from proto import raft_pb2 as raft_pb2
from proto import raft_pb2_grpc as raft_pb2_grpc

from time import time


class RaftGRPC(raft_pb2_grpc.RaftServicer):

    async def AskVote(self, request, context):
        if request.term > STATE.term:
            STATE.update_if_stale(request.term)

        if request.term < STATE.term:
            return raft_pb2.VoteResponse(
                term = STATE.term,
                is_vote_granted = False,
            )

        if STATE.voted_for != 0 and STATE.voted_for != request.candidate_id:
            return raft_pb2.VoteResponse(
                term = STATE.term,
                is_vote_granted = False,
            )

        if (STATE.log[-1].term > request.log_last_term or 
           (STATE.log[-1].term == request.log_last_term and len(STATE.log) - 1 > request.log_last_index)):
            return raft_pb2.VoteResponse(
                term = STATE.term,
                is_vote_granted = False,
            )
        
        STATE.voted_for = request.candidate_id
        STATE.dump_state_to_storage()

        TIMING.set_new_last_action_timestamp_safe(time())

        return raft_pb2.VoteResponse(
            term = STATE.term,
            is_vote_granted = True,
        )

    async def AppendEntries(self, request, context):
        if request.term > STATE.term:
            STATE.update_if_stale(request.term)

        if request.term < STATE.term:
            return raft_pb2.AppendEntriesResponse(
                term = STATE.term,
                is_successful = False,
            )

        if (len(STATE.log) - 1 < request.log_prev_index or
            STATE.log[request.log_prev_index].term != request.log_prev_term):
            return raft_pb2.AppendEntriesResponse(
                term = STATE.term,
                is_successful = False,
            )
        
        TIMING.set_new_last_action_timestamp_safe(time())
        STATE.leader_id = request.leader_id
        
        to_insert_index = 0
        for i in range(len(request.entries)):
            if STATE.get_log_entry_safe(request.log_prev_index + 1 + i).term != request.entries[i].term:
                to_insert_index = i

        STATE.remove_log_tail_safe(request.log_prev_index + i)

        for i in range(to_insert_index, len(request.entries[i])):
            STATE.append_to_log_safe(
                LogEntry(
                    term=request.entries[i].term,
                    command=request.entries[i].command,
                    key=request.entries[i].key,
                    value=request.entries[i].value,
                )
            )
        
        if request.leader_commit_index > STATE.log_commited_index:
            STATE.log_commited_index = min(request.leader_commit_index, len(STATE.log) - 1)

        return raft_pb2.AppendEntriesResponse(
            term = STATE.term,
            is_successful = True,
        )
