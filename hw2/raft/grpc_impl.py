from raft.status import STATUS_HOLDER, Status
from raft.state import STATE, LEADER_STATE
from raft.config import CONFIG, MY_ID

from proto import raft_pb2 as raft_pb2
from proto import raft_pb2_grpc as raft_pb2_grpc


class RaftGRPC(raft_pb2_grpc.RaftServicer):

    async def AskVote(self, request, context):
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

        if (len(STATE.log) > 0 and
           (STATE.log[-1].term > request.log_last_term or 
           (STATE.log[-1].term == request.log_last_term and len(STATE.log) > request.log_last_index))):
            return raft_pb2.VoteResponse(
                term = STATE.term,
                is_vote_granted = False,
            )
        
        STATE.voted_for = request.candidate_id
        STATE.dump_state_to_storage()

        return raft_pb2.VoteResponse(
            term = STATE.term,
            is_vote_granted = True,
        )

    async def AppendEntries(self, request, context):
        return raft_pb2.AppendEntriesResponse(
            term = STATE.term,
            is_successful = True,
        )
