package com.amongus.core.impl.voting;

import com.amongus.core.api.Vote.Vote;
import com.amongus.core.api.player.PlayerId;

public class VoteImpl implements Vote {

    private final PlayerId voterId;
    private final PlayerId targetId; // null = skip

    public VoteImpl(PlayerId voterId, PlayerId targetId) {
        this.voterId = voterId;
        this.targetId = targetId;
    }

    @Override
    public PlayerId getVoterId() { return voterId; }

    @Override
    public PlayerId getTargetId() { return targetId; }

    @Override
    public boolean isSkip() { return targetId == null; }
}
