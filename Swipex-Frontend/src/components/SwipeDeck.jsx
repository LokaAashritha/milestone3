import React, { useState, useEffect } from 'react';
import {
  motion,
  useMotionValue,
  useTransform,
  AnimatePresence,
} from 'framer-motion';
import {
  Building2,
  MapPin,
  Sparkles,
  X,
  Bookmark,
  Heart,
  RotateCcw,
  RefreshCw,
} from 'lucide-react';

import {
  RecommendationService,
  SwipeService,
} from '../services/api';

export default function SwipeDeck() {
  const [deck, setDeck] = useState([]);
  const [swipeHistory, setSwipeHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Framer Motion drag variables
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const rotate = useTransform(
    x,
    [-200, 200],
    [-20, 20]
  );

  const opacity = useTransform(
    x,
    [-200, -150, 0, 150, 200],
    [0, 1, 1, 1, 0]
  );

  useEffect(() => {
    loadDeck();
  }, []);

  /**
   * Load recommendations from the real Gateway.
   *
   * Frontend
   *   ↓
   * Gateway :8000
   *   ↓
   * AIML :8002
   *   ↓
   * Job Data :8004
   *
   * There is intentionally NO fallback/mock job list.
   */
  const loadDeck = async () => {
    setLoading(true);
    setError('');

    try {
      const response =
        await RecommendationService.getUpgradedRecommendations(10);

      const recommendations = Array.isArray(
        response?.recommendations
      )
        ? response.recommendations
        : [];

      setDeck(recommendations);
    } catch (err) {
      console.error(
        'Failed to load AI recommendations:',
        err
      );

      setDeck([]);

      setError(
        err?.message ||
          'Unable to load recommendations from the server.'
      );
    } finally {
      setLoading(false);
    }
  };

  const currentJob = deck[0];

  /**
   * Get the Gateway Job UUID.
   *
   * Recommendations are returned using the Gateway job object.
   * The frontend must send this ID back to the Gateway for swipes.
   */
  const getCurrentJobId = (job) => {
    return (
      job?.id ||
      job?.job_id ||
      job?.job?.id ||
      job?.job?.job_id ||
      null
    );
  };

  /**
   * Get the AI match score without inventing a score.
   *
   * The previous implementation used:
   *     || 88
   *
   * That has been removed.
   */
  const getMatchScore = (job) => {
    const score =
      job?.match_score ??
      job?.semantic_match_score ??
      job?.matchScore ??
      null;

    if (score === null || score === undefined) {
      return null;
    }

    const numericScore = Number(score);

    if (!Number.isFinite(numericScore)) {
      return null;
    }

    return Math.round(numericScore);
  };

  /**
   * Record the user's action through the Gateway.
   *
   * The Gateway is responsible for forwarding interaction
   * information to the Job Data service.
   */
  const handleSwipe = async (actionType) => {
    if (!currentJob) {
      return;
    }

    const targetJob = currentJob;
    const jobId = getCurrentJobId(targetJob);

    if (!jobId) {
      console.error(
        'Cannot record swipe: recommendation has no valid Gateway job ID.',
        targetJob
      );

      setError(
        'This recommendation does not contain a valid job ID.'
      );

      return;
    }

    /**
     * Remove the card immediately for smooth UI.
     * The actual interaction is still persisted through
     * the Gateway request below.
     */
    setDeck((previousDeck) =>
      previousDeck.slice(1)
    );

    setSwipeHistory((previousHistory) => [
      targetJob,
      ...previousHistory,
    ]);

    try {
      await SwipeService.recordCandidateSwipe(
        null,
        jobId,
        actionType
      );
    } catch (err) {
      console.error(
        'Failed to record swipe:',
        err
      );

      /**
       * Restore the card because the server did not
       * confirm the interaction.
       */
      setDeck((previousDeck) => [
        targetJob,
        ...previousDeck,
      ]);

      setSwipeHistory((previousHistory) =>
        previousHistory.filter(
          (job) => getCurrentJobId(job) !== jobId
        )
      );

      setError(
        err?.message ||
          'Unable to save your action. Please try again.'
      );
    }
  };

  /**
   * Drag gestures:
   *
   * Right  → Apply / Like
   * Left   → Skip
   * Up     → Save
   */
  const handleDragEnd = (event, info) => {
    if (info.offset.x > 100) {
      handleSwipe('like');
    } else if (info.offset.x < -100) {
      handleSwipe('skip');
    } else if (info.offset.y < -100) {
      handleSwipe('save');
    }
  };

  /**
   * Undo the latest recorded interaction.
   */
  const handleUndo = async () => {
    if (swipeHistory.length === 0) {
      return;
    }

    const lastJob = swipeHistory[0];
    const jobId = getCurrentJobId(lastJob);

    if (!jobId) {
      console.error(
        'Cannot undo swipe: invalid job ID.',
        lastJob
      );

      return;
    }

    try {
      await SwipeService.undoSwipe(jobId);

      setDeck((previousDeck) => [
        lastJob,
        ...previousDeck,
      ]);

      setSwipeHistory((previousHistory) =>
        previousHistory.slice(1)
      );

      setError('');
    } catch (err) {
      console.error(
        'Failed to undo swipe:',
        err
      );

      setError(
        err?.message ||
          'Unable to undo the last action.'
      );
    }
  };

  /* ==========================================================================
     LOADING STATE
     ========================================================================== */

  if (loading) {
    return (
      <div className="text-center py-20 space-y-3">
        <RefreshCw className="w-8 h-8 text-purple-600 animate-spin mx-auto" />

        <p className="text-xs font-bold text-slate-400">
          Fetching AI Career Recommendations...
        </p>
      </div>
    );
  }

  /* ==========================================================================
     ERROR STATE
     ========================================================================== */

  if (error && !currentJob) {
    return (
      <div className="text-center p-8 bg-white border border-slate-200 rounded-3xl space-y-4 shadow-sm max-w-sm w-full">
        <Sparkles className="w-10 h-10 text-purple-600 mx-auto" />

        <h3 className="text-base font-black text-slate-900">
          Recommendations unavailable
        </h3>

        <p className="text-xs text-slate-500 font-medium">
          {error}
        </p>

        <button
          onClick={loadDeck}
          className="px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold transition cursor-pointer shadow-sm"
        >
          Try Again
        </button>
      </div>
    );
  }

  /* ==========================================================================
     EMPTY STATE
     ========================================================================== */

  if (!currentJob) {
    return (
      <div className="text-center p-8 bg-white border border-slate-200 rounded-3xl space-y-4 shadow-sm max-w-sm w-full">
        <Sparkles className="w-10 h-10 text-purple-600 mx-auto" />

        <h3 className="text-base font-black text-slate-900">
          You're all caught up!
        </h3>

        <p className="text-xs text-slate-500 font-medium">
          No more AI-recommended opportunities are available
          in your feed right now.
        </p>

        <button
          onClick={loadDeck}
          className="px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold transition cursor-pointer shadow-sm"
        >
          Refresh Feed
        </button>
      </div>
    );
  }

  const currentJobId = getCurrentJobId(currentJob);
  const matchScore = getMatchScore(currentJob);

  const companyName =
    currentJob?.company_name ||
    currentJob?.company ||
    currentJob?.company?.name ||
    'Employer';

  const skills =
    Array.isArray(currentJob?.skills)
      ? currentJob.skills
      : Array.isArray(currentJob?.skills_required)
      ? currentJob.skills_required
      : [];

  const recommendationTags =
    Array.isArray(currentJob?.recommendation_tags)
      ? currentJob.recommendation_tags
      : [];

  const matchReasons =
    Array.isArray(currentJob?.match_reasons)
      ? currentJob.match_reasons
      : [];

  return (
    <div className="w-full max-w-md relative flex flex-col items-center">

      {/* ======================================================================
          JOB CARD
          ====================================================================== */}

      <AnimatePresence mode="wait">
        <motion.div
          key={currentJobId}
          style={{
            x,
            y,
            rotate,
            opacity,
          }}
          drag
          dragConstraints={{
            left: 0,
            right: 0,
            top: 0,
            bottom: 0,
          }}
          onDragEnd={handleDragEnd}
          className="w-full bg-white border border-slate-200 rounded-3xl p-6 shadow-xl space-y-5 cursor-grab active:cursor-grabbing select-none"
        >

          {/* ------------------------------------------------------------------
              Header & Match Badge
              ------------------------------------------------------------------ */}

          <div className="flex justify-between items-start gap-3">

            <div className="flex items-center gap-3 min-w-0">

              <div className="w-12 h-12 rounded-2xl border border-slate-100 bg-purple-50 flex items-center justify-center flex-shrink-0">
                <Building2 className="w-6 h-6 text-purple-600" />
              </div>

              <div className="min-w-0">
                <h3 className="text-xs font-bold text-slate-400 truncate">
                  {companyName}
                </h3>

                <h2 className="text-base font-black text-slate-900">
                  {currentJob.title || 'Job Opportunity'}
                </h2>
              </div>

            </div>

            {/* AI Match Score */}

            {matchScore !== null && (
              <div className="bg-purple-600 text-white px-3 py-1 rounded-full flex items-center gap-1 text-xs font-black shadow-xs flex-shrink-0">
                <Sparkles className="w-3 h-3 fill-white" />

                <span>
                  {matchScore}%
                </span>
              </div>
            )}

          </div>

          {/* ------------------------------------------------------------------
              Location & Salary
              ------------------------------------------------------------------ */}

          <div className="flex flex-wrap items-center gap-3 text-xs font-bold text-slate-500">

            {currentJob.location && (
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-purple-600" />

                {currentJob.location}
              </span>
            )}

            {currentJob.salary_range && (
              <span className="bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded-lg">
                {currentJob.salary_range}
              </span>
            )}

          </div>

          {/* ------------------------------------------------------------------
              Recommendation Tags
              ------------------------------------------------------------------ */}

          {recommendationTags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">

              {recommendationTags.map(
                (tag, index) => (
                  <span
                    key={`${tag}-${index}`}
                    className="text-[10px] font-black bg-purple-50 text-purple-700 border border-purple-200 px-2.5 py-0.5 rounded-md"
                  >
                    {tag}
                  </span>
                )
              )}

            </div>
          )}

          {/* ------------------------------------------------------------------
              AI Match Reasons
              ------------------------------------------------------------------ */}

          {matchReasons.length > 0 && (
            <div className="space-y-1 pt-1">

              <p className="text-[10px] font-black uppercase tracking-wide text-slate-400">
                Why this job matches
              </p>

              <div className="flex flex-wrap gap-1.5">

                {matchReasons.map(
                  (reason, index) => (
                    <span
                      key={`${reason}-${index}`}
                      className="text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-0.5 rounded-md"
                    >
                      {reason}
                    </span>
                  )
                )}

              </div>

            </div>
          )}

          {/* ------------------------------------------------------------------
              Skills
              ------------------------------------------------------------------ */}

          {skills.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-2 border-t border-slate-100">

              {skills.map(
                (skill, index) => (
                  <span
                    key={`${skill}-${index}`}
                    className="text-[11px] font-bold bg-slate-100 text-slate-700 px-2.5 py-1 rounded-lg"
                  >
                    {skill}
                  </span>
                )
              )}

            </div>
          )}

          {/* ------------------------------------------------------------------
              Error Notice
              ------------------------------------------------------------------ */}

          {error && (
            <div className="text-[10px] font-semibold text-rose-600 bg-rose-50 border border-rose-100 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

        </motion.div>
      </AnimatePresence>

      {/* ======================================================================
          ACTION BUTTONS
          ====================================================================== */}

      <div className="flex justify-center items-center gap-4 pt-6">

        {/* Skip */}

        <button
          onClick={() => handleSwipe('skip')}
          className="w-12 h-12 rounded-full bg-white border border-slate-200 text-rose-600 shadow-md flex items-center justify-center hover:bg-rose-50 cursor-pointer transition"
          title="Skip Job"
          aria-label="Skip Job"
        >
          <X className="w-6 h-6" />
        </button>

        {/* Undo */}

        <button
          onClick={handleUndo}
          disabled={swipeHistory.length === 0}
          className="w-10 h-10 rounded-full bg-white border border-slate-200 text-slate-600 shadow-md flex items-center justify-center disabled:opacity-40 hover:bg-slate-50 cursor-pointer transition"
          title="Undo Last Action"
          aria-label="Undo Last Action"
        >
          <RotateCcw className="w-4 h-4" />
        </button>

        {/* Save */}

        <button
          onClick={() => handleSwipe('save')}
          className="w-10 h-10 rounded-full bg-white border border-slate-200 text-purple-600 shadow-md flex items-center justify-center hover:bg-purple-50 cursor-pointer transition"
          title="Save Job"
          aria-label="Save Job"
        >
          <Bookmark className="w-4 h-4" />
        </button>

        {/* Apply / Like */}

        <button
          onClick={() => handleSwipe('like')}
          className="w-12 h-12 rounded-full bg-purple-600 text-white shadow-md flex items-center justify-center hover:bg-purple-700 cursor-pointer transition"
          title="Apply Now"
          aria-label="Apply Now"
        >
          <Heart className="w-6 h-6 fill-white" />
        </button>

      </div>

    </div>
  );
}